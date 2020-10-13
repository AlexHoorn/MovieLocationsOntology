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


# Remove chars from director map
file = os.getcwd() + "/converted_data/director_map.xlsx"
df = pd.read_excel(file)

df["nconst"] = df["nconst"].apply(RemoveChars)

df.to_excel(file)

# Rename Short in genre map, to avoid naming conflict
file = os.getcwd() + "/converted_data/genre_map.xlsx"
df = pd.read_excel(file)

df["genre"] = df["genre"].replace(["Short"], "Short (genre)")

df.to_excel(file)
