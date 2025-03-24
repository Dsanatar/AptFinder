import sys
import requests
import re
import time
from dotenv import dotenv_values
from Apt import Apt, csv_dump
from distance import get_distances


def get_zillow(city_list, state, is_rental, rent, beds, move_in_date, apt_list):

    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

    # TODO make sure location is valid?

    is_rental = True
    status_type = ''

    # TODO remove this if results are bad
    #sort = 'Newest'

    rentMinPrice = str(rent - 500)
    rentMaxPrice = str(rent)
    bedsMin = str(beds)

    if is_rental:
        status_type = 'ForRent'
    else:
        status_type = 'ForSale'

    env = dotenv_values('.env')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "x-rapidapi-key": env["API_KEY"],
        "x-rapidapi-host": "zillow-com1.p.rapidapi.com"
    }

    # make request for each city in config
    for city in city_list:
        location = (city.strip() + ", " + state)
        print(location)

        querystring = {
                    "location": location,
                    "status_type":status_type,
                    "rentMinPrice": rentMinPrice,
                    "rentMaxPrice": rentMaxPrice,
                    "bedsMin": bedsMin,
                    "moveInDate": move_in_date
        }
        print(querystring)
        
        response = requests.get(url, headers=headers, params=querystring)
        print(response)

        data = response.json()
        #print(data)
        listings = data['props']

        prefix = 'https://www.zillow.com'

        for apt in listings:
            # response is different if listing has multiple units
            if 'units' in apt:
                unit = apt['units'][0]
                beds = unit['beds']
                rent = unit['price']
                rent = rent.replace('+', '')
                rent = rent.replace('$', '')
                rent = rent.replace(',', '')
            else:
                rent = apt['price']
                beds = apt['bedrooms']
            beds = str(beds) + ' Beds'
            address = apt['address']
            url = prefix + apt['detailUrl']
            a = Apt(rent, beds, address, "", url)
            apt_list.append(a)
            

    print('Found', len(apt_list))
    #get_distances(apt_list, state)

    # sort listings by rent
    #apt_list.sort(key=lambda x: x.rent)
    #csv_dump(apt_list)

