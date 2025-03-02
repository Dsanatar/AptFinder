from geopy.geocoders import Nominatim
from geopy import distance
from functools import partial
import re

def get_distances(apt_list, state):

    loc = Nominatim(user_agent="Geopy Library")
    geocode = partial(loc.geocode, language="en")
    # Point of interest
    poi = "Davis Square MA"

    # entering the location name
    davis = geocode(poi)
    davis_loc = (davis.latitude, davis.longitude)

    for apt in apt_list:
        addr = apt.address
        # some addresses here give a range, so split it and just take the second num
        if "-" in addr and "ID" not in addr:
            addr = re.split("-", addr, maxsplit=1)[1]

        # gecode doesn't like unit numbers 
        # regex here removes everything after Unit until the next comma
        # so it keeps the city name from the address
        addr = addr.lower()
        if 'unit' in addr:
            addr = re.sub('unit[^,]*', "", addr)
        elif '#' in addr:
            addr = re.sub('#[^,]*', "", addr)
        elif 'apt':
            addr = re.sub('apt[^,]*', "", addr)

        '''
        #split on either | or ,
        addr_options = re.split('\| |,', addr, maxsplit=1)
        #print(addr_options)

        # this is weird, but the geopy package sometimes struggles to convert these addresses
        # so sometimes they have the name of the building that prefixes the address
        # split address to look for this building name and add the city and state
        # additionally, geopy doesn't seem to like APT #s in the search, so remove them here
        if (len(addr_options) > 1):
            #print(addr_options[0])
            addr_options[0] += " " + apt.get_city() + ", " + state
            addr_options[1] = re.sub("APT.\d+", "", addr_options[1])
            addr_options[1] = re.sub("Unit.*", "", addr_options[1])
            addr_options[1] += " " + apt.get_city() + ", " + state
            #print(addr_options[1])
        else:
            addr_options[0] = re.sub("APT.\d+", "", addr_options[0])
            addr_options[0] = re.sub("Unit.*", "", addr_options[0])
            addr_options[0] += " " + apt.get_city() + ", " + state
        '''
        # tries to do the distance calc on building name (if it exists) or the address
        #print(a)
        tmp = None
        try:
            tmp = geocode(addr)
        except:
            print("failed to find", addr)
            continue

        # if we can't resolve the address, just move on
        if tmp == None:
            print("?? ", addr)
            continue

        #tmp = loc.geocode(apt_list[1].address.split('|')[-1])
        tmp_loc = (tmp.latitude, tmp.longitude)

        dist = round(distance.distance(tmp_loc, davis_loc).miles, 2)
        print("****Distance = ", dist)
        if dist > 20:
            print("invalid distance...")
            dist = 0
        apt.set_distance(dist)
        # if we find and calculate a valid distance, we can stop this loop, no need to do it twice