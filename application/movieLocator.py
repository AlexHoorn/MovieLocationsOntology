from math import asin, cos, radians, sin, sqrt

import folium
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from SPARQLWrapper import JSON, SPARQLWrapper
from streamlit_folium import folium_static

import queries as Q
from components import get_config, overwrite_config, verify_endpoint

st.beta_set_page_config(layout="wide")  ## comment this out to disable widescreen

# Fetches configuration
config = get_config()
endpoint = config["Configuration"]["Endpoint"]

# Display an option to set the endpoint if not configured
if endpoint == "":
    endpoint_input = st.text_input("Set a SPARQL endpoint")

    if endpoint_input != "":
        config["Configuration"]["Endpoint"] = endpoint_input

        # Verify endpoint
        try:
            verify_endpoint(endpoint_input)
        except Exception as e:
            st.error(f"`{endpoint_input}` doesn't seem to be a valid endpoint")
            raise e

        # Saves the verified endpoint to the configfile
        overwrite_config(config)
        st.experimental_rerun()

    else:
        st.stop()

sparql = SPARQLWrapper(endpoint)

# with st.spinner("Loading ontology, this could take some time the first run"):
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


col0, col1, col2, col3 = st.beta_columns([1, 3, 1, 5])
with col1:
    st.title("Movie location finder")
    st.text("So that you can fall into the same vulcano as Gollum")

## User selects his favorite movie/actor/whatever
with col1:
    with st.beta_expander("Shows"):
        showList = Q.findShow(sparql)
        inputShow = st.multiselect("Select your favorite show", showList, key="1")
        st.write("Total number of movies in list = " + str(len(showList)))
        if inputShow != []:  ## If movie is selected, render the scene selectbox
            sceneList, mappingCoordinates = Q.findScene(sparql, inputShow)
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
                if st.button("Show map!", key="showButton"):
                    with col3:
                        folium_static(m2)
                        if st.button(  ## buttons to re-render the map with the next/previous scene in the list as the starting point.
                            "Next scene", key="nextButton"
                        ):  ## A button inside of another button doesn't work, I think because if you click it it reloads and goes out of the previous if-statement
                            tracker += 1  ## solution could be to not have the "show map" button but instead already have 2 buttons similar to next/previous scene
                            m2.location = coordinates[tracker]
                            folium_static(m2)
                        if st.button("Previous scene"):
                            tracker -= 1  ## Tracker also resets everytime, not sure if you can easily save variables like this during reloads
                            m2.location = coordinates[tracker]
                            folium_static(m2)

with col1:
    with st.beta_expander("Actors"):
        actorList = Q.findActor(sparql)
        st.write("Total number of actors in list = " + str(len(actorList)))
        inputActor = st.selectbox("Select your favorite Actor", actorList, key="3")
        if inputActor != "":
            showActorList = Q.findShowActor(sparql, inputActor)
            inputShow2 = st.multiselect("select a show", showActorList, key="4")
            st.write("Total number of movies in list = " + str(len(showActorList)))
            if inputShow2 != []:
                sceneList, mappingCoordinates = Q.findScene(sparql, inputShow2)
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
            coordinatesList = []
            coordinateOutput = geolocator.geocode(locationInput)
            coordinatesList.extend(
                [coordinateOutput.latitude, coordinateOutput.longitude]
            )
            allLocations = Q.findAllLocations(sparql)
            if coordinatesList != []:
                m2 = folium.Map(location=coordinatesList, zoom_start=14)
                folium.Circle(  ## create radius circle
                    coordinatesList,
                    radius=radiusInput * 1000,
                    fill=True,
                    fill_color="#3186cc",
                ).add_to(m2)
                dictSceneMovie = {}
                tempSceneList, tempMovieList = [], []
                finalList = []
                for lat, lon, scene, movie in allLocations:
                    a = haversine(  ## does a radius check, comparing every scene in the ontology to the user input location
                        coordinatesList[1],
                        coordinatesList[0],
                        float(lon),
                        float(lat),
                    )
                    if a < (
                        radiusInput
                    ):  ## all the movies of which there are scenes get added to a list
                        tempMovieList.append(movie)
                        tempvar = [
                            lat,
                            lon,
                            scene,
                            movie,
                        ]  ## all the scenes in the radius also get added in a different list, with their movie and coordinates
                        finalList.append(tempvar)

                movieList = ["Select all movies"]
                for movie in tempMovieList:
                    if (
                        movie not in movieList
                    ):  ## creates a list, without duplicates, of all movies within the radius, including the "select all movies"
                        movieList.append(movie)

                movieLocationInput = st.multiselect(
                    "Select your movies!", movieList, key=123123
                )

                if movieLocationInput != []:
                    if st.button("Render map!"):
                        if (
                            "Select all movies" in movieLocationInput
                        ):  ## if "Select all movies" is chosen, render all the scenes in the radius
                            for lat, lon, scene, movie in finalList:
                                folium.Marker(
                                    (lat, lon), tooltip=scene, popup=movie
                                ).add_to(m2)
                        else:
                            for lat, lon, scene, movie in finalList:
                                if (
                                    movie in movieLocationInput
                                ):  ## otherwise, render the scenes in the radius of the selected movies only.
                                    folium.Marker(
                                        (lat, lon), tooltip=scene, popup=movie
                                    ).add_to(m2)
                        with col3:
                            folium_static(m2)

## todo : set input radius
## radius <700, zoom 15
## radius 1000, zoom 14
## radius 2000, zoom 13
## radius 4000, zoom 12
