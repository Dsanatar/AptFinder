import time
import csv

class Apt:
    def __init__(self, rent, beds, address, city, url):
        self.rent = rent
        self.address = address
        self.beds = beds
        self.distance = 0
        self.distance_to = ""
        self.city = city
        self.url = url

    def get_city(self):
        return self.city
    
    def set_distance(self, dist):
        self.distance = dist

    def set_dist_loc(self, loc):
        self.distance_to = loc

    def get_data(self):
        data = [self.rent, self.beds, self.address, self.distance_to, self.distance, self.url]
        return data

    def __str__(self):
        return f"{self.rent} | {self.beds} | {self.address}| {self.distance} | closet = {self.distance_to} | {self.url}"



def csv_dump(apt_list):
    timestr = time.strftime("%m-%d-%Y-%H%M%S")
    file_path = "output/" + timestr + ".csv"
    with open(file_path, "w", newline='') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(['sep=|'])
        writer.writerow(['Rent', 'Beds', 'Address', 'Distance', 'T Stop', 'Link'])
        for apt in apt_list:
            writer.writerow(apt.get_data())