import streamlit as st
import streamlit.components.v1 as comp
from streamlit_folium import folium_static
import folium
from SPARQLWrapper import SPARQLWrapper, JSON

st.beta_set_page_config(layout="wide")  ## comment this out to disable widescreen

##if user selects to enter a scene, loads all scene from the selected movie
def findScene(show):
    filterstr = ""  ## string that gets inserted into the query, contains the filter
    if len(show) == 1:
        filterstr = (
            'FILTER(?title = "' + show[0] + '")'
        )  ## This could probably be inserted in a better way
    else:  ## but I did it like this to ensure double quotes for filtering purposes
        filterstr = "FILTER("
        for x in show:
            tempvar = (
                '?title = "' + x + '" || '
            )  ## basically adds multiple arguments to the filter condition
            filterstr = filterstr + tempvar
        filterstr = filterstr[:-3]  ## remove last 3 characters of str, which are "|| "
        filterstr = filterstr + ")"

    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT ?sceneName ?lon ?lat ?label where { 
        ?show a ex:Show.
        ?show ex:hasPrimaryTitle ?title.
        ?show ex:hasScene ?scene.
        ?scene rdfs:label ?sceneName.
    	?scene ex:hasLocation ?location.
    	    ?location ex:hasLongitude ?lon;
            ex:hasLatitude ?lat;
            rdfs:label ?label   
        %s 
    } 
    """
        % (filterstr)
    )  ## paste the show far into the string with %
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    sceneList, lonList, latList, dataList, labelList = [], [], [], [], []
    for result in results["results"]["bindings"]:
        sceneList.append(result["sceneName"]["value"])
        lonList.append(result["lon"]["value"])
        latList.append(result["lat"]["value"])
        labelList.append(result["label"]["value"])
    i = 0
    while i < len(lonList):
        tempList = [latList[i], lonList[i], labelList[i]]
        dataList.append(
            tempList
        )  ## datalist contains all info like coordinates, name of scene, name of location etc etc.
        i += 1
        ##Creates a map with scenes as key and all the associated data
    mappingCoordinates = dict(
        zip(sceneList, dataList)
    )  ## lat = value[0], lon = value[1], location = value[2]
    return sceneList, mappingCoordinates  ##


def findShow():
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select DISTINCT ?title where { 
            ?show a ex:Show;
                ex:hasPrimaryTitle ?title;
                  
            
    } 
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showList = []
    for result in results["results"]["bindings"]:
        showList.append(result["title"]["value"])
    return showList


def findActor():
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select DISTINCT ?name ?actor where { 
            ?character ex:playedBy ?actor.
            ?actor ex:hasFullName ?name
    }
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    actorNameList = []
    actorList = []  ## contains the actor code for our ontology
    for result in results["results"]["bindings"]:
        actorNameList.append(result["name"]["value"])
        actorList.append(result["actor"]["value"])
    actorNameList2 = []
    for (
        actor
    ) in (
        actorNameList
    ):  ## remove strings out of names. Dwayne 'The Rock" Johnson ==> Dwayne The Rock Johnson
        actor = actor.replace("'", "")
        actorNameList2.append(actor)
    return actorNameList2


def findShowActor(Actor):  ## finds all movies with a specific actor in it
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery(
        """
        PREFIX ex: <http://example.com/projectkand/>
        select DISTINCT ?title where { 
            ?actor ex:hasFullName '%s'.
            ?show a ex:Show.
            ?show ex:hasCharacter ?character.
            ?character ex:playedBy ?actor.
            ?show ex:hasPrimaryTitle ?title;
                    ex:hasScene ?scene  
    } 
    """
        % (Actor)
    )  ## when i say "movie ex:hasCharacter" it doesn't work. It infers actors in protege, but not in graphdb...
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showActorList = []
    for result in results["results"]["bindings"]:
        showActorList.append(result["title"]["value"])
    return showActorList


def findCoordinatesLocation(location):
    sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
    sparql.setQuery(
        """
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?city ?cityLabel ?coordinates WHERE {   
                ?city wdt:P31 wd:Q515;
                        rdfs:label ?cityLabel.
                filter(LANG(?cityLabel) = 'en').
                filter(?cityLabel = '%s'@en).
                ?city wdt:P625 ?coordinates
            }
            """
        % (location)
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    coordinates = ""
    for result in results["results"]["bindings"]:
        coordinates = result["coordinates"]["value"]  ## get the coordinate value
        coordinates = coordinates.replace("Point(", "")
        coordinates = coordinates.replace(")", "")  ## remove unneccesary characters
        coordinates = coordinates.replace(" ", ", ")
        stringList = coordinates.split(",")  ## put lon and lat into a list
        coordinateList = [float(x) for x in stringList]  ##convert str to float numbers
        coordinateList[0], coordinateList[1] = (
            coordinateList[1],
            coordinateList[0],
        )  ## change lon and lat indexes because wikidata is weird.
        print("dit is de coordinateList =    ", coordinateList)
    return coordinateList


##########################################################################################################################
col0, col1, col2, col3 = st.beta_columns([1, 3, 1, 5])
with col1:
    st.title("Movie location finder")
    st.text("So that you can fall into the same vulcano as Gollum")

## User selects his favorite movie/actor/whatever
with col1:
    with st.beta_expander("Shows"):
        showList = findShow()
        inputShow = st.multiselect("Select your favorite show", showList, key="1")
        st.write("Total number of movies in list = " + str(len(showList)))
        if inputShow != []:  ## If movie is selected, render the scene selectbox
            sceneList, mappingCoordinates = findScene(inputShow)
            inputScene = st.multiselect("Select your scene", sceneList, key="2")
            if (
                inputScene != []
            ):  ##if scene is selected, render the button to call the folium map
                coordinates, locations, scenes = [], [], []
                for key, value in mappingCoordinates.items():
                    if key in inputScene:
                        coordinates.append([value[0], value[1]])
                        locations.append(
                            value[2]
                        )  ## contains the locationName, used as popup
                        scenes.append(
                            key
                        )  ## contains the sceneName, will be used as a tooltip
                m2 = folium.Map(location=coordinates[0], zoom_start=16)
                i = 0
                tracker = 0  ## tracks which location the folium map currently has. if tracker = 0, location is the first scene.
                for x in coordinates:
                    folium.Marker(x, popup=locations[i], tooltip=scenes[i]).add_to(m2)
                    i += 1
                if st.button("test!", key="showButton"):
                    with col3:
                        folium_static(m2)
                        if st.button(
                            "Next scene", key="nextButton"
                        ):  ## These buttons do not work, I am having some issues with folium
                            tracker += 1
                            m2.location = coordinates[tracker]
                        if st.button("Previous scene"):
                            tracker -= 1
                            m2.location = coordinates[tracker]

with col1:
    with st.beta_expander("Actors"):
        actorList = findActor()
        st.write("Total number of actors in list = " + str(len(actorList)))
        inputActor = st.selectbox("Select your favorite Actor", actorList, key="3")
        if inputActor != "":
            showActorList = findShowActor(inputActor)
            inputShow2 = st.multiselect("select a show", showActorList, key="4")
            st.write("Total number of movies in list = " + str(len(showActorList)))
            if inputShow2 != []:
                sceneList, mappingCoordinates = findScene(inputShow2)
                inputScene = st.multiselect("Select your scene", sceneList, key="5")
                if (
                    inputScene != []
                ):  ##if scene is selected, render the button to call the folium map
                    coordinates, locations, scenes = [], [], []
                    for key, value in mappingCoordinates.items():
                        if key in inputScene:
                            coordinates.append([value[0], value[1]])
                            locations.append(
                                value[2]
                            )  ## contains the locationName, used as popup
                            scenes.append(
                                key
                            )  ## contains the sceneName, will be used as a tooltip
                    m2 = folium.Map(location=coordinates[0], zoom_start=16)
                    i = 0
                    for x in coordinates:
                        folium.Marker(x, popup=locations[i], tooltip=scenes[i]).add_to(
                            m2
                        )
                        i += 1
                    if st.button("test!", key="showButton2"):
                        with col3:
                            folium_static(m2)


## searchmode locations is still kind of outdated and doesn't use our own graphdb endpoint
with col1:
    with st.beta_expander("Locations"):
        locationInput = st.text_input(
            "Type your (ENGLISH) location name here", key="textinput1"
        )
        radiusInput = st.number_input(
            "Radius around the location, in meters", key="numberinput1"
        )
        if locationInput != "" and radiusInput != "":
            with col3:
                coordinatesList = findCoordinatesLocation(locationInput)
                m2 = folium.Map(location=coordinatesList, zoom_start=12)
                folium.Circle(
                    coordinatesList, radius=radiusInput, fill=True, fill_color="#3186cc"
                ).add_to(m2)
                folium_static(m2)
