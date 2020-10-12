import streamlit as st
import streamlit.components.v1 as comp
from streamlit_folium import folium_static
import folium
from SPARQLWrapper import SPARQLWrapper, JSON

## The queries that are not inside a function are outdated, and use dbpedia instead of our local ontology, will be changed soon
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery(
    """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT  * WHERE { 
    ?city a dbo:City;
    rdfs:label ?cityLabel
    FILTER(langMatches(lang(?cityLabel),"EN"))
    } LIMIT 100
"""
)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
locationList = [""]
for result in results["results"]["bindings"]:
    locationList.append(result["cityLabel"]["value"])

##if user selects to enter a scene, loads all scene from the selected movie
def findScene(movie):
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select ?scene ?lon ?lat where { 
        ?movie a ex:Movie.
        ?movie ex:hasPrimaryTitle ?title.
        ?movie ex:hasScene ?scene.
        ?scene ex:hasLongitude ?lon;
            ex:hasLatitude ?lat    
        FILTER(?title = '%s'@en) 
    } limit 100 
    """
        % (movie)
    )  ## paste the movie far into the string with %
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    sceneList, lonList, latList, lonLatList = [], [], [], []
    for result in results["results"]["bindings"]:
        sceneList.append(result["scene"]["value"])
        lonList.append(result["lon"]["value"])
        latList.append(result["lat"]["value"])
    i = 0
    while i < len(lonList):
        tempList = [latList[i], lonList[i]]
        lonLatList.append(tempList)
        i += 1
    sparql = SPARQLWrapper(
        "http://dbpedia.org/sparql"
    )  ##Creates a map with scenes as key and coordinates as value
    mappingCoordinates = dict(
        zip(sceneList, lonLatList)
    )  ## With lon as value[0] and lat as value[1]
    return sceneList, mappingCoordinates  ##


def findMovie():
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select ?title where { 
            ?movie a ex:Movie;
                ex:hasPrimaryTitle ?title  
    } limit 100 
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    movieList = []
    for result in results["results"]["bindings"]:
        movieList.append(result["title"]["value"])
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    return movieList

def findActor():
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select ?name where { 
            ?actor a ex:Actor;
                ex:hasFullName ?name  
    } limit 100 
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    actorList = []
    for result in results["results"]["bindings"]:
        actorList.append(result["name"]["value"])
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    return actorList

def findMovieActor(Actor): ## finds all movies with a specific actor in it
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select ?title where { 
            ?actor ex:hasFullName '%s'@en.
            ?movie a ex:Movie.
            ?movie ex:hasCharacter ?character.
            ?character ex:playedBy ?actor.
            ?movie ex:hasPrimaryTitle ?title 
    } limit 100 
    """ 
    % (Actor)
    )## when i say "movie ex:hasCharacter" it doesn't work. It infers actors in protege, but not in graphdb...
    print(Actor)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    movieActorList = []
    for result in results["results"]["bindings"]:
        movieActorList.append(result["title"]["value"])
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    return movieActorList


##########################################################################################################################

st.title("Movie location finder")
st.text("So that you can fall into the same vulcano as Gollum")



#movieExpander = st.beta_expander("Movies", expanded=False)
#actorExpander = st.beta_expander("Actors", expanded=False)
#locationExpander = st.beta_expander("Locations", expanded=False)
## I'm trying to add logic to the expanders (open 1, other 2 close), but can't find any documentation about it yet.

## User selects his favorite movie/actor/whatever
with st.beta_expander("Movies"):
    #if searchMode == "Movies":

    movieList = findMovie()
    inputMovie = st.selectbox("Select your favorite movie", movieList, key='1')
    if inputMovie != "":  ## If movie is selected, render the scene selectbox
        sceneList, mappingCoordinates = findScene(inputMovie)
        inputScene = st.selectbox("Select your scene", sceneList, key='2')
        if (
            inputScene != ""
        ):  ##if scene is selected, render the button to call the folium map
            for key, value in mappingCoordinates.items():
                if key == inputScene:
                    coordinates = [value[0], value[1]]
            m2 = folium.Map(location=coordinates, zoom_start=16)
            folium.Marker(coordinates, popup="test", tooltip="test").add_to(m2)
            if st.button("test!", key='moviesButton'):
                folium_static(m2)


with st.beta_expander("Actors"):
#if searchMode == "Actors":
    actorList = findActor()
    inputActor = st.selectbox("Select your favorite Actor", actorList, key='3')
    if inputActor != '':
        movieActorList = findMovieActor(inputActor)
        inputMovie2 = st.selectbox('select a movie', movieActorList, key='4')
        if inputMovie2 != '':
            sceneList, mappingCoordinates = findScene(inputMovie2)
            inputScene = st.selectbox("Select your scene", sceneList, key='5')
            if (
                inputScene != ""
            ):  ##if scene is selected, render the button to call the folium map
                for key, value in mappingCoordinates.items():
                    if key == inputScene:
                        coordinates = [value[0], value[1]]
                m2 = folium.Map(location=coordinates, zoom_start=16)
                folium.Marker(coordinates, popup="test", tooltip="test").add_to(m2)
                if st.button("test!", key='actorButton'):
                    folium_static(m2)



## searchmode locations is still kind of outdated and doesn't use our own graphdb endpoint
with st.beta_expander("Locations"):
#if searchMode == "Locations":
    inputLocation = st.selectbox("Select your location", locationList)
## These coordinates should come from querying our own ontology
## With the query being based on the user's selection ofcourse
tempCoordinates = [[37.8770, -4.7784], [37.8758, -4.7790]]
tooltip = ["This should be a bridge", "this should be a castle"]
popup = ["it's the bridge from GOT!", "it's a random castle!"]
m = folium.Map(location=tempCoordinates[0], zoom_start=16)

## Add all the coordinates, tooltips etc to the map
i = 0
while i < len(tempCoordinates):
    folium.Marker(tempCoordinates[i], popup=popup[i], tooltip=tooltip[i]).add_to(m)
    i += 1

## Load the map when the button is clicked
if st.button("find Location!"):
    folium_static(m)
