from rdflib import RDF, RDFS, Graph, Namespace, URIRef
import pandas as pd

print("Loading Wikidata mappings")
# Load our wikidat mappings
df = pd.read_csv("data/location_data/converted_data/zenodo_data.csv")

# Drop items without wikidata mapping
df = df[df["wikidata_entity"].notna()]


# Only keep necesaary columns and turn these into a dictionary
resource_map = dict(zip(df.tconst, df.wikidata_entity))


print("Loading graph")
g = Graph().parse("ontology/PopulatedOntology.ttl", format="ttl")
ML = Namespace("http://example.com/movieLocations/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")

count = 0


# Since everything is inferred we dont know what a show is.
# Luckily only shows have the property isAdult
# Loop trhough subjects with isAdult as relation
for sub in g.subjects(ML.isAdult, None):
    # If we have wikidata resource for this subject
    if sub.replace("http://example.com/movieLocations/", "") in resource_map:
        print(
            sub,
            OWL.sameAs,
            resource_map[sub.replace("http://example.com/movieLocations/", "")],
        )
        # Then add a new triple stating that this is owl_samAs
        g.add(
            (
                sub,
                OWL.sameAs,
                URIRef(
                    resource_map[sub.replace("http://example.com/movieLocations/", "")]
                ),
            )
        )


print("Saving graph")
g.serialize("ontology/PopulatedOntology.ttl", format="ttl")
print("Completed")
