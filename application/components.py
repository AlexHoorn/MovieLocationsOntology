from configparser import ConfigParser
from io import StringIO
from os import getcwd
from os.path import isfile

import pandas as pd
from SPARQLWrapper import CSV, SPARQLWrapper


class WrongOntologyError(Exception):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            msg="The wrong ontology file seems to be loaded, please load `PopulatedOntology_Reasoned.owl`.",
            *args,
            **kwargs,
        )


class WrongRulesetError(Exception):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            msg="The wrong ruleset seems to be enabled, please use `OWL2-RL`.",
            *args,
            **kwargs,
        )


def get_config_path():
    return getcwd() + "/config.ini"


def overwrite_config(config: ConfigParser):
    config_path = get_config_path()

    with open(config_path, "w+") as configfile:
        config.write(configfile)


def get_config() -> ConfigParser:
    config_path = get_config_path()
    config = ConfigParser()

    if not isfile(config_path):
        config["Configuration"] = {"Endpoint": ""}
        overwrite_config(config)

    config.read(config_path)

    return config


def query_to_pandas(sparql: SPARQLWrapper, query: str) -> pd.DataFrame:
    prefixes = {"ml": "http://example.com/movieLocations/"}
    for prefix, value in prefixes.items():
        query = f"PREFIX {prefix}: <{value}> {query}"

    sparql.setReturnFormat(CSV)
    sparql.setQuery(query)

    result = sparql.query().convert()
    csv = StringIO(result.decode())
    df = pd.read_csv(csv)

    return df


def verify_endpoint(endpoint: str):
    sparql = SPARQLWrapper(endpoint)
    sparql.setTimeout(5)

    try:
        actors = query_to_pandas(
            sparql, "SELECT * WHERE {?actor rdf:type ml:Actor} LIMIT 5"
        )
        if not len(actors) > 0:
            raise WrongOntologyError()

        plays_in = query_to_pandas(
            sparql, "SELECT * WHERE {?actor ml:playsIn ?show} LIMIT 5"
        )
        if not len(plays_in) > 0:
            raise WrongRulesetError()

    except Exception as e:
        raise e
