import sys
import requests
import re
import time
from dotenv import dotenv_values
from Apt import Apt, csv_dump


def get_listings(location, is_rental, rent, beds):

    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

    # TODO make sure location is valid?

    is_rental = True
    status_type = ''

    # TODO remove this if results are bad
    sort = 'Newest'

    rentMinPrice = str(rent - 500)
    rentMaxPrice = str(rent)
    bedsMin = str(beds)

    if is_rental:
        status_type = 'ForRent'
    else:
        status_type = 'ForSale'

    querystring = {
                "location": location,
                "status_type":status_type,
                "sort": sort,
                "rentMinPrice": rentMinPrice,
                "rentMaxPrice": rentMaxPrice,
                "bedsMin": bedsMin
                }

    env = dotenv_values('.env')
    headers = {
        "x-rapidapi-key": env["API_KEY"],
        "x-rapidapi-host": "zillow-com1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
    listings = data['props']

    prefix = 'https://www.zillow.com'

    apt_list = []
    for apt in listings:
        print(apt)
        #skip for now
        if 'units' in apt:
            continue 
        rent = apt['price']
        beds = apt['bedrooms']
        address = apt['address']
        url = prefix + apt['detailUrl']
        a = Apt(rent, beds, address, "", url)
        apt_list.append(a)

    print(len(apt_list))
    csv_dump(apt_list)


if __name__ == '__main__':
    #env = dotenv_values('.env')
    location = 'Cambridge, MA'
    is_rental = True
    rent = 3700
    beds = 2
    get_listings(location, is_rental, rent, beds)
