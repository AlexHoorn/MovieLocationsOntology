import pandas as pd
import os


def RemoveChars(input):
    return (
        str(input)
        .replace('"', "")
        .replace("'", "")
        .replace("{", "")
        .replace("}", "")
        .replace("[", "")
        .replace("]", "")
        .replace(".", "")
        .replace("\\N", "")
        .replace("\\n", "")
    )


def Capitalize(input):
    return str(input).capitalize()


# Remove chars from director map
def RemoveCharsFromDirectorMap():
    file = os.getcwd() + "/converted_data/director_map.xlsx"
    df = pd.read_excel(file)

    df["nconst"] = df["nconst"].apply(RemoveChars)

    df.to_excel(file, index=False)


# Rename Short in genre map, to avoid naming conflict
def RenameShortInGenreMap():
    file = os.getcwd() + "/converted_data/genre_map.xlsx"
    df = pd.read_excel(file)

    df["genre"] = df["genre"].replace(["Short"], "Short (genre)")

    df.to_excel(file, index=False)


# Uppercase the titleTypes
def UppercaseShowTitles():
    file = os.getcwd() + "/converted_data/show.xlsx"
    df = pd.read_excel(file)

    df["titleType"] = df["titleType"].apply(Capitalize)

    df.to_excel(file, index=False)


RemoveCharsFromDirectorMap()
RenameShortInGenreMap()
UppercaseShowTitles()
