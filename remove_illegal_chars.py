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


file = os.getcwd() + "/converted_data/director_map.xlsx"
df = pd.read_excel(file)

df["nconst"] = df["nconst"].apply(RemoveChars)

df.to_excel(file)
