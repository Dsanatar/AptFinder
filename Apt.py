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

    def get_data(self, has_dist):
        if has_dist:
            return [self.rent, self.beds, self.address, self.distance_to, self.distance, self.url]
        else:
            return [self.rent, self.beds, self.address, self.url]

    def __str__(self):
        return f"{self.rent} | {self.beds} | {self.address}| {self.distance} | closet = {self.distance_to} | {self.url}"



def csv_dump(apt_list, has_dist):
    timestr = time.strftime("%m-%d-%Y-%H%M%S")
    file_path = "output/" + timestr + ".csv"
    with open(file_path, "w", newline='') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(['sep=|'])
        if has_dist:
            writer.writerow(['Rent', 'Beds', 'Address', 'Distance', 'T Stop', 'Link'])
        else:
            writer.writerow(['Rent', 'Beds', 'Address', 'Link'])
            
        for apt in apt_list:
            writer.writerow(apt.get_data(has_dist))