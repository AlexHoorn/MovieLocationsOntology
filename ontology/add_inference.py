# %%
from owlready2 import get_ontology, sync_reasoner

filename = "PopulatedOntology"
onto = get_ontology(f"{filename}.owl").load()
with onto:
    sync_reasoner()

onto.save(f"{filename}_Inferred.owl")
