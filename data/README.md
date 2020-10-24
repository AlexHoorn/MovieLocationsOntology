- [IMDB Data](#imdb-data)
  - [Folder contens](#folder-contens)
  - [Explanation of converted data files](#explanation-of-converted-data-files)
    - [actor_map](#actor_map)
    - [character](#character)
    - [director_map](#director_map)
    - [genre_map](#genre_map)
    - [person](#person)
    - [show](#show)
- [Location Data](#location-data)
  - [Location data folder contents](#location-data-folder-contents)
  - [Explanation of location data creation process](#explanation-of-location-data-creation-process)
    - [Scraping](#scraping)
    - [Geocoding](#geocoding)
    - [Proces and clean data](#proces-and-clean-data)
    - [Create maps for ontology](#create-maps-for-ontology)
    - [Loading data into the ontology](#loading-data-into-the-ontology)
    - [Adding alignment with Wikidata resource URI's](#adding-alignment-with-wikidata-resource-uris)
  - [Explanation of converted data files](#explanation-of-converted-data-files-1)
    - [scene_map](#scene_map)
    - [location_map](#location_map)
    - [scene_info](#scene_info)
    - [location_info](#location_info)
    - [zenodo_data](#zenodo_data)
- [Overview](#overview)

# IMDB Data

## Folder contens

The folder of IMDB data stores the relevant files that were necessary for processing the raw data from IMDB to a tabular data structure that could directly be loaded into a linked data structure. The raw data from IMDB is not stored in this repository as it is deemed to large and already readily available from its [original source](https://www.imdb.com/interfaces/).

The script [`convert_data.py`](imdb_data/raw_data/convert_data.py) processes the raw data to a desired structure that can be imported into the ontology. Its full output and samples can be reviewed in the [converted data folder](imdb_data/converted_data/)

## Explanation of converted data files

### actor_map

[Sample](imdb_data/converted_data/samples/actor_map_sample.csv)

This table maps actors to a show. A show can have **multiple** actors. This table appears limited because **only the actors for who their character in the show is unknown appear in this table.** Further information of each specific actor is added to the ontology through the [person](#person) table.

| Column | Meaning                        |
| :----- | :----------------------------- |
| tconst | Identifier of a show           |
| nconst | Identifier of an actor/actress |

![actor_map](imdb_data/converted_data/images/actor_map.png)

### character

[Sample](imdb_data/converted_data/samples/character_sample.csv)

This table adds characters and their actors to a show. A show can have **multiple** characters. It is important to note that **these actors are not to be added directly to the show**. This should be through inference instead. Further information of each specific actor is added to the ontology through the [person](#person) table.

| Column      | Meaning                        |
| :---------- | :----------------------------- |
| tconst      | Identifier of a show           |
| nconst      | Identifier of an actor/actress |
| character   | Character name                 |
| characterId | Identifier of a character      |

![character](imdb_data/converted_data/images/character.png)

### director_map

[Sample](imdb_data/converted_data/samples/director_map_sample.csv)

This table maps directors to a show. A show can have **multiple** directors. Further information of each specific director is added to the ontology through the [person](#person) table.

| Column | Meaning                  |
| :----- | :----------------------- |
| tconst | Identifier of a show     |
| nconst | Identifier of a director |

![director_map](imdb_data/converted_data/images/director_map.png)

### genre_map

[Sample](imdb_data/converted_data/samples/genre_map_sample.csv)

This table maps genres to a show. A show can have **multiple** genres.

| Column | Meaning               |
| :----- | :-------------------- |
| tconst | Identifier of a show  |
| genre  | Identifier of a genre |

![genre_map](imdb_data/converted_data/images/genre_map.png)

### person

[Sample](imdb_data/converted_data/samples/person_sample.csv)

This table adds information to every person.

| Column      | Meaning                |
| :---------- | :--------------------- |
| nconst      | Identifier of a person |
| primaryName | Name of a person       |
| birthYear   | Year person was born   |
| deathYear   | Year person has died   |

![person](imdb_data/converted_data/images/person.png)

### show

[Sample](imdb_data/converted_data/samples/show_sample.csv)

This table adds information to every show.

| Column        | Meaning                                           |
| :------------ | :------------------------------------------------ |
| tconst        | Identifier of a show                              |
| titleType     | Identifier of the showtype                        |
| primaryTitle  | Name of a show                                    |
| isAdult       | Whether the show is for adults only               |
| startYear     | The release year for movies/start year for series |
| endYear       | The end year of series                            |
| runimeMinutes | Length of show in minutes                         |
| averageRating | Average rating of a show *(0-10)*                 |

![show](imdb_data/converted_data/images/show.png)

# Location Data

## Location data folder contents

The location data folder has several subfolder used in the process of creating these datasets. The process of creating this data is described in the [explanation of the data creation](#Explanation-of-location-data-creation-process). The resulting individual datafiles are explained under the [explanation of converted data files](#explanation-of-converted-data-files).

The [converted_data](location_data/scripts/) folder contains the endproduct of the dataset creation process: data ready for import into protege. The [images](location_data/images/) folder contains several illustrations used in the readme. The [raw_data](location_data/raw_data/) folder contains the raw data before it was processed towards an end product. This data forms the basis for the converted_data. It contains the raw data in several stages. The first stage was the scraped stage and the second stage was the geocoded stage. After cleaning and processing the geocoded data this data was saved in the converted data folder. The raw_data folder has an additional subfolder with wikidata_mappings. These were dictionaries used to map our shows to equivalent wikidata resources. The [scripts](location_data/scripts/) folder contains all scripts written for the dataset creation process.

## Explanation of location data creation process

The process of gathering the locations for the shows consisted of several steps. The steps are: Scraping, Geocoding, Processing & cleaning, Creating maps and finally loading the data into protege.

The proces from internet pages for scenes and locations to an ontology can be visualized as follows:

![location_data_progress](location_data/images/location_data_process.png)

### Scraping

The IMDB datasets **did not provide scenes and locations** for shows so we built a scraper to collect this data ourselves. This was done using the scrape_location_data.py script. After we had our first prototype functioning we found out that some scenes were missing. The scraper had accidentally only scraped odd rows and not even rows. A new scraper script was missing to only scrape for the data that was missing so that not everything had to be scraped again and geocoded again. The scrape_missing_data.py scraped all locations and scenes that were not included yet in our data. As such **the scraping step was done twice**. The second time for the missed scenes. Every step following this step was also done twice, now with the additional data from the missed scenes.

### Geocoding

While we had strings of locations and strings of scenes for titles these **location strings** did not yet have any connection to **"real" locations with longitudes and latitudes**. The fetch_nominatim_data.py script was created. This script fetched the coordinates for our locations by geocding them. Running on one computer this would have taken 24 hours so we made a script that automatically divided the workload over our four computers. Every person of the group ran this script simulteneously geocoding the location strings to locations with real latitudes and longitudes. All other geocoding API's were checked but didn't provide the service we needed on either scale, functionality or pricing.

### Proces and clean data

We now had data for scenes with actual locations and their longitudes and latitudes. The process_geocoded_data.py script **cleaned and processed** this data by giving columns appropriate names, removing special characters among other cleaning operations.

### Create maps for ontology

The fourth step was **creating several excel datasets** that could be loaded into protege with some easy rules. The cleaned, geocoded data was split in four excel dataset. More information on this can be found in the [explanation of converted data files](#explanation-of-converted-data-files).

### Loading data into the ontology

The final step was loading the data of our several processed datasets into protege using the cellfie plugin. This was one of the most time-consuming steps since every single one of our 10 datasets was too heavy to handle for protege often resulting in "axiom generating" times of 30 minutes. The rules that were used for loading the data into protege can be found in [the import rules for the ontology](../ontology/import_rules/actor_map.json).
The following images illustrate some of the import rules (non-exhaustive) found in this folder. With these import rules both IMDB data and Location data were loaded into the protege ontology.
![ruleset_img](../ontology/import_rules/images/actor.png)
![ruleset_img](../ontology/import_rules/images/actor_map.png)
![ruleset_img](../ontology/import_rules/images/character.png)
![ruleset_img](../ontology/import_rules/images/location.png)
![ruleset_img](../ontology/import_rules/images/location_map.png)
![ruleset_img](../ontology/import_rules/images/scene.png)
![ruleset_img](../ontology/import_rules/images/scene_map.png)
![ruleset_img](../ontology/import_rules/images/show.png)

### Adding alignment with Wikidata resource URI's

An additional step was further postprocessing the data to include a column indicating a wikidata resource. With this column our data was aligned to external RF data on the web. This also allowed for great reuse of our data for future users. This mapping was done via the add_owl_same_as.py script. In this script we queried wikidata for sections of 80 shows and saved the resources that were returned. For more information on this dataset see [zenodo_data](##zenodo_data). Finally with the data created from the add_owl_same_as.py script we integrated the alignment to wikidata resources into the ontology with the map_wiki_resources.py script. The resulting ontology was uploaded to [zenodo.org](https://zenodo.org/record/4126948).

## Explanation of converted data files

### scene_map

[Sample](converted_data/samples/scene_map_sample.csv)

This table maps scenes to a show. A show can have **multiple** scenes. Further information of each specific scene is added to the ontology through the [scene_info](#scene_info) table.

| Column | Meaning               |
| :----- | :-------------------- |
| tconst | Identifier of a show  |
| sconst | Identifier of a scene |

### location_map

[Sample](converted_data/samples/location_map_sample.csv)

This table maps locations to a show. **It only maps locations to shows if there was no scene for this location**. Locations for a scene were mapped to their respective scene. A show can have **multiple** locations. Further information of each specific location is added to the ontology through the [location_info](#location_info) table.

| Column | Meaning                  |
| :----- | :----------------------- |
| tconst | Identifier of a show     |
| lconst | Identifier of a location |

### scene_info

[Sample](converted_data/samples/scene_info_sample.csv)

This table contains the scene identifier and it's attributes. A scene has a label and a location identifier as attributes. More information about locations can be found in the [location_info](#location_info).

| Column | Meaning                                     |
| :----- | :------------------------------------------ |
| sconst | Identifier of a scene                       |
| lconst | ID of the location where the scene was shot |
| sLabel | IMDB label for the scene                    |

### location_info

[Sample](converted_data/samples/location_info_sample.csv)

This table contains the location identifier and it's attributes. A location has a label, alternative label, longitude and latitude. The alternative label is the original lable mentione don IMDB. The default label is the geocoded location from nominatim.

| Column    | Meaning                   |
| :-------- | :------------------------ |
| lconst    | Identifier of a location  |
| lLabel    | Default geocoded label    |
| lAltLabel | Alternative IMDB label    |
| lat       | Latitude of the location  |
| long      | Longitude of the location |

### zenodo_data

This file contains the data of all the previously mentioned datasets combined. It also has an additional column for **wikidata_entry** which maps each of our items to a wikidata resource. This greatly improves reusability for our dataset since it aligns the data to resources on the web. This dataset was created by the additional step of aligning with Wikidata resource URI's. This dataset was merged into our ontology in the final step with the map_wiki_resources.py script. This ontology was uploaded to [zenodo.org](https://zenodo.org/record/4126948)

| Column         | Meaning                                                               |
| :------------- | :-------------------------------------------------------------------- |
| tconst         | Identifier of a show                                                  |
| sconst         | Identifier of a scene                                                 |
| sLabel         | IMDB label for the scene                                              |
| lconst         | Identifier of a location                                              |
| lLabel         | Default geocoded label                                                |
| lAltLabel      | Alternative IMDB label                                                |
| lat            | Latitude of the location                                              |
| long           | Longitude of the location                                             |
| rowconst       | Identifier for every unique combination of title, scene and location  |
| wikidata_entry | Url to a wikidata entity which is the same as the tconst (owl:sameAs) |

# Overview

The figure below provides an overview of all data combined into the desired linked data structure.

![Overview](imdb_data/converted_data/images/overview.png)
