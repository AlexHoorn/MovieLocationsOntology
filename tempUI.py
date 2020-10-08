import streamlit as st
import streamlit.components.v1 as comp
from streamlit_folium import folium_static
import folium
from SPARQLWrapper import SPARQLWrapper, JSON

## The queries that are not inside a function are outdated, and use dbpedia instead of our local ontology, will be changed soon
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX yago: <http://dbpedia.org/class/yago/>
    SELECT  * WHERE { 
    ?actor a yago:Actor109765278;
    rdfs:label ?actorLabel
    FILTER(langMatches(lang(?actorLabel),"EN"))
    } LIMIT 100
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
actorList = ['']
for result in results["results"]["bindings"]:
    actorList.append(result["actorLabel"]["value"])

sparql.setQuery("""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT  * WHERE { 
    ?city a dbo:City;
    rdfs:label ?cityLabel
    FILTER(langMatches(lang(?cityLabel),"EN"))
    } LIMIT 100
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
locationList = ['']
for result in results["results"]["bindings"]:
    locationList.append(result["cityLabel"]["value"])    

##if user selects to enter a scene, loads all scene from the selected movie
def findScene(movie):
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")
    sparql.setQuery("""
        PREFIX ex: <http://example.com/projectkand/>
        select ?scene ?lon ?lat where { 
        ?movie a ex:Movie.
        ?movie ex:HasPrimaryTitle ?title.
        ?movie ex:HasScene ?scene.
        ?scene ex:HasLongitude ?lon;
            ex:HasLatitude ?lat    
        FILTER(?title = '%s'@en) 
    } limit 100 
    """ % (movie))  ## paste the movie far into the string with %
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    sceneList, lonList, latList, lonLatList = [], [], [], []
    for result in results["results"]["bindings"]:
        sceneList.append(result['scene']['value'])
        lonList.append(result['lon']['value'])
        latList.append(result['lat']['value'])
    i = 0
    while i < len(lonList): 
        tempList = [lonList[i], latList[i]]
        lonLatList.append(tempList)
        i += 1
    sparql = SPARQLWrapper("http://dbpedia.org/sparql") ##Creates a map with scenes as key and coordinates as value
    mappingCoordinates = dict(zip(sceneList, lonLatList)) ## With lon as value[0] and lat as value[1]
    return sceneList, mappingCoordinates ##    

#sceneList = ['bridgeScene', 'weddingScene', 'barScene']

def findMovie():
    sparql = SPARQLWrapper("http://192.168.0.160:7200/repositories/projectTest")    
    sparql.setQuery("""
        PREFIX ex: <http://example.com/projectkand/>
        select ?title where { 
            ?movie a ex:Movie;
                ex:HasPrimaryTitle ?title  
    } limit 100 
    """ )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    movieList = []
    for result in results["results"]["bindings"]:
        movieList.append(result["title"]["value"])   
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    return movieList
    
##########################################################################################################################   

st.title("Movie location finder")
st.text("So that you can fall into the same vulcano as Gollum")

## Multiple search options
searchMode = st.radio("What do you want to search?", options=["Movies", "Actors", "Locations"])

## User selects his favorite movie/actor/whatever
if searchMode == 'Movies':
    movieList = findMovie()
    inputMovie = st.selectbox("Select your favorite movie", movieList)
    if inputMovie != '': ## If movie is selected, render the scene selectbox
        sceneList, mappingCoordinates = findScene(inputMovie)
        inputScene = st.selectbox('Select your scene', sceneList, index=0)
        if inputScene != '': ##if scene is selected, render the button to call the folium map
            for key, value in mappingCoordinates.items():
                if key == inputScene:
                    coordinates = [value[0], value[1]]
            m2 = folium.Map(location=coordinates, zoom_start=16)
            folium.Marker(coordinates, popup='test', tooltip='test').add_to(m2)
            if st.button('test!'):
                folium_static(m2)



## searchMode actor and location don't use our own ontology yet and are kinda oudated.

if searchMode == 'Actors':    
    inputActor = st.selectbox("Select your favorite Actor", actorList, index=0)
if searchMode == 'Locations':    
    inputLocation = st.selectbox("Select your location", locationList)
## These coordinates should come from querying our own ontology
## With the query being based on the user's selection ofcourse
tempCoordinates = [[37.8770  , -4.7784 ], [37.8758, -4.7790]]
tooltip = ['This should be a bridge', 'this should be a castle']
popup = ["it's the bridge from GOT!", "it's a random castle!"]
m = folium.Map(location=tempCoordinates[0], zoom_start=16)

## Add all the coordinates, tooltips etc to the map
i = 0
while i < len(tempCoordinates):
    folium.Marker(tempCoordinates[i], popup=popup[i], tooltip=tooltip[i]).add_to(m)
    i +=1

## Load the map when the button is clicked
if st.button('find Location!'):
    folium_static(m)
