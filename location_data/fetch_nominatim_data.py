from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
import pandas as pd
import os
import random
import string
import time

# WORK IN PROGRESS

# PLEASE ENTER THE NR. OF THE PART YOU WILL FETCH HERE
# ALEX: 1, RAMON: 2, DAVEY:3, SETH:4
############################################################################
yourPartNr = 1
############################################################################


# CODE, NO NEED TO TEACH ANYTHING HERE ANYMORE
############################################################################

# Some helper functions
############################################################################
def GetRandomString(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)

# Actual program
############################################################################


# Set up the geocoder and rate limiter
userName = GetRandomString(8)+str(yourPartNr)
geolocator = Nominatim(user_agent=userName)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.05)

# Construct directory paths for your part
readDir = "raw_data/raw_data_part_" + str(yourPartNr)
writeDir = "raw_data_geocoded/geocoded_data_part_" + str(yourPartNr)

# Track HTTP Errors
numHTTPErrors = 0
numAttempts = 0

# For each file in the "data/" directory


def TryGeocode(df, attempts=10, sleep=10):
    try:
        df['geocodedLocation'] = df['Location'].apply(geocode)
    except Exception:
        print(
            "GEOCODING RETURNS EXCEPTION. WILL SLEEP FOR {sleep} SECONDS AND RETRY.")
        print(Exception)
        time.sleep(sleep)
        TryGeocode(df, attempts=10, sleep=10)


for file in os.listdir(readDir):

    # Open file as a dataframe
    print("Processing file:", file)
    df = pd.read_csv("Data/"+file)

    # Geocode location values of dataframe

    TryGeocode(df, )

    df['latitutde'] = df['geocodedLocation'].apply(
        lambda loc: loc.point[0] if loc else None)
    df['longitude'] = df['geocodedLocation'].apply(
        lambda loc: loc.point[1] if loc else None)

    # Save CSV as geocoded raw data
    df.to_csv("geocoded_" + str(file))


print(df)
