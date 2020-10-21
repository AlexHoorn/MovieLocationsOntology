import os
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

#Quickly testing out some methods to do OWL:sameAs for our items
#50000 movies / 150 unions per query = 333 queries
#333 queries times 10 seconds sleep is 3333 seconds
#3333 seconds is just one hour
#Awesome, will implement tomorrow



sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

#Get triples
def GetTriple(imdbID):
    return """UNION { ?page wdt:P345 '"""+ imdbID +"""' } """

def GetQuery(imdbIDList):
    query = """PREFIX wdt:<http://www.wikidata.org/prop/direct/> SELECT ?page WHERE { { ?page wdt:P345 'tt1528406' }"""
    for id in imdbIDList.iteritems():
        query+=GetTriple(id[1])
    query+= """ } """
    return query

#Method one: sent query with massive UNION, this works for 150 items per time otherwise we get HTTP error "uri to long"
def GetWikiDataResource(query):
    sparql.setQuery(
            query
        )

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

readDir = os.getcwd() + "/allmerged.csv"

df = pd.read_csv(readDir)

df = df["tconst"].drop_duplicates()

dfTop = df[:150]

query = GetQuery(dfTop)

print(query)

results = GetWikiDataResource(query)

# Print the results
for result in results:
    print(result["page"]["value"])




#Method 2 request the wikidata page for each imdb:id, gets a HTTP429 for too many requests after five requests. Rate limiting is going to take days again.
# def GetWikiDataResource(imdbID):
#     sparql.setQuery(
#             """PREFIX wdt:<http://www.wikidata.org/prop/direct/> SELECT ?page WHERE { ?page wdt:P345 '"""+ imdbID +"""' } LIMIT 1 """
#         )

#     sparql.setReturnFormat(JSON)
#     results = sparql.query().convert()
#     print(results["results"])
#     print(results["results"]["bindings"])
#     print(results["results"]["bindings"][0])
#     return "https://www.wikidata.org/wiki/" + str(results["results"]["bindings"][0]["page"]["value"])

# readDir = os.getcwd() + "/allmerged.csv"

# df = pd.read_csv(readDir)

# df = df["tconst"].drop_duplicates()


# for row in df.iteritems():
#     print (GetWikiDataResource(row[1]))
