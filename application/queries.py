import streamlit as st
from SPARQLWrapper import JSON, SPARQLWrapper

from components import generate_filter_string


@st.cache
def wikidataActor(actorNumber):
    sparql = SPARQLWrapper(
        "https://query.wikidata.org/bigdata/namespace/wdq/sparql",
        agent="KDD MovieLocator Project",
    )
    sparql.setQuery(
        """
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX bd: <http://www.bigdata.com/rdf#>
        SELECT ?actor  ?image ?actorDescription  WHERE {   
            ?actor wdt:P345 '%s'.
            OPTIONAL{?actor wdt:P18 ?image.}
            SERVICE wikibase:label {bd:serviceParam wikibase:language "en".
            }
                       
        }
    """
        % actorNumber
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    image, description = "", ""
    for result in results["results"]["bindings"]:
        if "image" in result:
            image = result["image"]["value"]
        description = result["actorDescription"]["value"]
    return image, description


@st.cache
def findAllLocations(sparql):
    sparql.setQuery(
        """
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select ?lon ?lat ?sceneName ?showName ?locationInfo where { 
            ?show a ml:Show;
                ml:hasLocation ?location;
                rdfs:label ?showName.
            ?location ml:hasLatitude ?lat;
                    ml:hasLongitude ?lon;
                    rdfs:label ?locationInfo 
            OPTIONAL{
                ?scene a ml:Scene.
                ?show ml:hasScene ?scene.
                ?scene ml:hasLocation ?location;
                    rdfs:label ?sceneName. 
            }
        }
        ORDER BY ?showName
        """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    locationList, lonList, latList, sceneList, movieList, dataList = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for result in results["results"]["bindings"]:
        locationList.append(result["locationInfo"]["value"])
        lonList.append(result["lon"]["value"])
        latList.append(result["lat"]["value"])
        if "sceneName" in result:
            sceneList.append(result["sceneName"]["value"])
        else:
            sceneList.append("Filming location")
        movieList.append(result["showName"]["value"])
    i = 0
    while i < len(lonList):
        tempList = [
            latList[i],
            lonList[i],
            sceneList[i],
            movieList[i],
            locationList[i],
        ]  
        dataList.append(
            tempList
        )  ## datalist contains all info like coordinates, name of scene, name of location etc etc.
        i += 1
    return dataList  ##


@st.cache
def findScene(sparql, show):
    filterstr = generate_filter_string("title", show)
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
        ORDER BY ?sceneName
        """
        % (filterstr)
    )
    ## paste the show far into the string with %
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


@st.cache
def findPerson(
    sparql, radioButton
):  ## this query can work for both actors and directors
    sparql.setQuery(
        """
        PREFIX ml: <http://example.com/movieLocations/>
        select DISTINCT ?name ?person where { 
            ?person a ml:%s;
                 rdfs:label ?name.
        }
        ORDER BY ?name
        """
        % (radioButton)
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    actorNameList = []
    actorNumberList = []  ## contains the actor code from our ontology
    for result in results["results"]["bindings"]:
        actorNameList.append(result["name"]["value"])
        actorNumberList.append(result["person"]["value"])
    actorNumberList2 = [
        str(i).replace("http://example.com/movieLocations/", "")
        for i in actorNumberList
    ]  ## removes the ontology prefix
    actorNameList2 = []
    for (
        actor
    ) in (
        actorNameList
    ):  ## remove strings out of names. Dwayne 'The Rock" Johnson ==> Dwayne The Rock Johnson
        actor = actor.replace("'", "")
        actorNameList2.append(actor)

    actorDict = dict(
        zip(actorNameList2, actorNumberList2)
    )  ## Make a dict of each actor with their
    actorNameList2.insert(
        0, "Select a person"
    )  ## This was done to prevent the query from auto-loading. you can not give st.select an empty value.
    return (
        actorNameList2,
        actorDict,
    )  ## Therefore, we add a value which is not an actor and only run the query when the user input is not equal to this value.


@st.cache
def findShowActor(
    sparql, Person, radioButton
):  ## finds all movies with a specific actor in it
    filter1 = f"?show ml:has{radioButton} ?{radioButton.lower()}. ?{radioButton.lower()} rdfs:label '{Person}'."
    sparql.setQuery(
        """
        PREFIX ml: <http://example.com/movieLocations/>
        select DISTINCT ?title ?sceneName ?lon ?lat ?locationName where { 
            %s
            ?show rdfs:label ?title;
                  ml:hasLocation ?location.
            ?location ml:hasLongitude ?lon;
                      ml:hasLatitude ?lat;
                      rdfs:label ?locationName
            OPTIONAL{
                ?scene a ml:Scene.
                ?show ml:hasScene ?scene.
                ?scene ml:hasLocation ?location;
                    rdfs:label ?sceneName. 
            }        
    } 
    """
        % (filter1)
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showTitleList = []
    locationList = []
    for result in results["results"]["bindings"]:
        showTitleList.append(result["title"]["value"])
        lonLat = [result["lon"]["value"], result["lat"]["value"]]
        if "sceneName" in result:
            tempvar = [
                result["title"]["value"],
                lonLat,
                result["sceneName"]["value"],
                result["locationName"]["value"],
            ]
        else:
            tempvar = [
                result["title"]["value"],
                lonLat,
                "Filming location",
                result["locationName"]["value"],
            ]
        locationList.append(tempvar)
    tempDict = {}
    for movie, location, sceneName, locationName in locationList:
        if movie in tempDict:
            tempvar = [location, sceneName, locationName]
            tempDict[movie].append(tempvar)
        else:
            tempDict[movie] = [[location, sceneName, locationName]]
    showTitleList = list(dict.fromkeys(showTitleList))

    return showTitleList, tempDict


@st.cache
def findShow(sparql, radioButton):
    filterStr = ""
    if radioButton == "Movie scenes":
        filterStr = "?show ml:hasScene ?scene"
    sparql.setQuery(
        """  
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT ?title where { 
            ?show rdf:type ml:Show;
                rdfs:label ?title.
            %s
                    } 
                    ORDER BY ?title
    """
        % (filterStr)
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showList = []
    for result in results["results"]["bindings"]:
        showList.append(result["title"]["value"])
    return showList


@st.cache
def findShowLocations(sparql, show):
    filterstr = generate_filter_string("title", show)
    sparql.setQuery(
        """
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT ?title ?sceneName ?lon ?lat ?locationInfo where { 
            ?show rdfs:label ?title.
            ?show ml:hasLocation ?location.
            ?location ml:hasLongitude ?lon;
                ml:hasLatitude ?lat;
                rdfs:label ?locationInfo.
            OPTIONAL{?scene a ml:Scene. 
                    ?show ml:hasScene ?scene.
                    ?scene ml:hasLocation ?location;
                            rdfs:label ?sceneName}   
            %s 
            
    } 
    """
        % (filterstr)
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    movieLocationDict = {}
    movieLocationList = []
    for result in results["results"]["bindings"]:
        lonLat = [result["lon"]["value"], result["lat"]["value"]]
        if "sceneList" in result:
            tempvar = [
                result["title"]["value"],
                lonLat,
                result["locationInfo"]["value"],
                result["sceneName"]["value"],
            ]
        else:
            tempvar = [
                result["title"]["value"],
                lonLat,
                result["locationInfo"]["value"],
                "Filming location",
            ]
        movieLocationList.append(tempvar)
        for movie, coordinates, locationInfo, sceneName in movieLocationList:
            if (
                movie in movieLocationDict
            ):  ## create dictionary with movies as key, containing 1 or more set of coordinates per key
                tempvar = [coordinates, locationInfo, sceneName]
                movieLocationDict[movie].append(tempvar)
            else:
                movieLocationDict[movie] = [[coordinates, locationInfo, sceneName]]
    return movieLocationDict  ##
