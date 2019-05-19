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
    with open('darksky_observations.csv', mode='w') as csv_file:
            fieldnames = ["zone", "hour", "temp"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for o in observations:
                writer.writerow(o.map())

"""
Grab the day's hourly observations for a lat,lng on the given time_secs

Params:
    lat: float
    lng: float 
    time_secs: long of seconds since epoch 

Returns:
   Temperature measured by the station sometime between start and end
"""
def get_hourlys(lat, lng, time_secs):
    darksky_api_key = "TODO"
    darksky_url = "https://api.darksky.net/forecast/" \
        datasky_api_key + "/" \
        "" + str(lat) + "," \
        "" + str(lng) + "," \
        "" + str(time_secs) + \
        "?exclude=currently,minutely,daily,alerts,flags"

    response_json = requests.get(darksky_url).json()

    hourlys = []

    # Make sure we have a valid response from the API
    if "hourly" in response_json:
        if "data" in response_json["hourly"]:
            data = response_json["hourly"]["data"]

            for x in data:
                if "time" in x and "temperature" in x:
                    hourlys.append([x["time"], x["temperature"]])

    return hourlys

"""
Returns a list of datetime objects from start to end, with increments

Params:
    start: datetime object to start at, inclusive
    end: datetime object to end at, exclusive

Returns:
    List of datetime objects at each day within the range 
"""
def create_dates(start, end):
    increment = timedelta(days=1)
    dates = []
    current = start
    while current != end:

        dates.append(current)
        current += increment

    return dates

class Observation:
    def __init__(self, zone, hour, temp):
        self.zone = zone
        self.hour = hour
        self.temp = temp

    def map(self):
        return {"zone": self.zone, "hour": datetime.fromtimestamp(self.hour).strftime('%Y/%m/%d %H:%M:%S'), "temp": self.temp}


def seconds_since_epoch(dt):
    return int((dt - datetime(1970,1,1)).total_seconds())

######################################## ACTUAL PROCESSING #################################

""
# Read in zone to lat,lng data
read_in_zone_to_lat_lng()
dates = create_dates(datetime(2017, 4, 30), datetime(2019, 4, 30))

observations = []

for zone, latlng in zone_to_lat_lng.iteritems():
    # Make sure we have a valid station_id
    for day in dates:
        hourlys = get_hourlys(latlng[0], latlng[1], seconds_since_epoch(day))
        if len(hourlys) > 0:
            for hour_temp in hourlys:
                observation = Observation(zone, hour_temp[0], hour_temp[1])
                observations.append(observation)

    ## Do something
write_observations(observations)

# Output zone to weather mapping





######################################## DEBUGGING #################################
# Expected: 21.7 (degrees C)
# print get_one_observation("KEMP", datetime(2019, 5, 18, 9), datetime(2019, 5, 18, 10))

# List of {time, temp} for each hour that day
# print get_hourlys(39.0693,-94.6716, 1556582400) 

# print zone_to_lat_lng

# print Observation("PEPCO", "KEMP", datetime(2019, 8, 5), datetime(2019, 8, 6)).map()
