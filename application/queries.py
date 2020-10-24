from SPARQLWrapper import SPARQLWrapper, JSON
import streamlit as st

@st.cache
def wikidataActor(actorNumber):
    sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
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
    # sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
    sparql.setQuery(
        """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select ?location ?lon ?lat ?sceneName ?movieName where { 
            ?movie ml:hasScene ?scene;
                    rdfs:label ?movieName.
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
    locationList, lonList, latList, sceneList, movieList, dataList = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for result in results["results"]["bindings"]:
        locationList.append(result["location"]["value"])
        lonList.append(result["lon"]["value"])
        latList.append(result["lat"]["value"])
        sceneList.append(result["sceneName"]["value"])
        movieList.append(result["movieName"]["value"])
    i = 0
    while i < len(lonList):
        tempList = [
            latList[i],
            lonList[i],
            sceneList[i],
            movieList[i],
        ]  # , locationList[i]
        dataList.append(
            tempList
        )  ## datalist contains all info like coordinates, name of scene, name of location etc etc.
        i += 1
    return dataList  ##


##if user selects to enter a scene, loads all scene from the selected movie

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

    # sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
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
    # print('dit is de sceneList', sceneList)
    # print('dit is de mappingCoordinates', mappingCoordinates)
    return sceneList, mappingCoordinates  ##

@st.cache
def findShow(sparql, radioButton):
    selectFilter = '?title'
    secondFilter = '?show ml:hasScene ?scene'
    if radioButton == 'Movies':
        selectFilter = '?title ?lon ?lat'
        secondFilter = '?show ml:hasLocation ?location. ?location ml:hasLongitude ?lon; ml:hasLatitude ?lat'
    sparql.setQuery(
        """  
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT %s where { 
            ?show rdf:type ml:Show;
                rdfs:label ?title.
            %s
                    } LIMIT 100
    """
    % (selectFilter, secondFilter)
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showList = []
    movieLocationList = []
    movieLocationDict = {}
    if radioButton == 'Movies':
        for result in results["results"]["bindings"]:
            showList.append(result['title']['value'])
            lonLat = [result['lon']['value'],result['lat']['value']]
            tempvar = [result['title']['value'], lonLat] ##create 2 dimensional list containing a movie + coordinates per index
            movieLocationList.append(tempvar)
        for movie, coordinates in movieLocationList: 
            if movie in movieLocationDict: ## create dictionary with movies as key, containing 1 or more set of coordinates per key
                movieLocationDict[movie].append(coordinates)
            else:
                movieLocationDict[movie] = [coordinates]
        showList = list(dict.fromkeys(showList)) ## remove dupes from showlist, gets used for multiselectbox
    else:
        for result in results["results"]["bindings"]:
            showList.append(result["title"]["value"])
    return showList, movieLocationDict

@st.cache
def findActor(sparql):
    # sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
    sparql.setQuery(
        """
        PREFIX ml: <http://example.com/movieLocations/>
        select DISTINCT ?name ?actor where { 
            ?actor a ml:Actor;
                 rdfs:label ?name.
    }
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    actorNameList = []
    actorNumberList = []  ## contains the actor code from our ontology
    for result in results["results"]["bindings"]:
        actorNameList.append(result["name"]["value"])
        actorNumberList.append(result["actor"]["value"])
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
    actorNameList2.insert(0, "Select an actor!") ## This was done to prevent the query from auto-loading. you can not give st.select an empty value.
    return actorNameList2, actorDict             ## Therefore, we add a value which is not an actor and only run the query when the user input is not equal to this value.


@st.cache
def findShowActor(sparql, Actor):  ## finds all movies with a specific actor in it
    # sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")

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
        % (Actor) ## Doesn't return movies if they have no scenes.
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showActorList = []
    for result in results["results"]["bindings"]:
        showActorList.append(result["title"]["value"])
    return showActorList
