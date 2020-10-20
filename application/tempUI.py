import streamlit as st
import streamlit.components.v1 as comp
#from components import load_ontology, query_to_pandas
from streamlit_folium import folium_static
import folium
from SPARQLWrapper import SPARQLWrapper, JSON
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from math import radians, cos, sin, asin, sqrt

st.beta_set_page_config(layout="wide")  ## comment this out to disable widescreen

userName = "sceneLocator"
geolocator = Nominatim(user_agent=userName)
geocode = RateLimiter(
    geolocator.geocode, min_delay_seconds=1.05, swallow_exceptions=True
)

sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test2")

#with st.spinner("Loading ontology, this could take some time the first run"):
#    # Loads the ontology, the output of this gets cached, returns a Graph
#    g = load_ontology("../ontology/PopulatedOntology.owl")


def haversine(
    lon1, lat1, lon2, lat2
):  ## calculates wether a geolocation is within the radius of another specified location
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def findAllLocations():
    #sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
    sparql.setQuery(
        """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select ?location ?lon ?lat ?sceneName where { 
            ?scene a ml:Scene;
                ml:hasLocation ?location;    
                rdfs:label ?sceneName.
            ?location ml:hasLatitude ?lat;
                    ml:hasLongitude ?lon. 
        }
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    locationList, lonList, latList, sceneList, dataList = [], [], [], [], []
    for result in results["results"]["bindings"]:
        locationList.append(result['location']['value'])
        lonList.append(result['lon']['value'])
        latList.append(result['lat']['value'])
        sceneList.append(result['sceneName']['value'])
    i = 0
    while i < len(lonList):
        tempList = [latList[i], lonList[i], sceneList[i]]  # , locationList[i]
        dataList.append(
            tempList
        )  ## datalist contains all info like coordinates, name of scene, name of location etc etc.
        i += 1
    return dataList  ##


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

    #sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
    sparql.setQuery(
        """
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT ?sceneName ?lon ?lat ?label where { 
            ?show ml:hasScene ?scene.
            ?show rdfs:label ?title.
            ?scene rdfs:label ?sceneName.
            ?scene ml:hasLocation ?location.
            ?location ml:hasLongitude ?lon;
                ml:hasLatitude ?lat;
                rdfs:label ?label   
            %s 
    } 
    """
        % (filterstr)
    )
      ## paste the show far into the string with %
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    sceneList, lonList, latList, dataList, labelList = [], [], [], [], []
    for result in results["results"]["bindings"]:
        sceneList.append(result['sceneName']['value'])
        lonList.append(result['lon']['value'])
        latList.append(result['lat']['value'])
        labelList.append(result['label']['value'])
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
    #print('dit is de sceneList', sceneList)
    #print('dit is de mappingCoordinates', mappingCoordinates)
    return sceneList, mappingCoordinates  ##


def findShow():
    #sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
    sparql.setQuery(
        """  
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT ?title where { 
                ?show a ml:Show;
                    rdfs:label ?title     
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
    #sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
    sparql.setQuery(
        """
        PREFIX ml: <http://example.com/movieLocations/>
        select DISTINCT ?name ?actor where { 
            ?actor a ml:Actor;
                 rdfs:label ?name.
            ?
    }
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    actorNameList = []
    actorList = []  ## contains the actor code for our ontology
    for result in results["results"]["bindings"]:
        actorNameList.append(result['name']['value'])
        actorList.append(result['actor']['value'])
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
    #sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
    sparql.setQuery( 
        """
        PREFIX ml: <http://example.com/movieLocations/>
        select DISTINCT ?title where { 
            ?show ml:hasCharacter ?character.
            ?character ml:playedBy ?actor.
            ?actor rdfs:label '%s'.
            ?show rdfs:label ?title;
                    ml:hasScene ?scene  
    } 
    """
        % (Actor)
    )  
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showActorList = []
    for result in results["results"]["bindings"]:
        showActorList.append(result['title']['value'])
    return showActorList


def findCoordinatesLocation(location):  ## This is currently not being used
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
    #print(results)
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


## use Nominatim to gather coordinate information
with col1:
    with st.beta_expander("Locations"):
        locationInput = st.text_input("Type your location name here", key="textinput1")
        radiusInput = st.number_input(
            "Radius around the location, in kilometers",
            format="%f",
            min_value=0.5,
            value=1.0,
            key="numberinput1",
        )
        if locationInput != "" and radiusInput > 0.5:
            with col3:
                coordinatesList = []
                coordinateOutput = geolocator.geocode(locationInput)
                coordinatesList.extend(
                    [coordinateOutput.latitude, coordinateOutput.longitude]
                )
                allLocations = findAllLocations()
                if coordinatesList != []:
                    m2 = folium.Map(location=coordinatesList, zoom_start=14)
                    folium.Circle(
                        coordinatesList,
                        radius=radiusInput * 1000,
                        fill=True,
                        fill_color="#3186cc",
                    ).add_to(m2)
                    for lat, lon, scene in allLocations:
                        a = haversine(
                            coordinatesList[1],
                            coordinatesList[0],
                            float(lon),
                            float(lat),
                        )
                        if a < (radiusInput):
                            folium.Marker((lat, lon), tooltip=scene).add_to(m2)
                            print(
                                lon,
                                lat,
                                "zit in de radius van",
                                coordinatesList,
                                "op basis van radius",
                                radiusInput,
                            )
                    folium_static(m2)

## todo : set input radius
## radius <700, zoom 15
## radius 1000, zoom 14
## radius 2000, zoom 13
## radius 4000, zoom 12
