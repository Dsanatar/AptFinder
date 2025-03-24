import sys
import configparser
from zillow_api import get_zillow
from apt_scraper import scrape_apts
from Apt import csv_dump
from distance import get_distances

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    # grab user inputs out of ini
    city_list = config['search']['city'].split(',')
    state = config['search']['state']
    is_rental = config.getboolean('search', 'is_rental')
    rent = int(config['search']['rent'])
    beds = int(config['search']['beds'])
    move_in_date = config['search']['move_in_date']
    calc_dist = config.getboolean('search', 'do_distance')
    two_source = config.getboolean('search', 'do_both')

    print('searching: ', city_list)

    apt_list = []

    get_zillow(city_list, state, is_rental, rent, beds, move_in_date, apt_list)

    if two_source:
        scrape_apts(city_list, state, beds, rent, apt_list)

    if calc_dist:
        get_distances(apt_list, state)

    #sort listings by rent
    #apt_list.sort(key=lambda x: x.rent)

    csv_dump(apt_list, calc_dist)


