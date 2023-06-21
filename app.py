from flask import Flask
from flask import Blueprint, render_template, send_from_directory, request,  url_for, redirect, session, Response, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import parse_qs , quote
import uuid
import requests
import json

#from views import views
#from routes import routes


app = Flask(__name__, static_folder="assets")

# endpoint
endpoint = "http://localhost:9999/blazegraph/sparql"
sparql = SPARQLWrapper(endpoint)
sparql.setTimeout(55)

# Define the routes using the example_routes blueprint
@app.route('/')
def home():

    #net = Network(directed=True, layout='hierarchical')

    networkQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?cardLabel ?meaningLabel (COUNT(?meaning) as ?n)
    where {
      ?card a odi:DeckCard .
      ?card odi:hasName ?cardLabel.
      ?story odi:hasCard ?storyCard.
      ?storyCard odi:specifies ?card.
      ?storyCard odi:carriesRepresentation ?representation.
      ?representation odi:hasMeaningOf ?meaning.
      ?meaning rdfs:label ?meaningLabel.
      }
      GROUP BY ?cardLabel ?meaningLabel
      """

    # Execute the SPARQL query
    sparql.setQuery(networkQuery)
    sparql.setReturnFormat('json')
    networkResults = sparql.query().convert()

    # retrieve all cards
    cardsQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?card ?cardName ?typology ?typologyLabel ?suit ?suitLabel
    where {
      ?card a odi:DeckCard ;
              odi:hasName ?cardName ;
              odi:hasTypology ?typology.
      ?typology rdfs:label ?typologyLabel.

      OPTIONAL {?card odi:hasSuit ?suit. ?suit rdfs:label ?suitLabel.}
    }
    """

    sparql.setQuery(cardsQuery)
    sparql.setReturnFormat(JSON)
    cardsResults = sparql.query().convert()

    suitList, typologyList = [],[]
    for res in cardsResults['results']['bindings']:
        if 'suitLabel' in res:
            suitList.append(res['suitLabel']['value'])
        typologyList.append(res['typologyLabel']['value'])

    suitList = list(set(suitList))
    typologyList = list(set(typologyList))

    # retrieve all stories
    storiesQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?story ?storyTitle ?storyName
    where {
         ?story a odi:Story.
         ?story rdfs:label ?storyTitle.
         OPTIONAL {?story odi:hasTitle ?storyName}
    }
    """
    sparql.setQuery(storiesQuery)
    sparql.setReturnFormat(JSON)
    storiesResults = sparql.query().convert()

    # retrieve all meanings
    meaningsQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?meaning ?meaningLabel ?classLabel (COUNT(?meaning) as ?nMeanings)
    where {
      ?meaning a odi:Meaning ;
                 rdfs:label ?meaningLabel ;
                 ^odi:hasMeaningOf ?representation.
      ?representation a ?class.
      ?class rdfs:label ?classLabel.
      FILTER (lang(?classLabel) = 'it')
    }

    GROUP BY ?meaning ?meaningLabel ?classLabel ORDER BY DESC (?nMeanings) """

    sparql.setQuery(meaningsQuery)
    sparql.setReturnFormat(JSON)
    meaningsResults = sparql.query().convert()

    classList = []
    for res in meaningsResults['results']['bindings']:
        classList.append(res['classLabel']['value'])

    classList = list(set(classList))

    return render_template('index.html',  cardsResults = cardsResults, storiesResults = storiesResults, suitList = suitList, typologyList = typologyList, meaningsResults = meaningsResults, classList = classList, networkResults = networkResults)

# SET THE ENDPOINT



# KG BROWSING
@app.route('/storie/<storyID>')
def story(storyID):

    storyQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?storyTitle ?storyCard ?deckCard ?deckCardLabel ?position ?storyName (group_concat(distinct ?text;separator="//") as ?texts)
    where {
         <https://purl.org/ebr/odi/data/""" + storyID + """> rdfs:label ?storyTitle;
            odi:hasCard ?storyCard.
        ?storyCard odi:hasPositionInTheText ?position ;
            odi:specifies ?deckCard.
        ?deckCard odi:hasName ?deckCardLabel.

        OPTIONAL {<https://purl.org/ebr/odi/data/""" + storyID + """> odi:hasTitle ?storyName}
        OPTIONAL {?storyCard odi:hasTextualReference ?text}

    }
    GROUP BY ?storyTitle ?storyCard ?deckCard ?deckCardLabel ?position ?storyName ORDER BY ASC (?position)
    """

    sparql.setQuery(storyQuery)
    sparql.setReturnFormat(JSON)
    storyResults = sparql.query().convert()

    storyRepresentationQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?storyCard ?meaning ?meaningLabel
    where {
         <https://purl.org/ebr/odi/data/""" + storyID + """> odi:hasCard ?storyCard.
        ?storyCard odi:carriesRepresentation ?representation.
        ?representation odi:hasMeaningOf ?meaning.
        ?meaning rdfs:label ?meaningLabel.
    }
    """

    sparql.setQuery(storyRepresentationQuery)
    sparql.setReturnFormat(JSON)
    storyRepresentationResult = sparql.query().convert()

    storyTitle = storyResults["results"]["bindings"][0]["storyTitle"]["value"]

    try:
        storyName = storyResults["results"]["bindings"][0]["storyName"]["value"]
    except:
        storyName = ''


    #net = Network()

    storyRelationsQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select ?representation ?reprLabel ?relation ?relLabel ?representation2 ?reprLabel2 ?classLabel ?classLabel2
    where {

        <https://purl.org/ebr/odi/data/""" + storyID + """> odi:hasCard ?card,?card2.

       ?card odi:carriesRepresentation ?representation.
       ?card2 odi:carriesRepresentation ?representation2.

       ?representation a ?class.
       ?class rdfs:label ?classLabel.
       ?class rdfs:subClassOf odi:Representation.
       ?representation2 a ?class2.
       ?class2 rdfs:subClassOf odi:Representation.
       ?class2 rdfs:label ?classLabel2.

       ?representation odi:hasMeaningOf ?meaning.
       ?meaning rdfs:label ?reprLabel.
       ?representation2 odi:hasMeaningOf ?meaning2.
       ?meaning2 rdfs:label ?reprLabel2.

      	?representation ?relation ?representation2.
      	?relation rdfs:label ?relLabel


      FILTER (lang(?relLabel) = 'it')
      FILTER (lang(?classLabel) = 'it')
      FILTER (lang(?classLabel2) = 'it')
      FILTER (?relation != odi:hasMeaningOf)
      FILTER (?relation != rdf:type)

    }"""

    sparql.setQuery(storyRelationsQuery)
    sparql.setReturnFormat(JSON)
    storyRelationsResult = sparql.query().convert()

    # Track the hierarchical level of each node
    # level_map = {}
    #
    # # Iterate over the query results and add nodes and edges to the network
    # for result in storyRelationsResult['results']['bindings']:
    #     subject = result['reprLabel']['value']
    #     object = result['reprLabel2']['value']
    #     net.add_node(subject, color='red', shape='square')
    #     net.add_node(object)
    #     net.add_edge(subject, object, label=result['relLabel']['value'], lenght=200)
    #
    #     # Serialize the network data to JSON
    # network_data = str(net.get_network_data())

    return render_template('storyTemplate.html',  storyResults = storyResults, storyRepresentationResult = storyRepresentationResult, storyTitle = storyTitle, storyName = storyName, storyRelationsResult=storyRelationsResult)

@app.route('/carte/<cardID>')
def card(cardID):

    cardDescriptionQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?pLabel ?object ?objectLabel
    where {
      <https://purl.org/ebr/odi/data/""" + cardID + """> ?p ?object.
      ?p rdfs:label ?pLabel.
      OPTIONAL {?object rdfs:label ?objectLabel}
      FILTER (lang(?pLabel) = 'it')
    }
    """

    sparql.setQuery(cardDescriptionQuery)
    sparql.setReturnFormat(JSON)
    cardDescriptionData = sparql.query().convert()

    cardQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?cardName ?story ?storyTitle ?storyName ?position (group_concat(distinct ?text;separator="//") as ?texts)
    where {
      <https://purl.org/ebr/odi/data/""" + cardID + """> odi:hasName ?cardName ;
           ^odi:specifies ?storyCard.
      ?storyCard ^odi:hasCard ?story;
        odi:hasPositionInTheText ?position.
      ?story rdfs:label ?storyTitle.
      OPTIONAL {?story odi:hasTitle ?storyName}
      OPTIONAL {?storyCard odi:hasTextualReference ?text}
    }
    GROUP BY  ?cardName ?story ?storyTitle ?storyName ?position ORDER BY ASC (?position)
    """

    sparql.setQuery(cardQuery)
    sparql.setReturnFormat(JSON)
    cardResults = sparql.query().convert()

    cardName = cardResults["results"]["bindings"][0]["cardName"]["value"]

    representationsCardQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?cardName ?story ?representation ?meaning ?meaningLabel
    where {
      <https://purl.org/ebr/odi/data/""" + cardID + """> ^odi:specifies ?storyCard.
      ?storyCard odi:carriesRepresentation ?representation;
        odi:hasTextualReference ?text;
        odi:hasPositionInTheText ?position;
        ^odi:hasCard ?story.
        ?representation odi:hasMeaningOf ?meaning.
        ?meaning rdfs:label ?meaningLabel.

    }
    """

    sparql.setQuery(representationsCardQuery)
    sparql.setReturnFormat(JSON)
    representationCardData = sparql.query().convert()

    #return f"Welcome, {storiesResults}!"
    return render_template('cardTemplate.html',  cardResults = cardResults, cardName = cardName, representationCardData = representationCardData, cardDescriptionData = cardDescriptionData)

@app.route('/semi/<suitID>')
def suit(suitID):

    suitQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?suitLabel
    where {
      <https://purl.org/ebr/odi/data/""" + suitID + """> rdfs:label ?suitLabel
    }
    """

    sparql.setQuery(suitQuery)
    sparql.setReturnFormat(JSON)
    suitResults = sparql.query().convert()

    suitLabel = suitResults['results']['bindings'][0]['suitLabel']

    suitCardsQuery = """
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?cardName ?deckCard ?story ?storyTitle ?storyName ?meaning ?meaningLabel ?position (group_concat(distinct ?text;separator="//") as ?texts)
    where {
      <https://purl.org/ebr/odi/data/""" + suitID + """> ^odi:hasSuit ?deckCard.
        ?deckCard ^odi:specifies ?storyCard;
            odi:hasName ?cardName.
      ?storyCard odi:carriesRepresentation ?representation;
                  odi:hasPositionInTheText ?position;
                 ^odi:hasCard ?story.
      ?story rdfs:label ?storyTitle.
      ?representation odi:hasMeaningOf ?meaning.
      ?meaning rdfs:label ?meaningLabel
    OPTIONAL {?story odi:hasTitle ?storyName}
    OPTIONAL {?storyCard odi:hasTextualReference ?text}
    }
    GROUP BY ?cardName ?deckCard ?story ?storyTitle ?storyName ?meaning ?meaningLabel ?position ORDER BY ASC (?position)
    """

    sparql.setQuery(suitCardsQuery)
    sparql.setReturnFormat(JSON)
    suitMeaningsResults = sparql.query().convert()

    print(suitMeaningsResults)

    return render_template('suitTemplate.html',  suitLabel = suitLabel, suitMeaningsResults = suitMeaningsResults)


@app.route('/significati/<meaningID>')
def meaning(meaningID):

    meaningDescriptionQuery = """
    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?suitLabel
    where {
      <https://purl.org/ebr/odi/data/""" + meaningID + """> rdfs:label ?suitLabel
    }
    """

    sparql.setQuery(meaningDescriptionQuery)
    sparql.setReturnFormat(JSON)
    meaningDescriptionData = sparql.query().convert()

    meaningLabel = meaningDescriptionData['results']['bindings'][0]['suitLabel']

    meaningQuery = """

    PREFIX odi: <https://purl.org/ebr/odi#>
    PREFIX bacodi: <https://purl.org/ebr/odi/data/>

    select distinct ?deckCard ?cardName ?story ?storyTitle ?storyName ?position (group_concat(distinct ?text;separator="//") as ?texts)
    where {
      <https://purl.org/ebr/odi/data/""" + meaningID + """> ^odi:hasMeaningOf ?representation .
      ?storyCard odi:carriesRepresentation ?representation.
      ?storyCard odi:specifies ?deckCard;
              odi:hasPositionInTheText ?position.
      ?story odi:hasCard ?storyCard;
             rdfs:label ?storyTitle.
      ?deckCard odi:hasName ?cardName.
      OPTIONAL {?story odi:hasTitle ?storyName}
      OPTIONAL {?storyCard odi:hasTextualReference ?text}
    }
    GROUP BY ?deckCard ?cardName ?story ?storyTitle ?storyName ?position ORDER BY ASC (?position)
    """

    sparql.setQuery(meaningQuery)
    sparql.setReturnFormat(JSON)
    meaningData = sparql.query().convert()


    return render_template('meaningTemplate.html',  meaningLabel = meaningLabel, meaningData = meaningData)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# ENDPOINT

@app.route("/sparql", methods=['GET', 'POST'])
def sparql_gui(active=None):
	""" SPARQL endpoint GUI and request handler

	Parameters
	----------
	active: str
		Query string or None
		If None, renders the GUI, else parse the query (__run_query_string)
		If the query string includes an update, return error, else sends
		the query to the endpoint (__contact_tp)
	"""
	if request.method == 'GET':
		content_type = request.content_type
		q = request.args.get("query")
		return __run_query_string(active, q, content_type)
	else:
		content_type = request.content_type
		cur_data = request.get_data()
		if "application/x-www-form-urlencoded" in content_type:
			return __run_query_string(active, cur_data, True, content_type)
		elif "application/sparql-query" in content_type:
			return __contact_tp(cur_data, True, content_type)
		else:
			return render_template('sparql.html',active=active)

def __run_query_string(active, query_string,
	is_post=False, content_type="application/x-www-form-urlencoded"):
	try:
		query_str_decoded = query_string.decode('utf-8')
	except Exception as e:
		query_str_decoded = query_string
	parsed_query = parse_qs(query_str_decoded)

	if query_str_decoded is None or query_str_decoded.strip() == "":
		return render_template('sparql.html',active=active)

	if re.search("updates?", query_str_decoded, re.IGNORECASE) is None:
		if "query" in parsed_query or "select" in query_str_decoded.lower():
			return __contact_tp(query_string, is_post, content_type)
		else:
			return render_template('sparql.html',active=active)
	else:
		return render_template('403.html'), 403

def __contact_tp(data, is_post, content_type):
	accept = request.args.get('HTTP_ACCEPT')
	if accept is None or accept == "*/*" or accept == "":
		accept = "application/sparql-results+json"

	data = data if isinstance(data,bytes) else quote(data)
	if is_post:
		req = requests.post(endpoint, data=data,
							headers={'content-type': content_type, "accept": accept})
	else:
		req = requests.get("%s?query=%s" % (endpoint,data ),
						   headers={'content-type': content_type, "accept": accept})

	if req.status_code == 200:
		response = Response()
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Credentials'] = 'true'
		response.headers['Content-Type'] = req.headers["content-type"]
		response.mimetype = "application/sparql-results+json"
		return req.json()
	else:
		return render_template('error.html',
			status_code=str(req.status_code),
			headers={"Content-Type": request.content_type},
			text=req.text)

@app.route('/error')
def error(status_code, headers, text):
	return render_template('error.html',status_code, headers, text)

@app.errorhandler(403)
def page_not_found(e):
	# note that we set the 403 status explicitly
	return render_template('403.html'), 403

# prova
# @app.route('/pipo', methods=['GET', 'POST'])
# def pipo():
#     #query = request.form.get('query')
#     data = request.get_json()
#     query = data['string']
#     sparql_endpoint = "http://10.200.13.4:9999/blazegraph/sparql"
#     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#     payload = {'query': query}
#     response = requests.post(sparql_endpoint, headers=headers, data=payload)
#     # Process the response as needed
#     print(response.text)
#     return response.text


@app.route('/process_query', methods=['POST'])
def process_query():
    data = request.get_json()
    query = data['string']

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    query_result = sparql.query().convert()

    print(query_result)

    if isinstance(query_result, str):
        return query_result
    else:
        # If the query result is a JSON response, return it as JSON
        return jsonify(query_result)

if __name__ == "__main__":
    app.run(debug = True, port = 8000)
