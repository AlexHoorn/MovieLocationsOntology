from bs4 import BeautifulSoup as bs
import requests
import csv
import time



currentGENRE = ""

def GetSaveName(count):
    return currentGENRE+"MovieLocations" + str(count) + "-" + str(count+500) + ".csv"

previousSaveName = ""


def Scrape50Shows(count):
    global previousSaveName

    # Set up the Url for the page that is scraped now
    url = startUrlPart1 + str(count) + startUrlPart2
    print(("Getting url:-----------------------------"))
    print(url)

    # Get a new save name every 500 entries.
    # If the program crashes it at least has saved on a lot of "safe points"
    saveName = previousSaveName
    if (count % 500 < 2):
        saveName = GetSaveName(count)
        previousSaveName = saveName
        print("saving under new filename: " + saveName)

    # Write the scraped data to a csv
    with open(saveName, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Code", "Show Name", "Location", "Scene"])

        # query the website and return the html to the variable ‘page’
        page = requests.get(url)

        # parse the html using beautiful soup and store in variable `soup`
        soup = bs(page.text, 'html.parser')

        # Get the items of the list on the page
        content = soup.find_all(class_="lister-item-header")

        for item in content:
            for a in item.find_all("a", href=True):
                print(a.text)
                newLink = "https://www.imdb.com" + a['href'] + "locations"
                print(newLink)
                newPage = requests.get(newLink)
                newSoup = bs(newPage.text, 'html.parser')
                locationHolder = newSoup.find(id="filming_locations")
                if locationHolder is not None:
                    elements = locationHolder.find_all(class_="soda sodavote odd")

                    for element in elements:
                        location = element.find("a")
                        scene = element.find("dd")
                        print(location.text.replace("\n", "", 999))
                        print(scene.text.replace("\n", "", 999))

                        writer.writerow([a['href'], a.text, location.text.replace("\n", "", 999),
                                         scene.text.replace("\n", "", 999)])
    if count % 2500 < 2:
        print("Sleep to avoid server connection refused")
        time.sleep(10)

#If an error is returned, wait 30 seconds and try again. Keep trying.
def ContinuousTryExtractPage():
    try:
        Scrape50Shows(count)
    except Exception:
        print(Exception)
        print("Sleeping for 30 secs and trying again")
        time.sleep(30)
        ContinuousTryExtractPage()


genres = ["Family", "Fantasy", "History", "Horror", "Music", "Musical", "Mystery", "Sci-Fi", "Sport", "Superhero", "Thriller", "War", "Western"]
for genre in genres:
    currentGENRE = genre
    startUrlPart1 = "https://www.imdb.com/search/title/?genres="+ genre.lower() +"&view=simple&start="
    startUrlPart2 = "&explore=title_type,genres&ref_=adv_nxt"

    #Scrape the range amount of movies. There are 50 movies per page.
    for count in range(0, 1000, 50):
        ContinuousTryExtractPage()
