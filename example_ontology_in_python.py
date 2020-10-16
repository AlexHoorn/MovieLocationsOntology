from io import StringIO

import pandas as pd
from owlready2 import default_world, get_ontology, sync_reasoner_pellet
from rdflib import Graph, Namespace


def load_ontology(filepath: str) -> Graph:
    onto = get_ontology(filepath).load()
    with onto:
        sync_reasoner_pellet()
    g = default_world.as_rdflib_graph()

    return g


def query_to_pandas(g: Graph, query: str) -> pd.DataFrame:
    res = g.query(query)
    csv = StringIO(res.serialize(format="csv").decode())
    df = pd.read_csv(csv)

    return df


g = load_ontology("ontology/MovieOntology.owl")
g.bind("ex", Namespace("http://example.com/projectkand/"))
df = query_to_pandas(
    g,
    """SELECT *
    WHERE {
        ?actor rdf:type ex:Actor
            ;ex:hasFullName ?name;
            ex:bornIn ?year
        }
    LIMIT 10""",
)
