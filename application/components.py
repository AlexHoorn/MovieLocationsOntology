from configparser import ConfigParser
from io import StringIO
from os import getcwd
from os.path import isfile

import pandas as pd
from SPARQLWrapper import CSV, SPARQLWrapper


class WrongRulesetError(Exception):
    pass


def get_config_path() -> str:
    """Gets the path to the config file

    Returns:
        str: Path to config file
    """
    return getcwd() + "/config.ini"


def overwrite_config(config: ConfigParser):
    """Overwrites the config file, whether it exists or not

    Args:
        config (ConfigParser): ConfigParser config object to write
    """    
    config_path = get_config_path()

    with open(config_path, "w+") as configfile:
        config.write(configfile)


def get_config() -> ConfigParser:
    """Gets the config

    Returns:
        ConfigParser: ConfigParser config object
    """    
    config_path = get_config_path()
    config = ConfigParser()

    if not isfile(config_path):
        config["Configuration"] = {"Endpoint": ""}
        overwrite_config(config)

    config.read(config_path)

    return config


def query_to_pandas(sparql: SPARQLWrapper, query: str) -> pd.DataFrame:
    """Queries the SPARQL endpoint and return a Pandas DataFrame

    Args:
        sparql (SPARQLWrapper): Initiated SPARQLWrapper object with endpoint set
        query (str): The SPARQL query

    Returns:
        pd.DataFrame: A Pandas DataFrame of the results
    """    
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
    """Verifies whether the Movie Locations endpoint is properly set

    Args:
        endpoint (str): Endpoint URL

    Raises:
        WrongRulesetError: Gets raised when the wrong inference ruleset is selected
        e: Any other exception that might occur
    """    
    sparql = SPARQLWrapper(endpoint)
    sparql.setTimeout(5)

    try:
        actors = query_to_pandas(
            sparql, "SELECT * WHERE {?actor rdf:type ml:Actor} LIMIT 5"
        )
        plays_in = query_to_pandas(
            sparql, "SELECT * WHERE {?actor ml:playsIn ?show} LIMIT 5"
        )

        if not len(plays_in) > 0 or not len(actors) > 0:
            raise WrongRulesetError(
                "The wrong inference rules are used, please use `OWL2-RL`."
            )

    except Exception as e:
        raise e


def generate_filter_string(filter_on: str, filter_vars: list) -> str:
    """Generates a SPARQL filter

    Args:
        filter_on (str): What the filter should be applied to, e.g. "title"
        filter_vars (list): The (multiple) variables that should be used in the filter

    Returns:
        str: SPARQL FILTER() string
    """    
    vars_prefixed = [f"?{filter_on} = '{x}'" for x in filter_vars]
    vars_joined = " || ".join(vars_prefixed)
    filter_string = f"FILTER({vars_joined})"

    return filter_string
