from bs4 import BeautifulSoup as bs
import requests
import csv
import time
import os
import pandas as pd
from tqdm import tqdm

#/Users/sethvanderbijl/Coding Projects/group51-kdd/location_data/raw_data/RomanceMovieLocations1000-1500_appendix.csv
#/Users/sethvanderbijl/Coding Projects/group51-kdd/location_data/raw_data/raw_data_part_1/BiographyMovieLocations500-1000.csv
#NEEDS A CHECK

def GetLocationDiv(tconst, tries):
    if tconst == "Code":
        return None
    if tries == 2:
        return None
    # Go to the locations page of the movie
    try:
        newLink = "https://www.imdb.com" + tconst + "locations"
        newPage = requests.get(newLink)
    except Exception:
        print(Exception)
        print("Sleeping for 30 secs and trying again")
        print("link:", newLink)
        print("trying {} more times".format(1-tries))
        time.sleep(30)
        tries+=1
        if tries == 2:
            return None
        return GetLocationDiv(tconst, tries)


    newSoup = bs(newPage.text, "html.parser")

    # Get the element from the HTML holding the locations
    locationHolder = newSoup.find(id="filming_locations")
    return locationHolder

def Strip(input):
    return str(input).strip()

def WriteLocationData(locationElement, writer, tconst, df):
    #Get all the locations we already have, qwe don't want to nominatim it all again
    showRows = df.loc[df['Code'] == tconst]
    
    # Actual location description
    location = locationElement.find("a").text.replace("\n", "", 999).strip()

    # Scene description
    scene = locationElement.find("dd").text.replace("\n", "", 999).strip()

    #Get rows with same show and location
    rows = showRows[showRows.Location == location]

    #Get rows where also scene is the same
    if scene != "":
        rows = rows[rows.Scene == scene]

    
    #Check if we already have this data
    # if not rows.empty:
        # print('DUPLICATE DATA, SKIPPING:', rows, "\n")
        # print("Rows for title: \n",showRows, "\n matching rows: ", rows, "\n Searching for location: ", location, "\n Searching for scene: ", scene, "\n")

    if rows.empty:
        writer.writerow(
            [
                tconst,
                location.replace("\n", "", 999),
                scene.replace("\n", "", 999),
            ]
        )

# Construct directory paths for your part
readDir = os.getcwd() + "/location_data/raw_data/"
writeDir = (
    os.getcwd()
    + "/location_data/raw_data/"
)
print("read:", readDir)

#Track file-indices
fileIndex=0

# For each file in the "data/" directory
for subdirs, dirs, files in os.walk(readDir):
    # Track file
    for file in files:

        #Write file to raw_data general directory, append filename with appendix, indicating missed locations
        writeFilePath = writeDir + file.replace(".csv", "") + "_appendix.csv"

        #Skip if aleady loaded
        if os.path.isfile(writeFilePath):
            print("Already exists, skipping: ",writeFilePath)

        #Only if the file was not processed yet
        if not os.path.isfile(writeFilePath):
            #Only if file is a csv and also we don't want to scan the newly generated files in an endless loop
            if file.__contains__(".csv") and subdirs.__contains__("part"):
            
                #Initiliaze to write new csv
                with open(writeFilePath, "a", newline="") as writeCSV:
                    writer = csv.writer(writeCSV)
                    writer.writerow(["Code", "Show Name", "Location", "Scene"])

                    #Construct read path
                    readFilePath = os.path.join(subdirs + "/" + file)

                    #Keep track of the proces
                    print(fileIndex, "Processing file: ", file)
                    
                    #Reading from
                    print("Reading from: ", readFilePath)

                    #Write file to raw_data general directory, append filename with appendix, indicating missed locations
                    print("Writing to: ", writeFilePath, "\n")

                    #open with pandas
                    df = pd.read_csv(readFilePath)
                    df = df[1:]

                    #Preprocess so values are recognized
                    df["Location"] = df["Location"].apply(Strip)
                    df["Scene"] = df["Scene"].apply(Strip)

                    #Get a list of all unique ttvalues
                    movieTitles = df.Code.unique()

                    #Loop through every movie in this raw data file
                    for tconst in tqdm(movieTitles):

                        #And now get the location page for this movie
                        # Go to the location webpage of the movie and the div holding the locations
                        locationDiv = GetLocationDiv(tconst, 0)

                        # Get all locations from this locations div
                        if locationDiv is not None:
                            locationElements = locationDiv.find_all(class_="soda sodavote odd")
                            locationElements += locationDiv.find_all(class_="soda sodavote even")

                            for locationElement in locationElements:
                                # Actual location description
                                WriteLocationData(locationElement, writer, tconst, df)


                    #Track indices of files
                    fileIndex+=1
