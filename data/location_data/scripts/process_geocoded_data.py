import os

import pandas as pd


# HELPER FUNCTIONS
##########################################
def GetKeyByValue(myDict, myValue):
    for key, val in myDict:
        if val == myValue:
            return key
    return ""


def RemoveIllegalChars(input):
    return (
        str(input)
        .replace('"', "")
        .replace("'", "")
        .replace("{", "")
        .replace("}", "")
        .replace("[", "")
        .replace("]", "")
        .replace(".", "")
    )


def RemoveSpace(input):
    return str(input).strip().replace("\n", "")


def CleanTitle(input):
    return input.replace("/title/", "").replace("/", "")


def MakeNANsEmpty(input):
    if input.lower() == "nan":
        return ""
    return input


row_index = 0


def GiveRowIdentifier(input, tconst, lconst):
    return str(input) + tconst + lconst


index = 0


def GetIdentifier(input, char, unique=True):
    if unique:
        return char + str(input)
    else:
        if input != "":
            global index
            index += 1
            return char + str(index)
        return ""


def RemoveBrackets(input):
    return str(input).replace("(", "").replace(")", "")


# VARIABLES
##########################################
frames = []
fileIndex = 0
index = 0
dir = os.getcwd() + "/data/location_data/raw_data/geocoded_data/"

# PROGRAM
##########################################
for subdirs, dirs, files in os.walk(dir):
    # Track file
    for file in files:
        print(fileIndex, "Processing file:", file, "\n")
        fileIndex += 1

        # Load CSV
        loadedCSV = pd.read_csv(os.path.join(subdirs + "/" + file))

        # Append dataframe without its header
        frames.append(loadedCSV[1:])

# GENERAL
##########################################
# Merge all df's
merged = pd.concat(frames)

# Drop index columns
merged.drop(merged.columns[[0]], axis=1, inplace=True)


# SHOWS
##########################################
# Clean tconst
merged["Code"] = merged["Code"].apply(CleanTitle)

# Remove special characters from titles
merged["Code"] = merged["Code"].apply(RemoveSpace)

# Drop rows with column names that accidentally entered dataset
merged.drop(merged.loc[merged["Code"] == "Code"].index, inplace=True)

# Rename code to tconst
merged.rename({"Code": "tconst"}, inplace=True, axis="columns")

# Rename column for show label
merged.rename({"Show Name": "tLabel"}, inplace=True, axis="columns")

# SCENES
##########################################
# Remove special characters from scenes
merged["Scene"] = merged["Scene"].apply(RemoveSpace)

# Remove brackets
merged["Scene"] = merged["Scene"].apply(RemoveBrackets)

# Get names for all rows with studios instead of scenes
merged.drop(merged.loc[merged["Scene"] == "(studio)"].index, inplace=True)

# Make NAN ""
merged["Scene"] = merged["Scene"].apply(MakeNANsEmpty)

# Give all scenes identifier, same names are different scenes. e.g. multiple movies might have a "school" scene.
merged["sconst"] = merged["Scene"].apply(lambda x: GetIdentifier(x, "s", False))

# Rename scene label
merged.rename({"Scene": "sLabel"}, inplace=True, axis="columns")

# LOCATIONS
##########################################
# Drop rows for which no location could be geocoded
merged = merged[merged["geocodedLocation"].notnull()]

# Give locations a unique lconst
merged = merged.assign(lconst=(merged["geocodedLocation"].astype("category").cat.codes))
merged["lconst"] = merged["lconst"].apply(lambda x: GetIdentifier(x, "l"))

# Remove specials characters
merged["geocodedLocation"] = merged["geocodedLocation"].apply(RemoveSpace)

# Rename lat and long
merged.rename({"latitude": "lat", "longitude": "long"}, inplace=True, axis="columns")

# Rename location label
merged.rename({"geocodedLocation": "lLabel"}, inplace=True, axis="columns")

# Rename original location label
merged.rename({"Location": "lAltLabel"}, inplace=True, axis="columns")

# Finally rearrange the columns
merged = merged[
    [
        "tconst",
        "tLabel",
        "sconst",
        "sLabel",
        "lconst",
        "lLabel",
        "lAltLabel",
        "lat",
        "long",
    ]
]

merged["sLabel"] = merged["sLabel"].apply(RemoveIllegalChars)

print(merged.shape)

# Create a identifier that we can use to match duplicate scenes
merged["rowconst"] = merged["tconst"] + merged["sLabel"] + merged["lconst"]

# Drop duplicate scenes (e.g. same scene name, same location and same movie)
merged = merged.drop_duplicates(subset="rowconst", keep="first")

print(merged.shape)

# Save
merged.to_csv(
    os.getcwd() + "data/location_data/converted_data/allmerged.csv", index=False
)
