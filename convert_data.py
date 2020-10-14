# %% Setup
from ast import literal_eval

import numpy as np
import pandas as pd

# Universal function to load IMDB tsv
def load_dataset(filepath, **kwargs):
    return pd.read_csv(filepath, delimiter="\t", na_values=["\\N"], **kwargs)


# Function to save both a sample and the full dataframe
def save_df(name, **kwargs):
    df = eval(name)
    df.head(10).to_csv(f"converted_data/samples/{name}_sample.csv", **kwargs)
    df.to_excel(f"converted_data/{name}.xlsx", **kwargs)


# Load all codes of shows for which locations are in the dataset
title_filter = (
    pd.read_csv("location_data/allmerged.csv", usecols=["tconst"])
    .drop_duplicates()["tconst"]
    .values
)

# %% Load shows into a dataframe
# Load ratings to add to shows
rating = load_dataset(
    "raw_data/title.ratings.tsv/data.tsv",
    index_col=0,
    usecols=["tconst", "averageRating"],
)

# Load shows
show = (
    load_dataset(
        "raw_data/title.basics.tsv/data.tsv",
        index_col=0,
        dtype={"startYear": float, "endYear": float},
    )
    # `originalTitle` isn't necessary the same as `primaryTitle` will be used as label
    .drop("originalTitle", axis=1)
    # Only keep shows that appear in the filter
    .query("tconst in @title_filter").assign(
        # Converts `titleType` to category and fix capitalization
        titleType=lambda x: pd.Categorical(
            x["titleType"].str[0].str.upper() + x["titleType"].str[1:]
        ),
        # Converts `runtimeMinutes` to float
        runtimeMinutes=lambda x: pd.to_numeric(x["runtimeMinutes"], errors="coerce"),
        # Add ratings
        averageRating=lambda x: x.index.map(rating["averageRating"]),
    )
)

# %% Creates a dataframe that is used to map shows with their **multiple** genres
genre_map = (
    show[["genres"]]
    # The genres are denoted by a long string with commas, this converts it to lists
    .assign(genres=lambda x: x["genres"].str.split(","))
    # Create new rows for every item in the lists from the previous step
    .reset_index().explode("genres")
    # Rename Short to avoid naming conflict with titleType
    .replace("Short", "Short (genre)")
    # Rename column
    .rename(columns={"genres": "genre"})
)

# Drop genres from show dataframe
show.drop("genres", axis=1, inplace=True)

# %% Creates a dataframe that is used to map shows with their **multiple** directors
director_map = (
    load_dataset(
        "raw_data/title.crew.tsv/data.tsv",
        usecols=["tconst", "directors"],
    )
    .dropna()
    # Only keep shows that appear in the filter
    .query("tconst in @title_filter")
    .assign(
        # The directors are denoted by a long string with commas, this converts it to lists
        directors=lambda x: x["directors"].str.split(","),
    )
    # Create new rows for every item in the lists from the previous step
    .explode("directors")
    # Rename column
    .rename(columns={"directors": "nconst"})
)

# %% Loads principals to a dataframe, this is used for actors and their characters
actor_terms = ["actor", "actress"]
actor = (
    load_dataset(
        "raw_data/title.principals.tsv/data.tsv",
    )
    .drop(["job"], axis=1)
    # Only keep actors/actresses and shows in the title filter
    .query("category in @actor_terms and tconst in @title_filter")
    # Fills missing characters otherwise `eval` will raise errors
    .fillna("[]")
    # Converts strings of lists to actual lists
    .assign(characters=lambda x: x["characters"].apply(literal_eval))
    # Converts list of characters to a character per row
    .explode("characters")
    .rename(columns={"characters": "character"})
    # Creates an identifier for each character of a show
    .assign(characterId=lambda x: x["tconst"] + "-c" + x["ordering"].astype(str))
    .drop(["ordering", "category"], axis=1)
)

person_filter = np.append(director_map["nconst"].values, actor["nconst"].values)
# Creates a dataframe with characters for each title and their actor
character = actor.copy().dropna()
# Creates a dataframe for the remaining cases where the character is unknown
actor_map = actor[actor["character"].isnull()].drop(
    ["character", "characterId"], axis=1
)

# %% Loads all people into a dataframe
person = (
    load_dataset(
        "raw_data/name.basics.tsv/data.tsv",
        index_col=0,
    )
    # Drop unused columns
    .drop(["primaryProfession", "knownForTitles"], axis=1)
    # Only keep people from the shows in the dataset
    .query("nconst in @person_filter")
)

# %% Exporting of data
save_df("actor_map", index=False)
save_df("character", index=False)
save_df("director_map", index=False)
save_df("genre_map", index=False)
save_df("person")
save_df("show")

# %%
