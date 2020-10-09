import pandas as pd
import os

# UNFINISHED


def GetKeyByValue(myDict, myValue):
    for key, val in myDict:
        if val == myValue:
            return key
    return ""


def RemoveSpecialChars(input):
    return " ".join(str(input).split())


def CleanTitle(input):
    return input.replace("/title/", "").replace("/", "")


def MakeNANsEmpty(input):
    if input.lower() == "nan":
        return ""
    return input


##########################################################################################################################
frames = []
index = 0

dir = os.getcwd() + "/raw_data_geocoded/"
for subdirs, dirs, file in os.walk(dir):
    # Load CSV
    print("Processing file:", str(index))
    loadedCSV = pd.read_csv(dir+file)

    # Remove special characters and double spaces
    loadedCSV["Code"] = loadedCSV["Code"].apply(CleanTitle)

    # Remove special characters and double spaces
    loadedCSV["Scene"] = loadedCSV["Scene"].apply(RemoveSpecialChars)

    # Get names for all rows with studios instead of scenes
    indexNames = loadedCSV[loadedCSV['Scene'].str.contains(
        "(studio)", na=False)].index

    # Delete these row indexes from dataFrame
    loadedCSV.drop(indexNames, inplace=True)

    # Make Nan values empty strings
    loadedCSV["Scene"] = loadedCSV["Scene"].apply(MakeNANsEmpty)

    # Append dataframe without its header
    frames.append(loadedCSV[1:])

    # Add to index to get overview of processing stage
    index += 1

    # Merge all df's
    merged = pd.concat(frames)
    print(merged)

    # Export to excel
    merged.to_csv("allmerged.csv")

# Get the merged document and create several maps from this

# First map locations to scenes
showDF = pd.read_csv(os.getcwd()+"allmerged.csv")

# Remove rows with no scenes


# Give each scene a unique id. I would be hard pressed to have multiple scenes with same name but we can't be sure
df['sceneConst'] = df.groupby(['Show','Scene']).ngroup()



