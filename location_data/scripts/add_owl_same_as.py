import os
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import time
from tqdm import tqdm
import pickle

#Quickly testing out some methods to do OWL:sameAs for our items
#50000 movies / 150 unions per query = 333 queries
#333 queries times 10 seconds sleep is 3333 seconds
#3333 seconds is just one hour
#Awesome, will implement tomorrow



sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

#Get triples
def GetTriple(imdbID):
    return """UNION { ?page wdt:P345 '"""+ imdbID +"""' .  ?page wdt:P345 ?title } """

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)

#Construct query for sectioon
def GetQuery(imdbIDList):
    query = """PREFIX wdt:<http://www.wikidata.org/prop/direct/> SELECT ?title ?page WHERE { {  ?page wdt:P345 'tt1528406'. ?page wdt:P345 ?title }"""
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

dictDir = os.getcwd() + "/owl_dicts/"
readDir = os.getcwd() + "/allmerged.csv"

df = pd.read_csv(readDir)

tconsts = df["tconst"].drop_duplicates()





def TryGetOwlPages(rangeNrs, sleep, currentDict):
    if not os.path.isfile(dictDir+"dict" + str(rangeNrs)+ ".pkl"):
        #Select a series of 80 items from the show titles
        section = tconsts[rangeNrs:rangeNrs + 80]

        print(rangeNrs,rangeNrs + 80)

        print(tconsts.shape)


        #Create a query from this selection
        query = GetQuery(section)

        print(section)

        succeed = True
        #Try to query the query to wikidata's sparql endpoint
        try:
            results = GetWikiDataResource(query)
            #On succes default the sleep time again
            sleep = 20
        #If this does not work sleep and try again
        except Exception as ex:
            print(ex)
            print("ERROR TRYING AGAIN")
            time.sleep(sleep)
            #Increment the sleep time and try again
            succeed=False


            TryGetOwlPages(rangeNrs, sleep + 20)

        #I do not want this to get executed after a retry
        if succeed:
            #Save results in a dict

            #Assign results to a dict
            for result in results:
                currentDict[result["title"]["value"]]=result["page"]["value"]

            #Print the dictionary to check if its right
            print(currentDict)
            save_obj(currentDict, dictDir+"dict" + str(rangeNrs))
        return True
    else:
        return False





#Select a section from the data and query it
for rangeNrs in tqdm(range(0, len(tconsts), 80)):
    if TryGetOwlPages(rangeNrs, 20, {}):
        time.sleep(2)


#Later we will map these dictionaries
#Map this dict to the original dat
superDict = {}
for file in os.listdir(dictDir):
    subdict = load_obj(dictDir+file)
    superDict.update(subdict)

df['Owl:SameAs'] = df['tconst'].map(superDict)

print("Sum of missing values: ",df['Owl:SameAs'].isna().sum())

#save the progress
df.to_csv(readDir.replace("allmerged.csv", "zenodo_data.csv"))