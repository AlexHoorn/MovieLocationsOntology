from rdflib import RDF, RDFS, Graph, Namespace

print("Loading graph")
g = Graph().parse("PopulatedOntology_Old.ttl", format="ttl")
ML = Namespace("http://example.com/movieLocations/")

count = 0
for Class in [ML.Show, ML.Scene, ML.Location, ML.Character, ML.Person]:
    print(f"Removing rdf:type statements for {Class.toPython()}")
    for sub in g.subjects(RDF.type, Class):
        g.remove((sub, RDF.type, Class))
        count += 1
print(f"Removed {count} statements")

count = 0
for Pred in [ML.hasSceneName, ML.hasFullName, ML.hasPrimaryTitle]:
    print(f"Changing statements with {Pred.toPython()} to rdfs:label")
    for sub, obj in g.subject_objects(Pred):
        g.add((sub, RDFS.label, obj))
        g.remove((sub, Pred, obj))
        count += 1

    g.remove((Pred, None, None))
    print(f"Removed {Pred.toPython()}")
print(f"Changed {count} statements")

print("Saving graph")
g.serialize("PopulatedOntology.ttl", format="ttl")
print("Completed")
