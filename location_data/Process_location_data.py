import pandas as pd
import os
import pandas as pd
import usaddress

# Some functions for cleaning and processing the data


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


def GetCity(input):
    return GetKeyByValue(usaddress.parse(input), "PlaceName")


def GetState(input):
    return GetKeyByValue(usaddress.parse(input), "StateName")


def GetStreet(input):
    return GetKeyByValue(usaddress.parse(input), "StreetName") + " " + GetKeyByValue(usaddress.parse(input), "StreetNamePostType")


def GetNumber(input):
    return GetKeyByValue(usaddress.parse(input), "AddressNumber")


def GetBuildingName(input):
    return GetKeyByValue(usaddress.parse(input), "BuildingName")


def GetLocationName(input):
    return GetKeyByValue(usaddress.parse(input), "Recipient")


##########################################################################################################################

frames = []
index = 0

# For each file in the "data/" directory
for file in os.listdir("Data/"):
    # Load CSV
    print("Processing file:", str(index))
    loadedCSV = pd.read_csv("Data/"+file)

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

    # Parse location values
    loadedCSV["City"] = loadedCSV["Location"].apply(GetCity)
    loadedCSV["State"] = loadedCSV["Location"].apply(GetState)
    loadedCSV["StreetName"] = loadedCSV["Location"].apply(GetStreet)
    loadedCSV["AddressNumber"] = loadedCSV["Location"].apply(GetNumber)
    loadedCSV["BuildingName"] = loadedCSV["Location"].apply(
        GetBuildingName)
    loadedCSV["LocationName"] = loadedCSV["Location"].apply(
        GetLocationName)

    # Append dataframe without its header
    frames.append(loadedCSV[1:])

    # Add to index to get overview of processing stage
    index += 1

# Merge all df's
merged = pd.concat(frames)
print(merged)

# Export to excel
merged.to_excel("merged.xlsx")

# And CSV for Debugging why the file is broken
merged.to_csv("merged.csv")
