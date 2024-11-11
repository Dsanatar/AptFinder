import sys
import requests
from bs4 import BeautifulSoup

class Apt:
    def __init__(self, rent, address):
        self.rent = rent
        self.address = address
    def __str__(self):
        return f"{self.rent} @ {self.address}"

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

    bed_query = '"beds":{"min":' + str(beds) + ',"max":' + str(beds) + '},'
    price_query ='"mp":{"max":' + str(price) + '},"price":{"max":678881},'
    
    apt_list = []
    for page in range(1,4):
        query = '/rentals/?searchQueryState={"pagination":{"currentPage":' + str(page) + '},"isMapVisible":true,"mapBounds":{"west":-71.20319402978515,"east":-71.02123297021484,"south":42.32359097463271,"north":42.433152995065775},"mapZoom":12,"usersSearchTerm":"Cambridge MA","regionSelection":[{"regionId":3934,"regionType":6}],"filterState":{"fr":{"value":true},"fsba":{"value":false},"fsbo":{"value":false},"nc":{"value":false},"cmsn":{"value":false},"auc":{"value":false},"fore":{"value":false},' + bed_query + price_query +'"mf":{"value":false},"land":{"value":false},"manu":{"value":false}},"isListVisible":true}'
        #'https://www.zillow.com/cambridge-ma/rentals/?searchQueryState={"pagination":{}:"isMapVisible":true:"mapBounds":{"north":42.43315299506577:"south":42.3235909746327:"east":-71.02123297021484:"west":-71.20319402978515}:"filterState":{"fr":{"value":true}:"fsba":{"value":false}:"fsbo":{"value":false}:"nc":{"value":false}:"cmsn":{"value":false}:"auc":{"value":false}:"fore":{"value":false}:"mf":{"value":false}:"land":{"value":false}:"manu":{"value":false}:"beds":{"min":2:"max":2}:"mp":{"max":3400}:"price":{"max":678881}}:"isListVisible":true:"mapZoom":12:"regionSelection":%5B{"regionId":3934:"regionType":6}%5D:"usersSearchTerm":"Cambridge%20MA"}'
        zillow = zillow + city + state + query
        #print(zillow)

        req = requests.get(zillow, headers=headers)
        resp = req.text

        soup = BeautifulSoup(resp,'html.parser')
        #listings.extend(soup.find_all("li",{"class":"ListItem-c11n-8-106-0__sc-13rwu5a-0 StyledListCardWrapper-srp-8-106-0__sc-wtsrtn-0 hcrUex cLDGnX"}))
        for listing in soup.find_all("li",{"class":"ListItem-c11n-8-106-0__sc-13rwu5a-0 StyledListCardWrapper-srp-8-106-0__sc-wtsrtn-0 hcrUex cLDGnX"}):
            if listing.find("span",{'data-test':'property-card-price'}) == None:
                print('skipped??')
                continue
            rent = listing.find("span",{'data-test':'property-card-price'}).text
            addr = listing.find("address", {'data-test': 'property-card-addr'}).text
            apt = Apt(rent, addr)
            apt_list.append(apt)
    

    for apt in apt_list:
        print(apt)
    
    