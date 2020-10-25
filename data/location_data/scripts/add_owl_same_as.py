import os
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import time
from tqdm import tqdm
import pickle

########################################################################
# VARIABLES
dictDir = os.getcwd() + "data/location_data/raw_data/owl_dicts/"
readDir = os.getcwd() + "data/location_data/converted_data/allmerged.csv"

df = pd.read_csv(readDir)

tconsts = df["tconst"].drop_duplicates()

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

############################################################
# HELPER FUNCTIONS

# Get triples for a title to construct a larger query from
def GetTriple(imdbID):
    return """UNION { ?page wdt:P345 '""" + imdbID + """' .  ?page wdt:P345 ?title } """


# Save dict obj
def save_obj(obj, name):
    with open(name + ".pkl", "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


# Load dict obj
def load_obj(name):
    with open(name, "rb") as f:
        return pickle.load(f)


# Construct query for series of tconsts
def GetQuery(imdbIDList):
    # Start of the query
    query = """PREFIX wdt:<http://www.wikidata.org/prop/direct/> SELECT ?title ?page WHERE { {  ?page wdt:P345 'tt1528406'. ?page wdt:P345 ?title }"""
    # The unioned triples in the midpart
    for id in imdbIDList.iteritems():
        query += GetTriple(id[1])
    # The end of the query
    query += """ } """
    return query


# Sent the constructed query to wikidata and return the results
def GetWikiDataResource(query):
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]


########################################################################
# PROGRAM


def TryGetOwlPages(rangeNrs, sleep, currentDict):
    # Check if this file was not already queried
    if not os.path.isfile(dictDir + "dict" + str(rangeNrs) + ".pkl"):
        # Select a series of 80 items from the show titles
        section = tconsts[rangeNrs : rangeNrs + 80]

        # Create a query from this selection
        query = GetQuery(section)

        # Without counterevidence the operationw ill assume to have succeeded
        succeed = True

        # Try to query the query to wikidata's sparql endpoint
        try:
            results = GetWikiDataResource(query)
            # On succes default the sleep time again
            sleep = 20
        # If this does not work sleep and try again
        except Exception as ex:
            # Inform of failure and sleep
            print(ex)
            print("TRYING AGAIN")
            time.sleep(sleep)

            # Do not write values of a failed attempt to a dict
            succeed = False

            # Retry with a sleep increment
            TryGetOwlPages(rangeNrs, sleep + 20, currentDict)

        # I do not want this to get executed after a retry
        if succeed:
            # Save results in a dict

            # Assign results to a dict
            for result in results:
                currentDict[result["title"]["value"]] = result["page"]["value"]

            # Print the dictionary to check if its right
            print(currentDict)
            save_obj(currentDict, dictDir + "dict" + str(rangeNrs))
        return True
    else:
        # Return false if this file already existed so nothing was queried and no sleep is needed
        return False


# Select a section from the data and query it
for rangeNrs in tqdm(range(0, len(tconsts), 80)):
    # If we can get some pages sleep, if we already querid this, skip this data and don't sleep
    if TryGetOwlPages(rangeNrs, 20, {}):
        # Always sleep to give wikidata some rest
        time.sleep(20)


# Merge all dictionaries
superDict = {}
for file in os.listdir(dictDir):
    subdict = load_obj(dictDir + file)
    superDict.update(subdict)

# Map all values of this super_dictionary to a new column called wikidata_entry
df["wikidata_entry"] = df["tconst"].map(superDict)

# Print the number of movies for which no wikidata entry was found
print(
    "For some movies no wikidata entry was found\n",
    "Sum of missing values: ",
    df["wikidata_entry"].isna().sum(),
)

# save the progress as zenodo data
df.to_csv(readDir.replace("allmerged.csv", "zenodo_data.csv"))
