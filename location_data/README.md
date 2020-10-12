- [Explanation of converted data files](#explanation-of-converted-data-files)
  - [scene_map](#scene_map)
  - [location_map](#location_map)
  - [scene_info](#scene_info)
  - [location_info](#location_info)
- [Other](#other)
    - [Old notes](#old-notes)

# Explanation of converted data files

## scene_map

[Sample](converted_data/samples/scene_map_sample.csv)

This table maps scenes to a show. A show can have **multiple** scenes. Further information of each specific scene is added to the ontology through the [scene_info](#scene_info) table.

| Column | Meaning               |
| :----- | :-------------------- |
| tconst | Identifier of a show  |
| sconst | Identifier of a scene |

## location_map

[Sample](converted_data/samples/location_map_sample.csv)

This table maps locations to a show. **It only maps locations to shows if there was no scene for this location**. Locations for a scene were mapped to their respective scene. A show can have **multiple** locations. Further information of each specific location is added to the ontology through the [location_info](#location_info) table.

| Column | Meaning                  |
| :----- | :----------------------- |
| tconst | Identifier of a show     |
| lconst | Identifier of a location |

## scene_info

[Sample](converted_data/samples/scene_info_sample.csv)

This table contains the scene identifier and it's attributes. A scene has a label and a location identifier as attributes. More information about locations can be found in the [location_info](#location_info). 

| Column | Meaning                                     |
| :----- | :------------------------------------------ |
| sconst | Identifier of a scene                       |
| lconst | ID of the location where the scene was shot |
| sLabel | IMDB label for the scene                    |

## location_info

[Sample](converted_data/samples/location_info_sample.csv)

This table contains the location identifier and it's attributes. A location has a label, alternative label, longitude and latitude. The alternative label is the original lable mentione don IMDB. The default label is the geocoded location from nominatim.

| Column    | Meaning                   |
| :-------- | :------------------------ |
| lconst    | Identifier of a location  |
| lLabel    | Default geocoded label    |
| lAltLabel | Alternative IMDB label    |
| lat       | Latitude of the location  |
| long      | Longitude of the location |






# Other
### Old notes

9/10: All you need to do is run the fetch_nominatim_data.py install the dependencies and enter your number. You can stop the program, when you start it again it will take off at the file where it stopped.

8/10: I have checked a lot of services and they all have their drawbacks in price, availability, etc. So we will do the proposed split of the raw_location_data in four parts where all four of us run the nominatim_fetcher included in this folder.

7/10: We have around 75000 locations for 30000 movies after removing studios.

GeoCoding might be an issue. Open API's such as Nominatim work very well but discourage bulk and prefer max. 1 request per second.

- I have temporarily used the usadress library to parse the locations to categories that might be helpful in getting the lat and long via dbPedia. There are other parsing libraries. Of the three that I tried this one was the best but not good enough.

- Alternatively we can reuest Geocoding from Nominatim on the fly in our website interface. Then it only has to code the locations that come from the filters.

- Alternatively, we can look into some API that allows bulk geocoding for free for a max. amount of requests. I.e. after registering 10000 queries for free.
