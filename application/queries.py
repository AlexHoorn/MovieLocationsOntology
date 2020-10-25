from SPARQLWrapper import SPARQLWrapper, JSON
import streamlit as st


@st.cache
def wikidataActor(actorNumber):
    sparql = SPARQLWrapper(
        "https://query.wikidata.org/bigdata/namespace/wdq/sparql",
        agent="kick ass movielocator project",
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
        # SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . ?countryWD rdfs:label ?countryWDlabel . ?coordinates rdfs:label ?
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
        select DISTINCT ?lon ?lat ?sceneName ?showName ?locationInfo where { 
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
        ]  # , locationList[i]
        dataList.append(
            tempList
        )  ## datalist contains all info like coordinates, name of scene, name of location etc etc.
        i += 1
    return dataList  ##


@st.cache
def findScene(sparql, show):
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
    filter2 = ""
    if radioButton == "Actor":
        filter2 = "?person a ml:Actor;"
    else:
        filter2 = "?person a ml:Director;"
    sparql.setQuery(
        """
        PREFIX ml: <http://example.com/movieLocations/>
        select DISTINCT ?name ?person where { 
            %s
                 rdfs:label ?name.
    }
    """
        % (filter2)
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
        0, "Select a person!"
    )  ## This was done to prevent the query from auto-loading. you can not give st.select an empty value.
    return (
        actorNameList2,
        actorDict,
    )  ## Therefore, we add a value which is not an actor and only run the query when the user input is not equal to this value.


@st.cache
def findShowActor(
    sparql, Person, radioButton
):  ## finds all movies with a specific actor in it
    filter1 = ""

    if radioButton == "Actor":
        filter1 = "?show ml:hasActor ?actor. ?actor rdfs:label '%s'." % (Person)
    else:
        filter1 = "?show ml:hasDirector ?director. ?director rdfs:label '%s'." % (
            Person
        )

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
        % (filter1)  ## Doesn't return movies if they have no scenes.
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showTitleList = []
    locationList = []
    if radioButton == "Actor" or radioButton == "Director":
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
    else:
        pass

    return showTitleList, tempDict


@st.cache
def findShow(sparql, radioButton):
    selectFilter = "?title"
    secondFilter = "?show ml:hasScene ?scene"
    if radioButton == "Movies":
        selectFilter = "?title ?lon ?lat ?locationInfo ?sceneName"
        secondFilter = """?show ml:hasLocation ?location. ?location ml:hasLongitude ?lon; ml:hasLatitude ?lat; rdfs:label ?locationInfo. 
                            OPTIONAL{?scene a ml:Scene.
                                    ?show ml:hasScene ?scene.
                                    ?scene ml:hasLocation ?location;
                                            rdfs:label ?sceneName}"""
    sparql.setQuery(
        """  
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT %s where { 
            ?show rdf:type ml:Show;
                rdfs:label ?title.
            %s
                    } 
    """
        % (selectFilter, secondFilter)
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showList = []
    movieLocationList = []

    movieLocationDict = {}
    if radioButton == "Movies":
        for result in results["results"]["bindings"]:
            showList.append(result["title"]["value"])
            lonLat = [result["lon"]["value"], result["lat"]["value"]]
            if "sceneName" in result:
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
                ]  ##create 2 dimensional list containing a movie + coordinates per index
            movieLocationList.append(tempvar)
        for movie, coordinates, locationInfo, sceneName in movieLocationList:
            if (
                movie in movieLocationDict
            ):  ## create dictionary with movies as key, containing 1 or more set of coordinates per key
                tempvar = [coordinates, locationInfo, sceneName]
                movieLocationDict[movie].append(tempvar)
            else:
                movieLocationDict[movie] = [[coordinates, locationInfo, sceneName]]
        showList = list(
            dict.fromkeys(showList)
        )  ## remove dupes from showlist, gets used for multiselectbox
    else:
        for result in results["results"]["bindings"]:
            showList.append(result["title"]["value"])
    return showList, movieLocationDict
