import csv
from pprint import pprint

# read data from cities_data_structure.csv into a list of dictionaries and print the first 5 rows
with open('cities_data_structure.csv', 'r') as f:
    reader = csv.DictReader(f)
    cities_data = [row for row in reader]

pprint(cities_data[:5])