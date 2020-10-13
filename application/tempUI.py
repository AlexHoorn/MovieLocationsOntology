import streamlit as st
import streamlit.components.v1 as comp
from streamlit_folium import folium_static
import folium
from SPARQLWrapper import SPARQLWrapper, JSON

st.beta_set_page_config(layout="wide")  ## comment this out to disable widescreen

##if user selects to enter a scene, loads all scene from the selected movie
def findScene(show):
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT ?sceneName ?lon ?lat where { 
        ?show a ex:Show.
        ?show ex:hasPrimaryTitle ?title.
        ?show ex:hasScene ?scene.
        ?scene rdfs:label ?sceneName.
    	?scene ex:hasLocation ?location.
    	    ?location ex:hasLongitude ?lon;
            ex:hasLatitude ?lat   
        FILTER(?title = '%s') 
    } 
    """
        % (show)
    )  ## paste the show far into the string with %
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    sceneList, lonList, latList, lonLatList = [], [], [], []
    for result in results["results"]["bindings"]:
        sceneList.append(result["sceneName"]["value"])
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


def findShow():
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select ?title where { 
            ?show a ex:Show;
                ex:hasPrimaryTitle ?title  
    } 
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showList = []
    for result in results["results"]["bindings"]:
        showList.append(result["title"]["value"])
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    return showList


def findActor():
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select ?name ?actor where { 
            ?character ex:playedBy ?actor.
            ?actor ex:hasFullName ?name
    }
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    actorNameList = []
    actorList = [] ## contains the actor code for our ontology
    for result in results["results"]["bindings"]:
        actorNameList.append(result["name"]["value"])
        actorList.append(result["actor"]["value"])
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    actorNameList2 = []
    for actor in actorNameList: ## remove strings out of names. Dwayne 'The Rock" Johnson ==> Dwayne The Rock Johnson
        actor = actor.replace("'", "") 
        actorNameList2.append(actor)
    return actorNameList2


def findShowActor(Actor):  ## finds all movies with a specific actor in it
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select ?title where { 
            ?actor ex:hasFullName '%s'.
            ?show a ex:Show.
            ?show ex:hasCharacter ?character.
            ?character ex:playedBy ?actor.
            ?show ex:hasPrimaryTitle ?title 
    } 
    """
        % (Actor)
    )  ## when i say "movie ex:hasCharacter" it doesn't work. It infers actors in protege, but not in graphdb...
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showActorList = []
    for result in results["results"]["bindings"]:
        showActorList.append(result["title"]["value"])
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    return showActorList


##########################################################################################################################
col1, col2, col3, col4, col5 = st.beta_columns(5)
with col2:
    st.title("Movie location finder")
    st.text("So that you can fall into the same vulcano as Gollum")


## User selects his favorite movie/actor/whatever
with col2:
    with st.beta_expander("Shows"):
        showList = findShow()
        inputShow = st.selectbox("Select your favorite show", showList, key="1")
        if inputShow != "":  ## If movie is selected, render the scene selectbox
            sceneList, mappingCoordinates = findScene(inputShow)
            inputScene = st.selectbox("Select your scene", sceneList, key="2")
            if (
                inputScene != ""
            ):  ##if scene is selected, render the button to call the folium map
                for key, value in mappingCoordinates.items():
                    if key == inputScene:
                        coordinates = [value[0], value[1]]
                m2 = folium.Map(location=coordinates, zoom_start=16)
                folium.Marker(coordinates, popup="test", tooltip="test").add_to(m2)
                if st.button("test!", key="showButton"):
                    with col4:
                        folium_static(m2)

with col2:
    with st.beta_expander("Actors"):
        actorList = findActor()
        inputActor = st.selectbox("Select your favorite Actor", actorList, key="3")
        if inputActor != "":
            showActorList = findShowActor(inputActor)
            inputShow2 = st.selectbox("select a show", showActorList, key="4")
            if inputShow2 != "":
                sceneList, mappingCoordinates = findScene(inputShow2)
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
