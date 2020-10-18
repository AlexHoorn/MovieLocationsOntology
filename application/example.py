import streamlit as st

from components import load_ontology, query_to_pandas

st.title("Example")
st.write("A quick example to show how the functions from `components` work.")

with st.spinner("Loading ontology, this could take some time the first run"):
    # Loads the ontology, the output of this gets cached, returns a Graph
    g = load_ontology("../ontology/PopulatedOntology.owl")

default_query = (
    "SELECT * WHERE {?actor rdf:type ml:Actor; ml:hasFullName ?name} LIMIT 100"
)
query = st.text_area("Query", default_query)

if query != "":
    # query_to_pandas takes a Graph and a query string and gives a Pandas DataFrame back
    st.write(query_to_pandas(g, query))

st.button("Reload")
