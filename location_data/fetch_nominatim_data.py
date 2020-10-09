from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
import pandas as pd
import os
import random
import string
import time
import sys
from tqdm import tqdm

# I assigned a number to everybody
# SETH: 1, RAMON: 2, ALEX: 3, DAVEY: 4
############################################################################
yourPartNr = input(
    "Please enter the number of your part. See the top of the code of the page ")
############################################################################


# CODE, NO NEED TO TEACH ANYTHING HERE ANYMORE
############################################################################

# Variables
############################################################################
# Track HTTP Errors
numHTTPErrors = 0

# Construct directory paths for your part
readDir = os.getcwd()+"/location_data/raw_data/raw_data_part_" + \
    str(yourPartNr) + "/"
writeDir = os.getcwd()+"/location_data/raw_data_geocoded/geocoded_data_part_" + \
    str(yourPartNr) + "/"

# Some helper functions
############################################################################


def GetRandomString(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def TryGeocode(df, attempts=5, sleep=20):
    global numHTTPErrors
    try:
        if numHTTPErrors > 1:
            print("Attempt {}: trying to geocode")
        # Try to get geocded location for the location column of this df
        df['geocodedLocation'] = df['Location'].progress_apply(geocode)

        # If succesfull we can start with a clean slate and forget previous http errors.
        numHTTPErrors = 0
    except Exception:
        # Terminate after 5 consecutive failed attempts
        if numHTTPErrors == attempts:
            print("5 failed attempts. Program will save the current progress and terminate. Try to rerun the script later. It will continue with the current progress.")
            sys.exit()

        # If it's < 5 failed attempts just sleep for a while and retry.
        else:
            print(
                "GEOCODING RETURNS EXCEPTION. WILL SLEEP FOR {} SECONDS AND RETRY.".format(sleep))
            SleepAndRetry(sleep, df)


def SleepAndRetry(sleep, df):
    global numHTTPErrors
    # If it's < 5 failed attempts just sleep for a while and retry.

    # Log the sleeping nicely
    for i in range(sleep, 0, -1):
        print("Retrying in {} seconds...".format(i))
        time.sleep(1)
    numHTTPErrors += 1
    TryGeocode(df, attempts=5, sleep=20)


# Actual program
############################################################################
# Set up the geocoder and rate limiter
userName = GetRandomString(8)+str(yourPartNr)
geolocator = Nominatim(user_agent=userName)
geocode = RateLimiter(geolocator.geocode,
                      min_delay_seconds=1.05, swallow_exceptions=True)

# Allow for seeing pandas progress
tqdm.pandas()

# Doublecheck that everybody scans the right part
if int(yourPartNr) == 1:
    v = input("Please press any button to confirm that you're Seth")
if int(yourPartNr) == 2:
    v = input("Please press any button to confirm that you're Ramon")
if int(yourPartNr) == 3:
    v = input("Please press any button to confirm that you're Alex")
if int(yourPartNr) == 4:
    v = input("Please press any button to confirm that you're Davey")


# Initial start statement
print("\n Starting nominatim requests with generated username: {}.\n Path of read directory: {}.\n Path of write directory: {}\n".format(
    userName, readDir, writeDir))


# For each file in the "data/" directory
for file in os.listdir(readDir):
    # Only process file if it was not processed already
    writeFilePath = writeDir + "geocoded_" + str(file)

    if not os.path.isfile(writeFilePath) and file.__contains__(".csv"):

        # Open file as a dataframe
        print("Processing file:", file)
        df = pd.read_csv(readDir + file)

        # Geocode location values of dataframe
        TryGeocode(df)
        df['latitude'] = df['geocodedLocation'].apply(
            lambda loc: loc.point[0] if loc else None)
        df['longitude'] = df['geocodedLocation'].apply(
            lambda loc: loc.point[1] if loc else None)

        # Save CSV as geocoded raw data
        df.to_csv(writeFilePath)


print(df)
