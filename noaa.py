import csv
import requests
from datetime import datetime
from datetime import timedelta

zone_to_lat_lng = {}
observations = []

"""
Map each zone to the [lat, lng]. 

NOTE: the index of the data is all hardcoded and heavily dependent on file format

Returns:
	Nothing, populates global mapping
"""
def read_in_zone_to_lat_lng():
	with open('zone_to_zip.csv') as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    first = True;
	    for row in readCSV:
	    	if (first):
	    		# header row
	    		first = False;
	    		continue;

	        zone_to_lat_lng[row[0]] = [row[2], row[3]]

def write_observations(observations):
    with open('observations.csv', mode='w') as csv_file:
            fieldnames = ["zone", "station_id", 'start', "end", "temp"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for o in observations:
                writer.writerow(o.map())

"""
Gets the closest station to the lat,lng

Example request_url: https://api.weather.gov/points/39.0693%2C-94.6716/stations

Params:
    lat: float 
    lng: float 

Returns:
    station_ids: list of strings
"""
def get_stations_for_point(lat, lng):
    request_url = "https://api.weather.gov/points/" + str(lat) + "%2C" + str(lng) + "/stations"
    response_json = requests.get(request_url).json()

    # Make sure we have a valid response from the API
    if "features" in response_json:
        features = response_json["features"]
        if len(features) > 0:
            return [x["properties"]["stationIdentifier"] for x in features]

            # return response_json["features"][0]["properties"]["stationIdentifier"]

    return ""

"""
Grab 1 observation for a given station_id, between start_time and end_time

Example request_url: https://api.weather.gov/stations/KEMP/observations?start=2019-05-18T09%3A00%3A00%2B00%3A00&end=2019-05-18T10%3A00%3A00%2B00%3A00&limit=1

Params:
    station_id: string
    start: datetime object
    end: datetime object

Returns:
   Temperature measured by the station sometime between start and end
"""
def get_one_observation(station_id, start, end):

    observation_url = "https://api.weather.gov/stations/" + station_id + "/observations?" \
        "start=" \
        "" + str(start.year) + "-" \
        "{:02d}".format(start.month) + "-" \
        "{:02d}".format(start.day) + "T" \
        "{:02d}".format(start.hour) + "%3A00%3A00%2B00%3A00&" \
        "end=" \
        "" + str(end.year) + "-" \
        "{:02d}".format(end.month) + "-" \
        "{:02d}".format(end.day) + "T" \
        "{:02d}".format(end.hour) + "%3A00%3A00%2B00%3A00&" \
        "&limit=1"

    print observation_url
    response_json = requests.get(observation_url).json()

    # Make sure we have a valid response from the API
    if "features" in response_json:
        if len(response_json["features"]) > 0:
            return response_json["features"][0]["properties"]["temperature"]["value"]


    return ""

"""
Returns a list of datetime objects from start to end, with increments

Params:
    start: datetime object to start at, inclusive
    end: datetime object to end at, exclusive
    increment: timedelta difference between each datetime object

Returns:
    List of datetime objects at increment intervals
"""
def create_dates(start, end, increment):
    dates = []
    current = start
    while current != end:

        dates.append(current)
        current += increment

    return dates

class Observation:
    def __init__(self, zone, station_id, start, end, temp):
        self.zone = zone
        self.station_id = station_id
        self.start = start
        self.end = end
        self.temp = temp

    def map(self):
        return {"zone": self.zone, "station_id": self.station_id, "start": self.start.strftime("%Y/%m/%d %H:%M:%S"), "end": self.end.strftime("%Y/%m/%d %H:%M:%S"), "temp": self.temp}

######################################## ACTUAL PROCESSING #################################

# Read in zone to lat,lng data
read_in_zone_to_lat_lng()
# dates = create_dates(datetime(2017, 4, 30), datetime(2019, 4, 30), timedelta(hours=1))
dates = create_dates(datetime(2019, 5, 16, 8), datetime(2019, 5, 18, 8), timedelta(hours=1))

observations = []

for zone, latlng in zone_to_lat_lng.iteritems():
    station_ids = get_stations_for_point(latlng[0], latlng[1])

    # Make sure we have a valid station_id
    for i in range(len(dates) - 1):
        start = dates[i]
        end = dates[i+1]

        temp = ""
        for station_id in station_ids:
            temp = get_one_observation(station_id, start, end)

            # Exit as soon as we find one temp
            if temp != "":
                break

        observation = Observation(zone, station_id, start, end, temp)
        print observation.map()
        observations.append(observation)

    ## Do something
write_observations(observations)

# Output zone to weather mapping





######################################## DEBUGGING #################################
# Expected: 21.7 (degrees C)
# print get_one_observation("KEMP", datetime(2019, 5, 18, 9), datetime(2019, 5, 18, 10))

# Expected: KMKC
# print get_stations_for_point(39.0693,-94.6716) 

# print zone_to_lat_lng

# print Observation("PEPCO", "KEMP", datetime(2019, 8, 5), datetime(2019, 8, 6)).map()
