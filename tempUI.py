import streamlit as st
import streamlit.components.v1 as comp
from streamlit_folium import folium_static
import folium
from SPARQLWrapper import SPARQLWrapper, JSON

## Just some temporary queries, this could be ran against our own ontology later on
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?movie ?movieLabel ?actor
    WHERE { 
        ?movie a dbo:Film;
  				rdfs:label ?movieLabel
	    filter(langMatches(lang(?movieLabel),"EN"))
    } LIMIT 10
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
movieList = ['']
for result in results["results"]["bindings"]:
    movieList.append(result["movieLabel"]["value"])

sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX yago: <http://dbpedia.org/class/yago/>
    SELECT  * WHERE { 
    ?actor a yago:Actor109765278;
    rdfs:label ?actorLabel
    FILTER(langMatches(lang(?actorLabel),"EN"))
    } LIMIT 10
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
    } LIMIT 10
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
locationList = ['']
for result in results["results"]["bindings"]:
    locationList.append(result["cityLabel"]["value"])    

sceneList = ['bridgeScene', 'weddingScene', 'barScene']

##########################################################################################################################   

st.title("Movie location finder")
st.text("So that you can fall into the same vulcano as Gollum")

## Multiple search options
searchMode = st.radio("What do you want to search?", options=["Movies", "Actors", "Locations"])

## User selects his favorite movie/actor/whatever
if searchMode == 'Movies':
    inputMovie = st.selectbox("Select your favorite movie", movieList)
    if inputMovie != '':
        inputScene = st.selectbox('select a scene from the movie', sceneList)
if searchMode == 'Actors':    
    inputActor = st.selectbox("Select your favorite Actor", actorList, index=0)
if searchMode == 'Locations':    
    inputLocation = st.selectbox("Select your favorite Actor", locationList)
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
