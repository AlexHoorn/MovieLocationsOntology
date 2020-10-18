from _thread import RLock
from io import StringIO
from sqlite3 import Connection
from weakref import KeyedRef

import pandas as pd
import streamlit as st
from owlready2 import Ontology, World, sync_reasoner
from rdflib import Graph, Namespace


@st.cache(
    hash_funcs={
        Ontology: lambda _: None,
        KeyedRef: lambda _: None,
        Connection: lambda _: None,
        RLock: lambda _: None,
    }
)
def load_ontology(filepath: str) -> Graph:
    """Loads the ontology and runs the reasoner.

    Args:
        filepath (str): filepath to the ontology

    Returns:
        Graph: rdflib.Graph object
    """
    ontology_world = World(filename=f"{filepath}.sqlite3")
    ontology = ontology_world.get_ontology(filepath).load(reload_if_newer=True)
    sync_reasoner(ontology_world)

    g = ontology_world.as_rdflib_graph()
    g.bind("ml", Namespace("http://example.com/movieLocations/"))

    return g


def query_to_pandas(g: Graph, query: str) -> pd.DataFrame:
    """Queries a graph object

    Args:
        g (Graph): rdflib.Graph object
        query (str): Query in SparQL

    Returns:
        pd.DataFrame: A pandas DataFrame with results
    """
    res = g.query(query)
    csv = StringIO(res.serialize(format="csv").decode())
    df = pd.read_csv(csv)

    return df
