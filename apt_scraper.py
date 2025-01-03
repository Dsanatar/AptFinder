import sys
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy import distance
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time


class Apt:
    def __init__(self, rent, beds, address, url):
        self.rent = rent
        self.address = address
        self.beds = beds
        self.distance = 0
        self.url = url
    
    def set_distance(self, dist):
        self.distance = dist

    def __str__(self):
        return f"{self.rent} | {self.beds} | {self.address}| {self.distance} | {self.url}"



if __name__ == '__main__':
    args = sys.argv
    if len(args) < 5:
        print("give me args: [city] [state] [beds] [price]")
        sys.exit(0)

    #headers = headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","Accept-Encoding":"gzip, deflate, br","upgrade-insecure-requests":"1"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    link = 'https://www.apartments.com/'

    city = args[1]
    state = args[2]
    beds = args[3]
    price = args[4]

    # read from cli?
    move_in = '?mid=20250901'

    location = city + '-' + state + '/'
    bed_query = 'min-' + beds + '-bedrooms'
    price_query = '-under-' + price

    query = link + location + bed_query + price_query +'/'
    

    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options)   

    apt_list = []
    count = 0
    for page in range(1,3):
        curr_query = query
        if page != 1:
            curr_query += str(page) + "/" + move_in
        else:
            curr_query += move_in

        print(curr_query)

        driver.get(curr_query)
        listings = driver.find_element(By.ID, "placardContainer").find_element(By.XPATH, ".//ul").find_elements(By.XPATH, ".//li[@class='mortar-wrapper']")
        
        
        for listing in listings:
            header = listing.find_element(By.XPATH, ".//article")
            url = header.get_attribute("data-url")
            addr = header.get_attribute("data-streetaddress")
            print(url)
            print(addr)

            # two different tags to look for here:
            price_elem = header.find_elements(By.XPATH, ".//div[@class='price-range']")
            price = ""

            if len(price_elem) > 0:
                price = price_elem[0].text
            else:
                price_elem = header.find_elements(By.XPATH, ".//p[@class='property-pricing']")
                if len(price_elem) > 0:
                    price = price_elem[0].text
                else:
                    price_elem = header.find_element(By.XPATH, ".//p[@class='property-rents']")
                    price = price_elem.text

            beds_elem = header.find_elements(By.XPATH, ".//p[@class='property-beds']")
            beds = ""

            if len(beds_elem) > 0:
                beds = beds_elem[0].text
            else:
                beds_elem = header.find_element(By.XPATH, ".//div[@class='bed-range']")
                beds = beds_elem.text

            count +=1
            apt = Apt(price, beds, addr, url)
            apt_list.append(apt)

    print("got " + str(count))
    sys.exit(0)

    '''
    #listings.extend(soup.find_all("li",{"class":"ListItem-c11n-8-106-0__sc-13rwu5a-0 StyledListCardWrapper-srp-8-106-0__sc-wtsrtn-0 hcrUex cLDGnX"}))
    for listing in driver.find_elements(By.CLASS_NAME, class_name):

        link = listing.find_all('data-url')
        print(link)
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
    '''
    
    loc = Nominatim(user_agent="Geopy Library")

    # Point of interest
    poi = "Davis Square MA"

    # entering the location name
    davis = loc.geocode(poi)
    davis_loc = (davis.latitude, davis.longitude)

    for apt in apt_list:
        addr = apt.address
        # some addresses here give a range, so split it and just take the second num
        if "-" in addr and "ID" not in addr:
            addr = re.split("-", addr, maxsplit=1)[1]

        #split on either | or ,
        addr_options = re.split('\| |,', addr, maxsplit=1)
        #print(addr_options)

        # this is weird, but the geopy package sometimes struggles to convert these addresses
        # so sometimes they have the name of the building that prefixes the address
        # split address to look for this building name and add the city and state
        # additionally, geopy doesn't seem to like APT #s in the search, so remove them here
        if (len(addr_options) > 1):
            #print(addr_options[0])
            addr_options[0] += " " + city + ", " + state
            addr_options[1] = re.sub("APT.\d+", "", addr_options[1])
            addr_options[1] = re.sub("Unit.*", "", addr_options[1])
            addr_options[1] += " " + city + ", " + state
            #print(addr_options[1])
        else:
            addr_options[0] = re.sub("APT.\d+", "", addr_options[0])
            addr_options[0] = re.sub("Unit.*", "", addr_options[0])
            addr_options[0] += " " + city + ", " + state
    
        # tries to do the distance calc on building name (if it exists) or the address
        for a in addr_options:
            #print(a)
            tmp = None
            try:
                tmp = loc.geocode(a)
            except:
                print("failed to find", a)
                continue

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