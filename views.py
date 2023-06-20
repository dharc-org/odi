from flask import Blueprint, render_template
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
import uuid

""" blueprint """
views = Blueprint(__name__, "views")

""" endpoint """
endpoint = "http://192.168.5.12:9999/blazegraph/sparql"
sparql = SPARQLWrapper(endpoint)

""" query """
""" raimondi """
# tarotCardsQuery = """
# PREFIX odi: <https://purl.org/ebr/odi#>
# PREFIX bacodi: <https://purl.org/ebr/odi/data/>
#
# select ?cardDeck ?cardName ?img
# where {
#     ?cardDeck a odi:DeckCard;
#         odi:hasName ?cardName ;
#         odi:hasImage ?img .
# }
# """

# linkedStoriesQuery = """
# PREFIX odi: <https://purl.org/ebr/odi#>
# PREFIX bacodi: <https://purl.org/ebr/odi/data/>
#
# select ?cardDeck ?story ?storyTitle
# where {
#     ?cardDeck a odi:DeckCard.
#     ?cardStory odi:specifies ?cardDeck.
#     ?story odi:hasCard ?cardStory ;
#         odi:hasTitle ?storyTitle .
# }
# """

storiesQuery = """
PREFIX odi: <https://purl.org/ebr/odi#>
PREFIX bacodi: <https://purl.org/ebr/odi/data/>

select distinct *
where {
    ?story a odi:Story ;
        odi:hasTitle|rdfs:label ?storyTitle.
}
"""

raimondiInfluencingquery = """
    PREFIX ecrm: <http://erlangen-crm.org/current/>
    PREFIX efrbroo: <http://erlangen-crm.org/efrbroo/>
    PREFIX prism: <http://prismstandard.org/namespaces/basic/2.0/>
    PREFIX pro: <http://purl.org/spar/pro/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?text ?title ?pubdate ?author
    WHERE {

        ?text a efrbroo:F24_Publication_Expression ;
            ecrm:P102_has_title ?title_uri ;
            prism:publicationDate ?pubdate .

        ?rit a pro:RoleInTime ;
            pro:relatesToEntity ?text .

        ?author_uri pro:holdsRoleInTime ?rit ;
                    rdfs:label ?author . FILTER (!regex(?author, "Giuseppe Raimondi","i")) .
        ?title_uri rdf:value ?title .
    }
"""

""" homepage """
@views.route("/")
def index():
    return render_template("index.html")

""" cards """
@views.route("/raimondi")
def raimondi():

    """ works by raimondi """
    """ convert data into JSON """
    sparql = SPARQLWrapper(endpoint)
    sparql.setTimeout(55)

    # sparql.setQuery(tarotCardsQuery)
    # sparql.setReturnFormat(JSON)
    # tarotCards =  sparql.query().convert()
    #
    # sparql.setQuery(linkedStoriesQuery)
    # sparql.setReturnFormat(JSON)
    # linkedStories = sparql.query().convert()

    sparql.setQuery(storiesQuery)
    sparql.setReturnFormat(JSON)
    storiesResults = sparql.query().convert()

    storiesData = []
    for res in storiesResults["results"]["bindings"]:
        temp = {}
        for k,v in res.items():
            temp.update({k:v["value"]})

        storiesData.append(temp)

    for res in storiesData:
        var = res['story']
        storyCardsQuery = """PREFIX odi: <https://purl.org/ebr/odi#> select distinct ?storyCard ?img ?position (group_concat(distinct ?text;separator="//") as ?texts) where { <""" + var + """> odi:hasCard ?storyCard. ?storyCard odi:hasPositionInTheText ?position; odi:hasTextualReference ?text; odi:specifies ?deckCard. OPTIONAL{?deckCard odi:hasImage ?img}} GROUP BY ?storyCard ?img ?position ORDER BY ASC (?position) """
        sparql.setQuery(storyCardsQuery)
        sparql.setReturnFormat(JSON)
        storyCardsResults = sparql.query().convert()

        storyCardsData = []
        for elem in storyCardsResults["results"]["bindings"]:
            temp2 = {}
            for k,v in elem.items():
                temp2.update({k:v["value"]})

            storyCardsData.append(temp2)

        res.update({'storyCards':storyCardsData})

        for st in storyCardsData:
            var1 = st['storyCard']
            representationQuery = """PREFIX odi: <https://purl.org/ebr/odi#> PREFIX bacodi: <https://purl.org/ebr/odi/data/> select distinct ?representation ?representationClassLabel ?meaningLabel ?predicateLabel where { <""" + var1 + """> odi:carriesRepresentation ?representation. ?representation a ?class; odi:hasMeaningOf ?meaning. OPTIONAL { ?protagonist odi:hasMeaningOf bacodi:protagonista. ?protagonist ?predicate ?representation. ?predicate rdfs:label ?predicateLabel. FILTER(lang(?predicateLabel) = 'it') FILTER(lang(?predicateLabel) != 'en')} ?meaning rdfs:label ?meaningLabel. ?class rdfs:label ?representationClassLabel. FILTER(lang(?representationClassLabel) = 'it') }"""
            sparql.setQuery(representationQuery)
            sparql.setReturnFormat(JSON)
            representationsResults = sparql.query().convert()


            representationsData = []
            for elem in representationsResults["results"]["bindings"]:
                temp2 = {}
                for k,v in elem.items():
                    temp2.update({k:v["value"]})

                representationsData.append(temp2)

            st.update({'representations':representationsData})




    # """ create a dictionary """
    # cardDeckContainer = []

    # """ Tarot deck cards """
    # for result in tarotCards["results"]["bindings"]:
    #     cardDeck = {}
    #     cardDeck.update({'cardDeck':result["cardDeck"]["value"] })
    #     cardDeck.update({'cardName':result["cardName"]["value"] })
    #     cardDeck.update({'img':result["img"]["value"] })
    #
    #     cardRelatedStories = []
    #     for story in linkedStories["results"]["bindings"]:
    #         cardRelatedStory = {}
    #         if str(result["cardDeck"]["value"]) == str(story["cardDeck"]["value"]):
    #             print(result["cardDeck"]["value"], story["cardDeck"]["value"])
    #             cardRelatedStory.update({'story':story["cardDeck"]["value"]})
    #             cardRelatedStory.update({'storyTitle':story["storyTitle"]["value"]})
    #             if cardRelatedStory != {}:
    #                 cardRelatedStories.append(cardRelatedStory)
    #     cardDeckContainer.append(cardDeck)

        #print(cardDeckContainer)



    # """ authors """
    # for result in raimondiResults["results"]["bindings"]:
    #     if result["author"]["value"] not in raimondiAuthors:
    #         raimondiAuthors.append(result["author"]["value"])
    #
    # """ works """
    # for author in raimondiAuthors:
    #     authorWorks = []
    #     for result in raimondiResults["results"]["bindings"]:
    #         uuidID = uuid.uuid4()
    #         id = str(uuidID)
    #         if author == result["author"]["value"]:
    #             if id + "---" + result["title"]["value"] + "___" + result["pubdate"]["value"] not in authorWorks:
    #                 authorWorks.append(id + "---" + result["title"]["value"] + "___" + result["pubdate"]["value"])
    #             raimondiWorksDict[author] = authorWorks
    #
    # """ works influencing raimondi """
    # """ convert data into JSON """
    # sparql.setQuery(raimondiInfluencingquery)
    # sparql.setReturnFormat(JSON)
    # inflRaimondiResults =  sparql.query().convert()
    #
    # """ create a dictionary """
    # inflRaimondiAuthors = []
    # inflRaimondiWorksDict = {}
    #
    # """ authors """
    # for result in inflRaimondiResults["results"]["bindings"]:
    #     if result["author"]["value"] not in inflRaimondiAuthors:
    #         inflRaimondiAuthors.append(result["author"]["value"])
    #
    # """ works """
    # for author in inflRaimondiAuthors:
    #     authorWorks = []
    #     for result in inflRaimondiResults["results"]["bindings"]:
    #         if author == result["author"]["value"]:
    #             if result["title"]["value"] + "___" + result["pubdate"]["value"] not in authorWorks:
    #                 authorWorks.append(result["title"]["value"] + "___" + result["pubdate"]["value"])
    #             inflRaimondiWorksDict[author] = authorWorks

    # return render_template("raimondi.html", raimondiAuthors = raimondiAuthors, raimondiWorksDict = raimondiWorksDict, inflRaimondiDict = inflRaimondiWorksDict)

    return render_template("raimondi.html", storiesData = storiesData)
