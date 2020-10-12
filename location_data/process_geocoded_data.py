import pandas as pd
import os

# UNFINISHED


def GetKeyByValue(myDict, myValue):
    for key, val in myDict:
        if val == myValue:
            return key
    return ""


def RemoveSpace(input):
    return str(input).strip().replace("\n", "")


def CleanTitle(input):
    return input.replace("/title/", "").replace("/", "")


def MakeNANsEmpty(input):
    if input.lower() == "nan":
        return ""
    return input


##########################################################################################################################
frames = []
fileIndex = 0

dir = os.getcwd() + "/location_data/raw_data_geocoded/"
print(dir)
for subdirs, dirs, files in os.walk(dir):
    #Track file
    for file in files:
        print(fileIndex, "Processing file:", file, "\n")
        fileIndex += 1
        
        #Load CSV
        loadedCSV = pd.read_csv(os.path.join(subdirs +"/" +file))

        

        # # Make Nan values empty strings
        # loadedCSV["Scene"] = loadedCSV["Scene"].apply(MakeNANsEmpty)

        #Append dataframe without its header
        frames.append(loadedCSV[1:])

#General
##########################################
# Merge all df's
merged = pd.concat(frames)

#Drop index columns
merged.drop(merged.columns[[0]],axis=1,inplace=True)


#SHOW CODES
##########################################
# Clean tconst
merged["Code"] = merged["Code"].apply(CleanTitle)

#Remove special characters from titles
merged["Code"] = merged["Code"].apply(RemoveSpace)

#Drop rows with column names that accidentally entered dataset
merged.drop(merged.loc[merged['Code']=="Code"].index, inplace=True)

#Rename code to tconst
merged.rename({"Code":"tconst"}, inplace = True, axis="columns")


#SHOW LABELS
##########################################
#Rename column for show label
merged.rename({"Show Name":"tLabel"}, inplace = True, axis="columns")


#SCENES
##########################################
#Remove special characters from scenes
merged["Scene"] = merged["Scene"].apply(RemoveSpace)

# Get names for all rows with studios instead of scenes
merged.drop(merged.loc[merged['Scene']=="(studio)"].index, inplace=True)

#Make NAN ""
merged["Scene"] = merged["Scene"].apply(MakeNANsEmpty)


#LOCATIONS
##########################################
#Drop rows for which no location could be geocoded
merged=merged[merged["geocodedLocation"].notnull()]

#Remove specials characters
merged["geocodedLocation"] = merged["geocodedLocation"].apply(RemoveSpace)




print(merged.shape)

# Save
merged.to_csv(os.getcwd()+"/location_data/allmerged.csv")

    