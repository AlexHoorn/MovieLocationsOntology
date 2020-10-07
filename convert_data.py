# %% Setup
import pandas as pd

# %%  Load ratings into a dataframe this is later used to add the ratings to the shows
rating = pd.read_csv(
    "raw_data/title.ratings.tsv/data.tsv",
    delimiter="\t",
    index_col=0,
    usecols=["tconst", "averageRating"],
)

# %% Load shows into a dataframe
show = (
    pd.read_csv(
        "raw_data/title.basics.tsv/data.tsv",
        delimiter="\t",
        index_col=0,
        na_values=["\\N"],
        dtype={"startYear": float, "endYear": float},
    )
    # `originalTitle` isn't necessary as `primaryTitle` will be used as label
    .drop("originalTitle", axis=1).assign(
        # Converts `titleType` to category
        titleType=lambda x: pd.Categorical(x["titleType"]),
        # Converts `runtimeMinutes` to float
        runtimeMinutes=lambda x: pd.to_numeric(x["runtimeMinutes"], errors="coerce"),
        # Add ratings
        averageRating=lambda x: x.index.map(rating["averageRating"]),
    )
)

# %% Creates a dataframe that is used to map shows with their **multiple** genres
genre_map = (
    show[["primaryTitle", "genres"]]
    # The genres are denoted by a long string with commas, this converts it to lists
    .assign(genres=lambda x: x["genres"].str.split(","))
    # Create new rows for every item in the lists from the previous step
    .explode("genres").rename(columns={"genres": "genre"})
)

# %% Loads all people into a dataframe
person = (
    pd.read_csv(
        "raw_data/name.basics.tsv/data.tsv",
        delimiter="\t",
        index_col=0,
        na_values=["\\N"],
    )
    # Drop unused columns
    .drop(["primaryProfession", "knownForTitles"], axis=1)
)

# %% Creates a dataframe that is used to map shows with their **multiple** directors
director_map = (
    pd.read_csv(
        "raw_data/title.crew.tsv/data.tsv",
        delimiter="\t",
        index_col=0,
        usecols=["tconst", "directors"],
    )
    .assign(
        # The directors are denoted by a long string with commas, this converts it to lists
        directors=lambda x: x["directors"].str.split(","),
        # Adds the title of the show
        showTitle=lambda x: x.index.map(show["primaryTitle"]),
    )
    # Create new rows for every item in the lists from the previous step
    .explode("directors")
    .rename(columns={"directors": "director"})
    # Add the name of the director
    .assign(directorName=lambda x: x["director"].map(person["primaryName"]))
)

# %% Loads principals to a dataframe, this is used for actors and their characters
actor_terms = ["actor", "actress"]
actor = (
    pd.read_csv(
        "raw_data/title.principals.tsv/data.tsv",
        delimiter="\t",
        na_values=["\\N"],
        nrows=1000,
    )
    .drop(["job"], axis=1)
    .query("category == @actor_terms")
    # TODO
    .fillna("[]")
    .assign(characters=lambda x: x["characters"].apply(lambda x: eval(x)))
    .explode("characters")
    .assign(characterId=lambda x: x["tconst"] + "-c" + x["ordering"].astype(str))
)

# %% Exporting of data - currently only exports a sample
genre_map.head().to_excel("converted_data/genre_map.xlsx")
show.head().drop("genres", axis=1).to_excel("converted_data/show.xlsx")
director_map.head().to_excel("converted_data/director_map.xlsx")

# TODO - Split into actors and characters
actor.head().to_excel("converted_data/actor.xlsx")
