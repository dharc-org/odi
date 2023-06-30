from flask import Flask
from flask import Blueprint, render_template, send_from_directory, request,  url_for, redirect, session, Response, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import parse_qs , quote
import uuid
import requests
import json

app = Flask(__name__, static_folder="assets")

# endpoint
endpoint = "http://localhost:9999/blazegraph/sparql"
sparql = SPARQLWrapper(endpoint)
sparql.setTimeout(55)

# Define the routes using the example_routes blueprint
@app.route('/')
def home():
    return render_template('index.html')

# Define the routes using the example_routes blueprint
@app.route('/indici/')
def indexes():

    #net = Network(directed=True, layout='hierarchical')

    networkQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

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
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?card ?cardName ?typology ?typologyLabel ?suit ?suitLabel (COUNT(?storyCard) as ?nCards)
    where {
      ?card a odi:DeckCard ;
              odi:hasName ?cardName ;
              odi:hasTypology ?typology.
      ?typology rdfs:label ?typologyLabel.
      OPTIONAL {?storyCard odi:specifies ?card. ?story odi:hasCard ?storyCard.}

      OPTIONAL {?card odi:hasSuit ?suit. ?suit rdfs:label ?suitLabel.}
    }

    GROUP BY ?card ?cardName ?typology ?typologyLabel ?suit ?suitLabel ORDER BY DESC (?nCards)
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
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?story ?storyTitle ?storyName ?position
    where {
         ?story a odi:Story.
         ?story rdfs:label ?storyTitle.
         ?story odi:hasPositionInTheBook ?position.
         OPTIONAL {?story odi:hasTitle ?storyName}

    }
    GROUP BY ?story ?storyTitle ?storyName ?position ORDER BY ASC (?position)
    """
    sparql.setQuery(storiesQuery)
    sparql.setReturnFormat(JSON)
    storiesResults = sparql.query().convert()

    # retrieve all meanings
    meaningsQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

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

    return render_template('indexes.html',  cardsResults = cardsResults, storiesResults = storiesResults, suitList = suitList, typologyList = typologyList, meaningsResults = meaningsResults, classList = classList, networkResults = networkResults)

# SET THE ENDPOINT

# KG BROWSING
@app.route('/storie/<storyID>')
def story(storyID):

    storyQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?storyTitle ?storyCard ?deckCard ?deckCardLabel ?position ?storyName ?comment (group_concat(distinct ?text;separator="//") as ?texts)
    where {
         <https://w3id.org/odi/data/storie/""" + storyID + """> rdfs:label ?storyTitle;
            odi:hasCard ?storyCard.
        ?storyCard odi:hasPositionInTheText ?position ;
            odi:specifies ?deckCard.
        ?deckCard odi:hasName ?deckCardLabel.

        OPTIONAL {<https://w3id.org/odi/data/storie/""" + storyID + """> odi:hasTitle ?storyName}
        OPTIONAL {?storyCard odi:hasTextualReference ?text}
        OPTIONAL {<https://w3id.org/odi/data/storie/""" + storyID + """> rdfs:comment ?comment}

    }
    GROUP BY ?storyTitle ?storyCard ?deckCard ?deckCardLabel ?position ?storyName ?comment ORDER BY ASC (?position)
    """

    sparql.setQuery(storyQuery)
    sparql.setReturnFormat(JSON)
    storyResults = sparql.query().convert()

    storyRepresentationQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?storyCard ?meaning ?meaningLabel
    where {
         <https://w3id.org/odi/data/storie/""" + storyID + """> odi:hasCard ?storyCard.
        ?storyCard odi:carriesRepresentation ?representation.
        ?representation odi:hasMeaningOf ?meaning.
        ?meaning rdfs:label ?meaningLabel.
    }
    """

    sparql.setQuery(storyRepresentationQuery)
    sparql.setReturnFormat(JSON)
    storyRepresentationResult = sparql.query().convert()

    storyTitle = storyResults["results"]["bindings"][0]["storyTitle"]["value"]
    storyDescription = storyResults["results"]["bindings"][0]["comment"]["value"]

    try:
        storyName = storyResults["results"]["bindings"][0]["storyName"]["value"]
    except:
        storyName = ''


    #net = Network()

    storyRelationsQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select ?representation ?reprLabel ?relation ?relLabel ?representation2 ?reprLabel2 ?classLabel ?classLabel2
    where {

        <https://w3id.org/odi/data/storie/""" + storyID + """> odi:hasCard ?card,?card2.

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

    return render_template('storyTemplate.html',  storyResults = storyResults, storyRepresentationResult = storyRepresentationResult, storyTitle = storyTitle, storyDescription = storyDescription, storyName = storyName, storyRelationsResult=storyRelationsResult)

@app.route('/carte/<cardID>')
def card(cardID):

    cardDescriptionQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?pLabel ?object ?objectLabel
    where {
      <https://w3id.org/odi/data/carte/""" + cardID + """> ?p ?object.
      ?p rdfs:label ?pLabel.
      OPTIONAL {?object rdfs:label ?objectLabel}
      FILTER (lang(?pLabel) = 'it')
    }
    """

    sparql.setQuery(cardDescriptionQuery)
    sparql.setReturnFormat(JSON)
    cardDescriptionData = sparql.query().convert()

    cardQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?cardName ?story ?storyTitle ?storyName ?position (group_concat(distinct ?text;separator="//") as ?texts)
    where {
      <https://w3id.org/odi/data/carte/""" + cardID + """> odi:hasName ?cardName ;
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
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?cardName ?story ?representation ?meaning ?meaningLabel
    where {
      <https://w3id.org/odi/data/carte/""" + cardID + """> ^odi:specifies ?storyCard.
      ?storyCard odi:carriesRepresentation ?representation;
        odi:hasPositionInTheText ?position;
        ^odi:hasCard ?story.
        ?representation odi:hasMeaningOf ?meaning.
        ?meaning rdfs:label ?meaningLabel.

    OPTIONAL {?storyCard odi:hasTextualReference ?text;}

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
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?suitLabel ?comment
    where {
      <https://w3id.org/odi/data/semi/""" + suitID + """> rdfs:label ?suitLabel.
      OPTIONAL {<https://w3id.org/odi/data/semi/""" + suitID + """> rdfs:comment ?comment}
    }
    """

    sparql.setQuery(suitQuery)
    sparql.setReturnFormat(JSON)
    suitResults = sparql.query().convert()

    suitLabel = suitResults['results']['bindings'][0]['suitLabel']
    suitDescription = suitResults['results']['bindings'][0]['comment']

    suitCardsQuery = """
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?cardName ?deckCard ?story ?storyTitle ?storyName ?meaning ?meaningLabel ?position (group_concat(distinct ?text;separator="//") as ?texts)
    where {
      <https://w3id.org/odi/data/semi/""" + suitID + """> ^odi:hasSuit ?deckCard.
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

    return render_template('suitTemplate.html',  suitLabel = suitLabel, suitDescription = suitDescription, suitMeaningsResults = suitMeaningsResults)

@app.route('/tipologia/<typologyID>')
def typology(typologyID):

    typologyQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?typologyLabel ?comment
    where {
      <https://w3id.org/odi/data/tipologia/""" + typologyID + """> rdfs:label ?typologyLabel.
      OPTIONAL {<https://w3id.org/odi/data/tipologia/""" + typologyID + """> rdfs:comment ?comment}
    }
    """

    sparql.setQuery(typologyQuery)
    sparql.setReturnFormat(JSON)
    typologyResults = sparql.query().convert()

    typologyLabel = typologyResults['results']['bindings'][0]['typologyLabel']
    typologyDescription = typologyResults['results']['bindings'][0]['comment']


    typologyCardsQuery = """
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?cardName ?deckCard ?story ?storyTitle ?storyName ?meaning ?meaningLabel ?position (group_concat(distinct ?text;separator="//") as ?texts)
    where {
      <https://w3id.org/odi/data/tipologia/""" + typologyID + """> ^odi:hasTypology ?deckCard.
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

    sparql.setQuery(typologyCardsQuery)
    sparql.setReturnFormat(JSON)
    typologyMeaningsResults = sparql.query().convert()

    return render_template('typologyTemplate.html',  typologyLabel = typologyLabel, typologyDescription = typologyDescription, typologyMeaningsResults = typologyMeaningsResults)


@app.route('/significati/<meaningID>')
def meaning(meaningID):

    meaningDescriptionQuery = """
    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?suitLabel
    where {
      <https://w3id.org/odi/data/significati/""" + meaningID + """> rdfs:label ?suitLabel
    }
    """

    sparql.setQuery(meaningDescriptionQuery)
    sparql.setReturnFormat(JSON)
    meaningDescriptionData = sparql.query().convert()

    meaningLabel = meaningDescriptionData['results']['bindings'][0]['suitLabel']

    meaningQuery = """

    PREFIX odi: <https://w3id.org/odi/>
    PREFIX bacodi: <https://w3id.org/odi/data/>

    select distinct ?deckCard ?cardName ?story ?storyTitle ?storyName ?position (group_concat(distinct ?text;separator="//") as ?texts)
    where {
      <https://w3id.org/odi/data/significati/""" + meaningID + """> ^odi:hasMeaningOf ?representation .
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

@app.route('/data/visualisation/<path:path>')
def send_static(path):
    return send_from_directory('visualisation', path)

@app.route('/contatti')
def contacts():
    return render_template('contacts.html')

# ENDPOINT

@app.route("/sparql", methods=['GET', 'POST'])
def sparql_gui(active=None):
	return render_template('sparql.html',active=active)

@app.errorhandler(403)
def page_not_found(e):
	# note that we set the 403 status explicitly
	return render_template('403.html'), 403

@app.errorhandler(500)
def server_error(e):
	# note that we set the 403 status explicitly
	return render_template('500.html'), 500


@app.route('/process_query', methods=['POST'])
def process_query():
    data = request.get_json()
    query = data['string']

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    query_result = sparql.query().convert()

    if 'select' in query.lower() or 'construct' in query.lower():
        if isinstance(query_result, str):
            return render_template('500.html'), 500
        else:
            # If the query result is a JSON response, return it as JSON
            return jsonify(query_result)
    else:
        return render_template('403.html'), 403

if __name__ == "__main__":
    app.run(debug = True, port = 8000)
