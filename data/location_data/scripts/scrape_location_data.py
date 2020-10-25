import csv
import os
import time

import requests
from bs4 import BeautifulSoup as bs

# Some variables
########################################################################
currentGENRE = ""
previousSaveName = ""
startUrlPart1 = ""
startUrlPart2 = ""


# Helper functions
########################################################################


def GetSaveName(count):
    # Get a save name based on the genre and 500movies
    return (
        os.getcwd()
        + "/data/location_data/raw_data/scraped_data/"
        + currentGENRE
        + "MovieLocations"
        + str(count)
        + "-"
        + str(count + 500)
        + ".csv"
    )


def GetNewSaveName(count, previousSaveName):
    # Get a **new** save name every 500 entries.
    # If the program crashes it at least has saved on a lot of "safe points"
    saveName = previousSaveName
    if count % 500 < 2:
        saveName = GetSaveName(count)
        previousSaveName = saveName
        print("saving under new filename: " + saveName)
    return saveName


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


def GetMovieListElement(url):
    # query the website and return the html to the variable ‘page’
    page = requests.get(url)

    # parse the html using beautiful soup and store in variable `soup`
    soup = bs(page.text, "html.parser")

    # Get the items of the list on the page
    movieLists = soup.find_all(class_="lister-item-header")
    return movieLists


def ContinuousTryExtractPage(count):
    # Attempt to scrape a page with 50 shows
    try:
        Scrape50Shows(count)
    # If an error is returned, wait 30 seconds and try again. Keep trying.
    except Exception:
        print(Exception)
        print("Sleeping for 30 secs and trying again")
        time.sleep(30)
        ContinuousTryExtractPage(count)


def ScrapeMoviesData(movieLists, writer):
    # Scrapes data for all movies from movielist and writes it to the CSV
    for movieList in movieLists:
        # The individual movies in the HTML
        for movieElement in movieList.find_all("a", href=True):
            # Go to the location webpage of the movie and the div holding the locations
            locationDiv = GetLocationDiv(movieElement)

            # Get all locations from this locations div
            if locationDiv is not None:
                locationElements = locationDiv.find_all(class_="soda sodavote odd")

                for locationElement in locationElements:
                    # Actual location description
                    WriteLocationData(locationElement, writer, movieElement)


def ScrapeAndWritePage(saveName, url):
    # Scrapes all movies and their locations on a page
    with open(saveName, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Code", "Show Name", "Location", "Scene"])

        # query the website and return the html to the variable ‘page’
        movieLists = GetMovieListElement(url)

        # This is actually a list of list, normally this should contain only one list
        ScrapeMoviesData(movieLists, writer)


def SleepAvoidTimeout(count):
    # After parsing 2500 movies sleep a bit to avoid connection refused
    if count % 2500 < 2:
        print("Sleep to avoid server connection refused")
        time.sleep(10)


def Scrape50Shows(count):
    # Scrape 50 shows at a time. 50 is the default amount that is shown at a page on IMDB
    global previousSaveName

    # Set up the Url for the page that is scraped now
    url = startUrlPart1 + str(count) + startUrlPart2

    # Get a new save name every 500 entries. If the program crashes it at least has saved on a lot of "safe points"
    saveName = GetNewSaveName(count, previousSaveName)

    # Write the scraped data to a csv
    ScrapeAndWritePage(saveName, url)

    # After parsing 2500 movies sleep a bit to avoid connection refused
    SleepAvoidTimeout(count)


# Actual program
########################################################################


def Run():
    # Run scraper consecutevily on categories
    global currentGENRE
    global startUrlPart1
    global startUrlPart2

    # The list of genres from IMDB we will scrape for
    genres = [
        "Action",
        "Adventure",
        "Family",
        "Fantasy",
        "History",
        "Horror",
        "Music",
        "Musical",
        "Mystery",
        "Sci-Fi",
        "Sport",
        "Superhero",
        "Thriller",
        "War",
        "Western",
    ]

    # Run scraper on every category
    for genre in genres:
        # Set the url we will scrape from currently
        currentGENRE = genre
        startUrlPart1 = (
            "https://www.imdb.com/search/title/?genres="
            + genre.lower()
            + "&view=simple&start="
        )
        startUrlPart2 = "&explore=title_type,genres&ref_=adv_nxt"

        # Scrape the range amount of movies. There are 50 movies per page.
        for count in range(0, 1000, 50):
            ContinuousTryExtractPage(count)


# Start Program
Run()
