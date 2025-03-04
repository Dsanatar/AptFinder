import sys
import requests
#from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy import distance
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from functools import partial
import argparse
from Apt import Apt, csv_dump
from distance import get_distances

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='apt_scraper')
    parser.add_argument('cities', nargs="+", type=str, help="list of cities to search")
    parser.add_argument('state', type=str, help="single state abbreviation ex: ny")
    parser.add_argument('beds', type=int, help="number of bedrooms")
    parser.add_argument('price', type=int, help="max search price")
    parser.add_argument('--pages', nargs='?', type=int, default=1)

    args = parser.parse_args()
    print(args)
    
    if args.state == '' or not args.cities:
        print("please provide state and city")
        parser.print_help()
        sys.exit(0)


    #headers = headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","Accept-Encoding":"gzip, deflate, br","upgrade-insecure-requests":"1"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    link = 'https://www.apartments.com/'

    # increment page number bc loop is exclusive bounds
    max_pages = args.pages+1

    bed_query = 'min-' + str(args.beds) + '-bedrooms'
    price_query = '-under-' + str(args.price)
    
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options)   
    loc = Nominatim(user_agent="Geopy Library")
    geocode = partial(loc.geocode, language="en")

    apt_list = []
    count = 0
    for city in args.cities:
        # before we do the search, make sure the provided cities are valid
        try:
            test = geocode(city + ", " + args.state)
            if test == None:
                 print("invalid city name: ", city)
                 continue
        except:
            print("invalid city name: ", city)
            continue

        location = city + '-' + args.state + '/'
        query = link + location + bed_query + price_query +'/'
        for page in range(1,max_pages):
            curr_query = query
            '''
            if page != 1:
                curr_query += str(page) + "/" + move_in
            else:
                curr_query += move_in
            '''

            print(curr_query)

            driver.get(curr_query)
            listings = driver.find_element(By.ID, "placardContainer").find_element(By.XPATH, ".//ul").find_elements(By.XPATH, ".//li[@class='mortar-wrapper']")
            
            
            for listing in listings:
                header = listing.find_element(By.XPATH, ".//article")
                url = header.get_attribute("data-url")
                #addr = header.get_attribute("data-streetaddress")
                addr_detail = header.find_elements(By.XPATH, ".//div[@class='property-address js-url']")
                addr_title = header.find_elements(By.XPATH, ".//div[@class='property-title']")
                addr = ''

                if addr_detail:
                    addr = addr_detail[0].text
                elif addr_title:
                    addr = addr_title[0].text
                else:
                    print('oops')
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
                apt = Apt(price, beds, addr, city, url)
                apt_list.append(apt)

    print("got " + str(count))

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
    get_distances(apt_list, args.state)    

    # sort listings by rent
    apt_list.sort(key=lambda x: x.distance)

    csv_dump(apt_list)
