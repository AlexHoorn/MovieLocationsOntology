from bs4 import BeautifulSoup as bs
import requests
import csv
import time
import os
import pandas as pd

def GetLocationDiv(a):
    # Go to the locations page of the movie
    newLink = "https://www.imdb.com" + a["href"] + "locations"
    newPage = requests.get(newLink)
    newSoup = bs(newPage.text, "html.parser")

    # Get the element from the HTML holding the locations
    locationHolder = newSoup.find(id="filming_locations")
    return locationHolder


def WriteLocationData(locationElement, writer, movieElement):
    # Actual location description
    location = locationElement.find("a")

    # Scene description
    scene = locationElement.find("dd")

    # Write tconst code, moviename, location, scene to CSV
    writer.writerow(
        [
            movieElement["href"],
            movieElement.text,
            location.text.replace("\n", "", 999),
            scene.text.replace("\n", "", 999),
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
    #Only if file is a csv
        if file.__contains__(".csv"):
        
            #Initiliaze to write new csv
            # with open(writeFilePath, "a", newline="") as writeCSV:
            #     writer = csv.writer(writeCSV)
            #     writer.writerow(["Code", "Show Name", "Location", "Scene"])
            
            #Keep track of the proces
            print(fileIndex, "Processing file: ", file, "\n")
            
            #Write file to raw_data general directory, append filename with appendix, indicating missed locations
            print("Writing to: ", writeFilePath, "\n")

            #Construct read path
            readFilePath = os.path.join(subdirs + "/" + file)

            #open with pandas
            df = pd.read_csv(readFilePath)
            print(df)

            #Get a list of all unique ttvalues
            movieTitles = df.Code.unique()

            #Loop through every movie in this raw data file
            for tconst in movieTitles:
                print(tconst)

                #Get all the locations we already have, qwe don't want to nominatim it all again
                locationValuesForTitle =  df.loc[df['Code'] == tconst, 'Location']
                print(locationValuesForTitle)

                #And now get the location page for this movie
                # Go to the location webpage of the movie and the div holding the locations
                locationDiv = GetLocationDiv(movieElement)

                # Get all locations from this locations div
                if locationDiv is not None:
                    locationElements = locationDiv.find_all(class_="soda sodavote odd")

                    for locationElement in locationElements:
                        # Actual location description
                        WriteLocationData(locationElement, writer, movieElement)


            #Track indices of files
            fileIndex+=1
