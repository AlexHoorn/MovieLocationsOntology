from bs4 import BeautifulSoup as bs
import requests
import csv
import time
import os
import pandas as pd

def GetLocationDiv(tconst):
    # Go to the locations page of the movie
    newLink = "https://www.imdb.com" + tconst + "locations"
    newPage = requests.get(newLink)
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

    print("Rows for title: \n",showRows, "\n matching rows: ", rows, "\n Searching for location: ", location, "\n Searching for scene: ", scene, "\n")
    
    #Check if we already have this data
    if(rows.shape[0] > 0):
        print('already in there')

    else:
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

        #Only if the file was not processed yet
        # if not os.path.isfile(writeFilePath):
        #Only if file is a csv and also we don't want to scan the newly generated files in an endless loop
        if file.__contains__(".csv") and subdirs.__contains__("part"):
        
            #Initiliaze to write new csv
            with open(writeFilePath, "a", newline="") as writeCSV:
                writer = csv.writer(writeCSV)
                writer.writerow(["Code", "Show Name", "Location", "Scene"])
            
                #Keep track of the proces
                print(fileIndex, "Processing file: ", file, "\n")
                
                #Write file to raw_data general directory, append filename with appendix, indicating missed locations
                print("Writing to: ", writeFilePath, "\n")

                #Construct read path
                readFilePath = os.path.join(subdirs + "/" + file)

                #open with pandas
                df = pd.read_csv(readFilePath)
                print(df)

                #Preprocess so values are recognized
                df["Location"] = df["Location"].apply(Strip)
                df["Scene"] = df["Scene"].apply(Strip)

                #Get a list of all unique ttvalues
                movieTitles = df.Code.unique()

                #Loop through every movie in this raw data file
                for tconst in movieTitles:
                    print(tconst)

                    #And now get the location page for this movie
                    # Go to the location webpage of the movie and the div holding the locations
                    locationDiv = GetLocationDiv(tconst)

                    # Get all locations from this locations div
                    if locationDiv is not None:
                        locationElements = locationDiv.find_all(class_="soda sodavote odd")
                        locationElements += locationDiv.find_all(class_="soda sodavote even")

                        for locationElement in locationElements:
                            # Actual location description
                            WriteLocationData(locationElement, writer, tconst, df)


                #Track indices of files
                fileIndex+=1
