<h5>Current instructions</h5>

9/10: All you need to do is run the fetch_nominatim_data.py install the dependencies and enter your number. You can stop the program, when you start it again it will take off at the file where it stopped.

<h5>Old notes</h5>

8/10: I have checked a lot of services and they all have their drawbacks in price, availability, etc. So we will do the proposed split of the raw_location_data in four parts where all four of us run the nominatim_fetcher included in this folder.

7/10: We have around 75000 locations for 30000 movies after removing studios.

GeoCoding might be an issue. Open API's such as Nominatim work very well but discourage bulk and prefer max. 1 request per second.

- I have temporarily used the usadress library to parse the locations to categories that might be helpful in getting the lat and long via dbPedia. There are other parsing libraries. Of the three that I tried this one was the best but not good enough.

- Alternatively we can reuest Geocoding from Nominatim on the fly in our website interface. Then it only has to code the locations that come from the filters.

- Alternatively, we can look into some API that allows bulk geocoding for free for a max. amount of requests. I.e. after registering 10000 queries for free.
