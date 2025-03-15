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

def scrape_apts(city, state, beds, price, apt_list):
    #headers = headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","Accept-Encoding":"gzip, deflate, br","upgrade-insecure-requests":"1"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    link = 'https://www.apartments.com/'

    # increment page number bc loop is exclusive bounds
    max_pages = 2

    bed_query = 'min-' + str(beds) + '-bedrooms'
    min_price = price - 500
    price_query = '-' + str(min_price) + '-to-' + str(price)
    
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_argument("--headless=new")

    driver = webdriver.Chrome(options)   
    loc = Nominatim(user_agent="Geopy Library")
    geocode = partial(loc.geocode, language="en")

    count = 0

    # before we do the search, make sure the provided cities are valid
    try:
        test = geocode(city + ", " + state)
        if test == None:
                print("invalid city name: ", city)
                return
    except:
        print("invalid city name: ", city)
        return

    location = city + '-' + state + '/'
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

            # strip off price range
            if '-' in price:
                price = price.split('-')[0]

            # remove characters so we can sort as an int
            price = price.replace('$','')
            price = price.replace(',','')

            beds_elem = header.find_elements(By.XPATH, ".//p[@class='property-beds']")
            beds = ""

            if len(beds_elem) > 0:
                beds = beds_elem[0].text
            else:
                beds_elem = header.find_element(By.XPATH, ".//div[@class='bed-range']")
                beds = beds_elem.text

            # strip off range
            if '-' in beds:
                beds = beds.split('-')[0]
                beds += ' Beds'
            if ',' in beds:
                beds = beds.split(',')[0]

            count +=1
            apt = Apt(price, beds, addr, city, url)
            apt_list.append(apt)

    print("got " + str(count))
    
    #get_distances(apt_list, state)    

    # sort listings by rent
    #apt_list.sort(key=lambda x: x.distance)

    #csv_dump(apt_list)
