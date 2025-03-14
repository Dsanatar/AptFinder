import configparser
from zillow_api import get_listings
from apt_scraper import scrape_apts
from Apt import csv_dump

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    # grab user inputs out of ini
    city = config['search']['city']
    state = config['search']['state']
    is_rental = config.getboolean('search', 'is_rental')
    rent = int(config['search']['rent'])
    beds = int(config['search']['beds'])
    move_in_date = config['search']['move_in_date']

    apt_list = []

    get_listings(city, state, is_rental, rent, beds, move_in_date, apt_list)
    print(len(apt_list))
    scrape_apts(city, state, beds, rent, apt_list)

    print(len(apt_list))

    #sort listings by rent
    #apt_list.sort(key=lambda x: x.rent)

    csv_dump(apt_list)


