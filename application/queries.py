from SPARQLWrapper import SPARQLWrapper, JSON


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
    #SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . ?countryWD rdfs:label ?countryWDlabel . ?coordinates rdfs:label ?
    %actorNumber
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    imageList, description = [], ''
    for result in results["results"]["bindings"]:
        if "image" in result:
            imageList.append(result["image"]["value"])
        description = result["actorDescription"]["value"]
    return imageList, description


def findAllLocations(sparql):
    #sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
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
    locationList, lonList, latList, sceneList, movieList, dataList = [], [], [], [], [], []
    for result in results["results"]["bindings"]:
        locationList.append(result['location']['value'])
        lonList.append(result['lon']['value'])
        latList.append(result['lat']['value'])
        sceneList.append(result['sceneName']['value'])
        movieList.append(result['movieName']['value'])
    i = 0
    while i < len(lonList):
        tempList = [latList[i], lonList[i], sceneList[i], movieList[i]]  # , locationList[i]
        dataList.append(
            tempList
        )  ## datalist contains all info like coordinates, name of scene, name of location etc etc.
        i += 1
    return dataList  ##


##if user selects to enter a scene, loads all scene from the selected movie

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


def findShow(sparql):
    #sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
    sparql.setQuery(
        """  
        PREFIX ml: <http://example.com/movieLocations/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select DISTINCT ?title where { 
                ?show rdf:type ?any_show;
                    rdfs:label ?title.
                ?any_show rdfs:subClassOf* ml:Show.
                    } 
    """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    showList = []
    for result in results["results"]["bindings"]:
        showList.append(result["title"]["value"])
    return showList


def findActor(sparql):
    #sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/test3")
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
        actorNameList.append(result['name']['value'])
        actorNumberList.append(result['actor']['value'])
    actorNumberList2 = [str(i).replace( 'http://example.com/movieLocations/', '') for i in actorNumberList] ## removes the ontology prefix       
    actorNameList2 = []
    for (
        actor
    ) in (
        actorNameList
    ):  ## remove strings out of names. Dwayne 'The Rock" Johnson ==> Dwayne The Rock Johnson
        actor = actor.replace("'", "")
        actorNameList2.append(actor)

    actorDict = dict(zip(actorNameList2, actorNumberList2)) ## Make a dict of each actor with their
    return actorNameList2, actorDict

def findShowActor(sparql, Actor):  ## finds all movies with a specific actor in it
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


def findCoordinatesLocation(sparql, location):  ## This is currently not being used
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
        #print("dit is de coordinateList =    ", coordinateList)
    return coordinateList