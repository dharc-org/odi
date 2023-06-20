from flask import Flask
from flask import Blueprint, render_template, send_from_directory, jsonify

from SPARQLWrapper import SPARQLWrapper, JSON
import uuid
from pyvis.network import Network
import requests
import json

#from views import views
#from routes import routes


app = Flask(__name__, static_folder="assets")

# endpoint
endpoint = "http://10.200.9.68:9999/blazegraph/sparql"
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

    # Set up the Pyvis network
    # net = Network()

    # Execute the SPARQL query
    sparql.setQuery(networkQuery)
    sparql.setReturnFormat('json')
    networkResults = sparql.query().convert()

    # Track the hierarchical level of each node
    #level_map = {}

    # Iterate over the query results and add nodes and edges to the network
    # for result in results['results']['bindings']:
    #     subject = result['cardLabel']['value']
    #     object = result['meaningLabel']['value']
    #     weight = result['n']['value']
    #     net.add_node(subject, color='red', shape='square')
    #     net.add_node(object)
    #     net.add_edge(subject, object, value=int(weight))
    #
    # # Assign the hierarchical level to the nodes
    # for node, level in level_map.items():
    #     net.nodes[node]['level'] = level
    #
    # # Save the network as an HTML file
    # net.save_graph("static/network.html")



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

if __name__ == "__main__":
    app.run(debug = True, port = 8000)
