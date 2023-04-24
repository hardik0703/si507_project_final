from flask import Flask, render_template, request
import plotly.graph_objects as go 
import plotly.express as px
import zipcodes as zip
from pprint import pprint
import csv
import geonamescache
import numpy as np

# Import other files
import get_cities_v2 as gci
import get_crime_data as gcr
import get_house_prices as ghp
import search_functions as sf


'''TO DO

- make github repo properly, there are too many files here, only commit the final project files - 20

REPORT (look at the rubric): 1.5 to 2 hours
- README section in the report - 15
- data sources section - 20
- data structure - do I need to write some functions here?
- interaction and presentation section - 20
- make demo video (write script first) - 20

'''


def get_bar_plot(search_results):
    '''
    This function takes in a list of City objects and returns a bar plot of the house prices of the cities.

    Parameters:
    search_results: list
        a list of City objects
    
    Returns:
    div: string
        the html code for the bar plot
    
    '''
    x_values = [x.name for x in search_results]
    y_values = [int(y.house_price) for y in search_results]
    bars = go.Bar(x=x_values, y=y_values, orientation='v')

    layout = go.Layout(
    title='House Price by City',
    xaxis=dict(title='City', autorange=True),
    yaxis=dict(title='House Prices', autorange=True)
    )
    # sort the graph by house price, highest to lowest
    fig = go.Figure(data=bars, layout=layout)
    div = fig.to_html(full_html=False)
    return div



# The dictionary that represents the search tree (not binary, it has many branches at each node)
SEARCH_TREE = {}
# I am aware using a global variable is not a good practice, 
# but I am using it here because I need to access this variable in multiple functions.
# I could not solve for scope issues when I tried to pass this variable as an argument to the functions.

# Create a Class City
class City:
    '''
    This class represents a city and will be the unit of analysis for this project.
    '''
    def __init__(self):
        self.name = None
        self.latitude = None
        self.longitude = None
        self.population = None
        self.county = None
        self.state = None
        self.example_zipcode = None
        self.summer_high_temp = None
        self.winter_low_temp = None
        self.crime_rate = None
        self.state_population = None
        self.house_price = None
        

    def __str__(self):
        return("City Name: " + self.name + ", County: " + self.county + ", State: " + self.state + ", Population: " + str(self.population) + ", Summer High Temp: " + str(self.summer_high_temp) + ", Winter Low Temp: " + str(self.winter_low_temp)
               + ", Crime Rate: " + str(self.crime_rate) + ", State Population: " + str(self.state_population) + ", House Price: " + str(self.house_price))

def is_yes(usr_input):
    '''
    This function takes in a string and returns True if the string is a yes answer and False otherwise.

    Parameters:
    usr_input: string
        a string that represents a user input

    Returns:
    boolean

    '''

    allowed_inputs = ['yes', 'yup', 'y', 'yeah', 'sure', 'right', 'correct',
                      'yes!', 'yup!', 'y!', 'yeah!', 'sure!', 'right!', 'correct!']
    if usr_input.lower() in allowed_inputs:
        return True
    else:
        return False


def write_cities_chache(CACHE_FILE_NAME, CITIES_CACHE):
    '''
    This function takes in a list of City objects and writes them to a csv file.

    Parameters:
    CACHE_FILE_NAME: string
        the name of the csv file
    
    CITIES_CACHE: list
        a list of City objects
    '''

    with open(CACHE_FILE_NAME, 'w', encoding = 'utf-8', newline='') as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=CITIES_CACHE[0].keys())
        writer.writeheader() # first row
        writer.writerows(CITIES_CACHE)

        # writer = csv.writer(file_obj)
        # writer.writerow(CITIES_CACHE[0].__dict__.keys())
        # for row in CITIES_CACHE:
        #     row_dict = row.__dict__
        #     writer.writerow(row_dict.values())
    print('Cities cache file created.')


def write_crime_chache(CACHE_FILE_NAME, CRIME_CACHE):
    '''
    This function takes in a list of dictionaries that contain state-wise crime data and writes them to a csv file.

    Parameters:
    CACHE_FILE_NAME: string
        the name of the csv file

    CRIME_CACHE: list
        a list of dictionaries that contain state-wise crime data

    Returns:
    None
    '''

    with open(CACHE_FILE_NAME, 'w', encoding = 'utf-8', newline='') as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=CRIME_CACHE[0].keys())
        writer.writeheader() # first row
        writer.writerows(CRIME_CACHE)
    print('Crime Data cache file created.')


def write_house_prices_chache(CACHE_FILE_NAME, HOUSE_PRICES_CACHE):
    '''
    This function takes in a list of dictionaries that contain city-wise house price data and writes them to a csv file.

    Parameters:
    CACHE_FILE_NAME: string
        the name of the csv file

    HOUSE_PRICES_CACHE: list
        a list of dictionaries that contain city-wise house price data

    Returns:
    None

    '''


    with open(CACHE_FILE_NAME, 'w', encoding = 'utf-8', newline='') as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=HOUSE_PRICES_CACHE[0].keys())
        writer.writeheader() # first row
        writer.writerows(HOUSE_PRICES_CACHE)
    print('House Price cache file created.')

# GET THE DATA

# Get the cities from cache or generate them
CITIES_CACHE = []

# a list of relevant cities will be generated based on the user input
min_population = int(input("What is the minimum population of your candidate city? (It needs to be over 15000): "))

CACHE_FILE_NAME = 'cities_cache_' + str(min_population) +  '.csv'
# if the cache file exists, load the data from the file, 
# or call the function from the gci module to generate the data, and write the data to the cache file
try:
    with open(CACHE_FILE_NAME, 'r', encoding = 'utf-8') as file_obj:
        reader = csv.DictReader(file_obj, delimiter=',')
        for row in reader:
            CITIES_CACHE.append(row)
    print('Loaded ' + str(len(CITIES_CACHE)) + ' cities from cache.')
except:
    print(f'\nNo cache file found for cities with population over {min_population}. Generating data from python libraries...')
    CITIES_CACHE = gci.get_cities(min_population)
    write_cities_chache(CACHE_FILE_NAME, CITIES_CACHE)

# Get the crime data from cache or generate them
CRIME_CACHE = []
CACHE_FILE_NAME = 'crime_cache.csv'
try:
    with open(CACHE_FILE_NAME, 'r', encoding = 'utf-8') as file_obj:
        reader = csv.DictReader(file_obj, delimiter=',')
        for row in reader:
            CRIME_CACHE.append(row)
    print('Loaded all ' + str(len(CRIME_CACHE)) + ' states crime data from cache.')
except:
    print('\nNo cache file found for crime data. Fetching data from API...')
    CRIME_CACHE = gcr.get_data()
    write_crime_chache(CACHE_FILE_NAME, CRIME_CACHE)

# Get the house price data from cache or generate them
HOUSE_PRICES_CACHE = []
CACHE_FILE_NAME = 'house_prices_cache.csv'
try:
    with open(CACHE_FILE_NAME, 'r', encoding = 'utf-8') as file_obj:
        reader = csv.DictReader(file_obj, delimiter=',')
        for row in reader:
            HOUSE_PRICES_CACHE.append(row)
    print('Loaded ' + str(len(HOUSE_PRICES_CACHE)) + ' house prices data from cache.')
except:
    print('\nNo cache file found for house prices data. Fetching data from source CSV file with multi-year data...')
    HOUSE_PRICES_CACHE = ghp.get_data()
    write_house_prices_chache(CACHE_FILE_NAME, HOUSE_PRICES_CACHE)

# create class 'City' objects from the cities cache (which is a list of dictionaries)
cities = []
for city in CITIES_CACHE:
    new_city = City()
    new_city.name = city['name']
    new_city.latitude = city['latitude']
    new_city.longitude = city['longitude']
    new_city.population = city['population']
    new_city.county = city['county']
    new_city.state = city['state']
    new_city.example_zipcode = city['example_zipcode']
    new_city.summer_high_temp = city['summer_high_temp']
    new_city.winter_low_temp = city['winter_low_temp']
    cities.append(new_city)

# add crime and state population data to the city objects
# for every city, scan the CRIME_CACHE for the correct state, and add the crime rate and population data to the city object
for city in cities:
    for state_entry in CRIME_CACHE:
        if city.state == state_entry['state']:
            city.crime_rate = state_entry['crime rate']
            city.state_population = state_entry['population']
            break
print('\nAdded state-wise aggregate crime-rate data to the cities in that state.')


# add the house price data to the city objects
# for every city, scan the HOUSE_PRICES_CACHE for the correct city, and add the house price data to the city object
# some city names are slightly different in the two datasets, so we miss out on some data
for city in cities:
    for city_entry in HOUSE_PRICES_CACHE:
        if city.name == city_entry['City']:
            city.house_price = city_entry['Price']
            break
print('\nAdded house price data to the cities.')

# discard the entries without house price data or crime data
cities = [city for city in cities if city.house_price != None and city.crime_rate != None]
print('\nOnly ' + str(len(cities)) + ' cities have both house price and crime data. Discarding the remaining ' + str(len(CITIES_CACHE) - len(cities)) + ' cities.')
print('\nData is now fully ready!')

'''
# Write the final cities to a CSV file - this is for debugging purposes
with open('cities_testing.csv', 'w', encoding = 'utf-8', newline='') as file_obj:
    writer = csv.DictWriter(file_obj, fieldnames=cities[0].__dict__.keys())
    writer.writeheader() # first row
    for row in cities:
        row_dict = row.__dict__
        writer.writerow(row_dict)
'''


# ANALYSIS AND PLOTTING SECTION
# plot correlation between house prices and crime rate
x_values = [float(x.crime_rate)*1000 for x in cities]
y_values = [int(y.house_price) for y in cities]
scatter = go.Scatter(x=x_values, y=y_values)
fig_price_crime = px.scatter(x=x_values, y=y_values, title='House Price vs. Crime Rate')

# plot correlation between house prices and weather
x_values = [float(x.summer_high_temp) for x in cities]
y_values = [int(y.house_price) for y in cities]
scatter = go.Scatter(x=x_values, y=y_values)
fig_price_sum_temp = px.scatter(x=x_values, y=y_values, title='House Price vs. Summer High Temperature')

# plot correlation between house prices and weather
x_values = [float(x.winter_low_temp) for x in cities]
y_values = [int(y.house_price) for y in cities]
scatter = go.Scatter(x=x_values, y=y_values)
fig_price_winter_temp = px.scatter(x=x_values, y=y_values, title='House Price vs. Winter Low Temperature')

# plot correlation between house prices and population
x_values = [float(x.population) for x in cities]
y_values = [int(y.house_price) for y in cities]
scatter = go.Scatter(x=x_values, y=y_values)
fig_price_population = px.scatter(x=x_values, y=y_values, title='House Price vs. Population')

# Run a while loop and ask user what plots they wish to see
while True:
    response = input('''
    \nLet's plot some data!
    Which correlation scatter plot would you like to see? (1, 2, 3, 4, or 5): 
    1. House Price vs. Crime Rate
    2. House Price vs. Summer High Temperature
    3. House Price vs. Winter Low Temperature
    4. House Price vs. Population
    5. Exit
    Enter Input : ''')
    if response == '1':
        print('Please open your browser to view the plot\n')
        fig_price_crime.show()
    elif response == '2':
        print('Please open your browser to view the plot\n')
        fig_price_sum_temp.show()
    elif response == '3':
        print('Please open your browser to view the plot\n')
        fig_price_winter_temp.show()
    elif response == '4':
        print('Please open your browser to view the plot\n')
        fig_price_population.show()
    elif response == '5':
        break
    else:
        print('Invalid input. Please enter a number between 1 and 5.')


# SEARCH SECTION
# make empty search tree
SEARCH_TREE = sf.make_search_tree(SEARCH_TREE)

# insert cities into the search tree
insertions = 0
for city in cities:
    sf.add_city_to_search_tree(city, SEARCH_TREE)
    insertions += 1
print('\nInserted ' + str(insertions) + ' cities into the search tree.')
# pprint(SEARCH_TREE)

# Sanity Check - count the number of cities in the search tree
# print(sf.do_sanity_count_check(SEARCH_TREE))

# Sample Search
# sresults = SEARCH_TREE['price 200-400k']['crime rare']['summer temp 90-100']['winter temp 40-50']
# for r in sresults:
    # pprint(r.name)

# Start Search tool
print('\nWelcome to the city search tool. You can search for cities based on a few criteria.')
response = input('Please type yes to proceed. [You will need to click on the URL in the terminal below to run the flask app] : ')


if is_yes(response):
    # RUN THE FLASK APP
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search_zipcodes')
    def search():
        return render_template('search_new.html')

    @app.route('/handle_search', methods=['POST'])
    def handle_search():
        house_price = str(request.form['price'])
        crime_rate = str(request.form['Crime Rate'])
        avg_summer_high = str(request.form['summer_temp'])
        avg_winter_low = str(request.form['winter_temp'])

        search_results = SEARCH_TREE[house_price][crime_rate][avg_summer_high][avg_winter_low]
        if search_results == []:
            return "Sorry, there are no cities that match your search criteria. Please try again."
        return render_template('search_results_new.html', search_results=search_results, plot_div=get_bar_plot(search_results))

    app.run(debug=True, use_reloader=False)
else:
    pass

print('Thank you for interacting with this tool. Goodbye!')


# if __name__ == "__main__":
    # main()
