import sys
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy import distance
import re


class Apt:
    def __init__(self, rent, beds, address):
        self.rent = rent
        self.address = address
        self.beds = beds
        self.distance = 0
    
    def set_distance(self, dist):
        self.distance = dist

    def __str__(self):
        return f"${self.rent} {self.beds} @ {self.address}, {self.distance}mi"



if __name__ == '__main__':
    args = sys.argv
    if len(args) < 4:
        print("give me args: [city] [beds] [price]")
        sys.exit(0)

    headers = headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","Accept-Encoding":"gzip, deflate, br","upgrade-insecure-requests":"1"}
    zillow = 'https://www.zillow.com/'

    city = args[1]
    beds = args[2]
    price = args[3]
    state = '-ma'

    bed_query = '"beds":{"min":' + str(beds) + '},'
    #bed_query = 'beds%22%3A%7B%22min%22%3A' + str(beds) + '%7D%7D%2C'
    price_query ='"mp":{"max":' + str(price) + '},"price":{"max":678881},'
    #price_query = 'mp%22%3A%7B%22min%22%3Anull%2C%22max%22%3A' + str(price) + '%7D%2C'

    apt_list = []
    for page in range(1,2):
        query = '/rentals/?searchQueryState={"isMapVisible":true,"mapBounds":{"west":-71.20319402978515,"east":-71.02123297021484,"south":42.32359097463271,"north":42.433152995065775},"mapZoom":12,"usersSearchTerm":"Cambridge MA","regionSelection":[{"regionId":3934,"regionType":6}],"filterState":{"fr":{"value":true},"fsba":{"value":false},"fsbo":{"value":false},"nc":{"value":false},"cmsn":{"value":false},"auc":{"value":false},"fore":{"value":false},' + bed_query + price_query +'"mf":{"value":false},"land":{"value":false},"manu":{"value":false}},"isListVisible":true}'
        #query = '/rentals/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-71.20319402978515%2C%22east%22%3A-71.02123297021484%2C%22south%22%3A42.32359097463271%2C%22north%22%3A42.433152995065775%7D%2C%22mapZoom%22%3A12%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A3934%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22priorityscore%22%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22price%22%3A%7B%22min%22%3Anull%2C%22max%22%3A584024%7D%2C%22' + price_query + '%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22' + bed_query + '%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3A%22Cambridge%20MA%22%7D'
        zillow = zillow + city + state + query

        req = requests.get(zillow, headers=headers)
        
        resp = req.text

        soup = BeautifulSoup(resp,'html.parser')
        class_name = ' '.join(soup.find(id="grid-search-results").find("li")["class"])

        #listings.extend(soup.find_all("li",{"class":"ListItem-c11n-8-106-0__sc-13rwu5a-0 StyledListCardWrapper-srp-8-106-0__sc-wtsrtn-0 hcrUex cLDGnX"}))
        for listing in soup.find_all("li",{class_name}):
            if listing.find("span",{'data-test':'property-card-price'}) == None:
                # this is to avoid grabbing listings from the website that are "loading"
                continue
            rent = listing.find("span",{'data-test':'property-card-price'}).text

            # this assumes we aren't looking for higher than 4digit rent cost
            rent_int = rent.replace('$', '').replace(',', '')[:4]

            addr = listing.find("address", {'data-test': 'property-card-addr'}).text

            bd_bath = ""
            count = 0
            for stat in listing.find_all("ul", class_="StyledPropertyCardHomeDetailsList-c11n-8-106-0__sc-1j0som5-0 eDOePJ"):
                for list_items in stat.find_all('li'):
                    bd_bath = bd_bath + list_items.text + ' '
                    count = count + 1
                    # first two entries have bed/bath
                    if count == 2:
                        break

            # this is the case where the listing contains multiple units
            if bd_bath == '':
                bd_bath = rent[rent.find("+")+2:]

            
            apt = Apt(rent_int, bd_bath, addr)
            apt_list.append(apt)
    
    loc = Nominatim(user_agent="Geopy Library")

    # Point of interest
    poi = "Davis Square MA"

    # entering the location name
    davis = loc.geocode(poi)
    davis_loc = (davis.latitude, davis.longitude)



    for apt in apt_list:
        #print(apt.address)
        addr = apt.address
        #split on either | or ,
        addr_options = re.split('\| |, ', addr, maxsplit=1)
        #print(addr_options)

        # this is weird, but the geopy package sometimes struggles to convert these addresses
        # so sometimes they have the name of the building that prefixes the address
        # split address to look for this building name and add the city and state
        # additionally, geopy doesn't seem to like APT #s in the search, so remove them here
        if (len(addr_options) > 1):
            addr_options[0] += " " + city + ", MA"
            #print(addr_options[0])
            addr_options[1] = re.sub("APT.\d+", "", addr_options[1])
            #print(addr_options[1])
        else:
            addr_options[0] = re.sub("APT.\d+", "", addr_options[0])
    
        # tries to do the distance calc on building name (if it exists) or the address
        for a in addr_options:
            tmp = loc.geocode(a)
            # if we can't resolve the address, just move on
            if tmp == None:
                continue
            #tmp = loc.geocode(apt_list[1].address.split('|')[-1])
            tmp_loc = (tmp.latitude, tmp.longitude)

            dist = round(distance.distance(tmp_loc, davis_loc).miles, 2)
            print("****Distance = ", dist)
            apt.set_distance(dist)
            # if we find and calculate a valid distance, we can stop this loop, no need to do it twice
            break
    
    # sort listings by rent
    apt_list.sort(key=lambda x: x.distance)
    for apt in apt_list:
        print(apt)