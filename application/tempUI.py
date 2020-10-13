import streamlit as st
import streamlit.components.v1 as comp
from streamlit_folium import folium_static
import folium
from SPARQLWrapper import SPARQLWrapper, JSON

st.beta_set_page_config(layout="wide")  ## comment this out to disable widescreen

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


def findMovieActor(Actor):  ## finds all movies with a specific actor in it
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
    )  ## when i say "movie ex:hasCharacter" it doesn't work. It infers actors in protege, but not in graphdb...
    print(Actor)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    movieActorList = []
    for result in results["results"]["bindings"]:
        movieActorList.append(result["title"]["value"])
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    return movieActorList


##########################################################################################################################
col1, col2, col3, col4, col5 = st.beta_columns(5)
with col2:
    st.title("Movie location finder")
    st.text("So that you can fall into the same vulcano as Gollum")


## User selects his favorite movie/actor/whatever
with col2:
    with st.beta_expander("Movies"):
        movieList = findMovie()
        inputMovie = st.selectbox("Select your favorite movie", movieList, key="1")
        if inputMovie != "":  ## If movie is selected, render the scene selectbox
            sceneList, mappingCoordinates = findScene(inputMovie)
            inputScene = st.selectbox("Select your scene", sceneList, key="2")
            if (
                inputScene != ""
            ):  ##if scene is selected, render the button to call the folium map
                for key, value in mappingCoordinates.items():
                    if key == inputScene:
                        coordinates = [value[0], value[1]]
                m2 = folium.Map(location=coordinates, zoom_start=16)
                folium.Marker(coordinates, popup="test", tooltip="test").add_to(m2)
                if st.button("test!", key="moviesButton"):
                    with col4:
                        folium_static(m2)

with col2:
    with st.beta_expander("Actors"):
        actorList = findActor()
        inputActor = st.selectbox("Select your favorite Actor", actorList, key="3")
        if inputActor != "":
            movieActorList = findMovieActor(inputActor)
            inputMovie2 = st.selectbox("select a movie", movieActorList, key="4")
            if inputMovie2 != "":
                sceneList, mappingCoordinates = findScene(inputMovie2)
                inputScene = st.selectbox("Select your scene", sceneList, key="5")
                if (
                    inputScene != ""
                ):  ##if scene is selected, render the button to call the folium map
                    for key, value in mappingCoordinates.items():
                        if key == inputScene:
                            coordinates = [value[0], value[1]]
                    m2 = folium.Map(location=coordinates, zoom_start=16)
                    folium.Marker(coordinates, popup="test", tooltip="test").add_to(m2)
                    if st.button("test!", key="actorButton"):
                        with col4:
                            folium_static(m2)


## searchmode locations is still kind of outdated and doesn't use our own graphdb endpoint
with col2:
    with st.beta_expander("Locations"):
        st.write("Work in progress")
