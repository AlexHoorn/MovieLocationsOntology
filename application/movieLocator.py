from io import BytesIO

import folium
import requests
import streamlit as st
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from PIL import Image
from SPARQLWrapper import SPARQLWrapper
from streamlit_folium import folium_static

import queries as Q
from components import get_config, haversine, overwrite_config, verify_endpoint

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

# with st.spinner("Hold up, we're pre-caching some things."): ## <<<<---- everytime you change queries.py you need to reload the entire application. Turned off while developing.
#    _ = Q.findAllLocations(sparql)
#    del _

#### Setting up the geolocator which is neccesary for the location func, pls don't delete #####
userName = "sceneLocator"
geolocator = Nominatim(user_agent=userName)
geocode = RateLimiter(
    geolocator.geocode, min_delay_seconds=1.05, swallow_exceptions=True
)
##################################################################################################

col0, col1, col2, col3, col4, col5, col6 = st.beta_columns(
    [0.5, 2, 0.5, 3, 0.5, 1.3, 0.2]
)  ## the small columns (0.5) are used for padding purposes
with col1:
    st.title("Movie location finder")
    st.write("So that you can fall into the same vulcano as Gollum.")

    ## User selects his favorite movie/actor/whatever
    with st.beta_expander("Shows"):
        movieLocationList = []
        radioOptions = ["Movie scenes", "Movies"]
        radioInput = st.radio(
            "Look for all scenes of a movie, or individual scenes of a movie",
            radioOptions,
            key="radio1",
            format_func=lambda x: {
                "Movie scenes": "Select specific scenes",
                "Movies": "Select all scenes",
            }[x],
        )
        showList = Q.findShow(sparql, radioInput)
        st.write(f"{len(showList)} shows available.")

        if radioInput == "Movies":
            inputShow3 = st.multiselect(
                "Select show(s)", showList, key="randomkey12344"
            )
            if inputShow3 != []:
                movieLocationDict = Q.findShowLocations(sparql, inputShow3)
                mapInitialized = False
                for (
                    key,
                    value,
                ) in (
                    movieLocationDict.items()
                ):  ## dictionary contains every show as a key, and all the scenes/locations etc as a value list
                    for show in inputShow3:
                        if show in key:
                            tempValue = [show, value]
                            movieLocationList.append(tempValue)
                for movie in movieLocationList:
                    for x in range(len(movie[1])):
                        lon = movie[1][x][0][1]
                        lat = movie[1][x][0][0]
                        scene = movie[1][x][2]
                        location = movie[1][x][1]
                        if mapInitialized == False:
                            m2 = folium.Map(location=[lon, lat], zoom_start=12)
                            mapInitialized = True
                        if "Filming location" in scene:
                            folium.Marker(
                                [lon, lat],
                                popup="<b>Location:</b>" + location,
                                tooltip=movie[0],
                            ).add_to(m2)
                        else:
                            folium.Marker(
                                [lon, lat],
                                popup="<b>Scene:</b> " + scene + "\n<b>Location:</b> " + location,
                                tooltip=movie[0],
                            ).add_to(m2)

                if st.button("Render map", key="showButton"):
                    with col3:
                        folium_static(m2)
        if radioInput == "Movie scenes":
            inputShow = st.multiselect("Select show(s)", showList, key="1")
            if inputShow != []:  ## If movie is selected, render the scene selectbox
                sceneList, mappingCoordinates = Q.findScene(sparql, inputShow)
                inputScene = st.multiselect("Select scene(s)", sceneList, key="2")
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
                    m2 = folium.Map(location=coordinates[0], zoom_start=12)
                    i = 0
                    tracker = 0  ## tracks which location the folium map currently has. if tracker = 0, location is the first scene.
                    for x in coordinates:
                        folium.Marker(
                            x, popup="<b>Location:</b> " + locations[i], tooltip=scenes[i]
                        ).add_to(m2)
                        i += 1
                    if st.button("Render map", key="showButton"):
                        with col3:
                            folium_static(m2)

    with st.beta_expander("Actors and directors"):
        mapInitialized2 = False
        radioOptions2 = ["Actor", "Director"]
        radioInput2 = st.radio(
            "Look for an actor or a director",
            radioOptions2,
            key="radio1",
        )
        labelString = (
            f"Select a{'n' if radioInput2 == 'Actor' else ''} {radioInput2.lower()}"
        )
        actorList, actorDict = Q.findPerson(sparql, radioInput2)
        st.write(f"{len(actorList)} {radioInput2.lower()}s available.")
        inputActor = st.selectbox(labelString, actorList, key="3")
        actorNumber = ""
        if inputActor != "Select a person":
            for (
                key,
                value,
            ) in (
                actorDict.items()
            ):  ## find the selected actor/director in the result list
                if inputActor in key:
                    actorNumber = value
                    break
            wikiImage, wikiDescription = Q.wikidataActor(
                actorNumber
            )  ## gather wikidata info (image, description)
            showActorList, locationDict = Q.findShowActor(
                sparql, inputActor, radioInput2
            )
            st.write(
                f"{len(showActorList)} show{'s' if len(showActorList) > 1 else ''} available."
            )
            inputShow2 = st.multiselect("Select show(s)", showActorList, key="4")
            if wikiImage != "":
                with col5:
                    response = requests.get(
                        wikiImage
                    )  ## Open the image from the imagelink, then display it
                    img = Image.open(BytesIO(response.content))
                    st.image(img, use_column_width=True, caption=inputActor)
            if wikiDescription != "":
                with col5:  ## write the description from wikidata on the page
                    st.write(wikiDescription)

            if inputShow2 != []:
                for key, value in locationDict.items():
                    for show in inputShow2:
                        if (
                            show in key
                        ):  ## if chosen show is in the dictionary of shows, create the markers
                            for value2 in value:
                                lon = value2[0][0]
                                lat = value2[0][1]
                                if mapInitialized2 == False:
                                    m2 = folium.Map(location=[lat, lon], zoom_start=12)
                                    mapInitialized2 = True
                                sceneName = value2[1]
                                locationName = value2[2]
                                if "Filming location" in sceneName:
                                    folium.Marker(
                                        [lat, lon],
                                        popup="<b>Location:</b>  " + locationName,
                                        tooltip=show,
                                    ).add_to(m2)
                                else:
                                    folium.Marker(
                                        [lat, lon],
                                        popup="<b>Scene:</b> "
                                        + sceneName
                                        + "\n<b>Location:</b> "
                                        + locationName,
                                        tooltip=show,
                                    ).add_to(m2)
                if st.button("Render map", key=13213232133):
                    with col3:
                        folium_static(m2)

    ## use Nominatim to gather coordinate information
    with st.beta_expander("Locations"):
        locationInput = st.text_input("Type a location", key="textinput1")
        radiusInput = st.number_input(
            "Radius around the location (km)",
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
                for lat, lon, scene, movie, location in allLocations:
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
                            location,
                        ]  ## all the scenes in the radius also get added in a different list, with their movie and coordinates
                        finalList.append(tempvar)

                movieList = ["Select all movies"]
                for movie in tempMovieList:
                    if (
                        movie not in movieList
                    ):  ## creates a list, without duplicates, of all movies within the radius, including the "select all movies"
                        movieList.append(movie)

                movieLocationInput = st.multiselect(
                    "Select movie(s)", movieList, key=123123
                )

                if movieLocationInput != []:
                    if st.button("Render map"):
                        if (
                            "Select all movies" in movieLocationInput
                        ):  ## if "Select all movies" is chosen, render all the scenes in the radius
                            for lat, lon, scene, movie, location in finalList:
                                if "Filming location" in scene:
                                    folium.Marker(
                                        (lat, lon),
                                        tooltip=movie,
                                        popup="<b>Location:</b>\n" + location,
                                    ).add_to(m2)
                                else:
                                    folium.Marker(
                                        (lat, lon),
                                        tooltip=movie,
                                        popup="<b>Scene:</b> " + scene + "\n"
                                        "<b>Location:</b> " + location,
                                    ).add_to(m2)
                        else:
                            for lat, lon, scene, movie, location in finalList:
                                if (
                                    movie in movieLocationInput
                                ):  ## otherwise, render the scenes in the radius of the selected movies only.
                                    if "Filming location" in scene:
                                        folium.Marker(
                                            (lat, lon),
                                            tooltip=movie,
                                            popup="<b>Location:</b>\n" + location,
                                        ).add_to(m2)
                                    else:
                                        folium.Marker(
                                            (lat, lon),
                                            tooltip=movie,
                                            popup="<b>Scene:</b> " + scene + "\n"
                                            "<b>Location:</b> " + location,
                                        ).add_to(m2)
                        with col3:
                            folium_static(m2)
