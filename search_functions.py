from pprint import pprint
import csv

def make_search_tree(search_tree):
    '''
    This function creates a nested dictionary that represents the search tree.

    Parameters:
    search_tree (dict): an empty dictionary

    Returns:
    search_tree (dict): a nested dictionary that represents the search tree
    '''

    # first level of branches in the tree is price
    search_tree['price below 200k'] = {}
    search_tree['price 200-400k'] = {}
    search_tree['price 400-600k'] = {} # price 400-600k
    search_tree['price above 600k'] = {}

    # second level of the tree is crime
    # for each price bucket (a dict itself), create a key-value pair of crime rate buckets
    for price_bucket in search_tree.values():
        price_bucket['crime rare'] = {}  # crime rate < 0.0165
        price_bucket['crime medium'] = {}  # crime rate 0.0165-0.02
        price_bucket['crime frequent'] = {}  # crime rate > 0.02
    
    # third level of the tree is summer high temp
    # for each crime rate bucket (a dict itself), create a key-value pair of summer high temp buckets
    for price_bucket in search_tree.values():
        for crime_bucket in price_bucket.values():
            crime_bucket['summer temp below 90'] = {}
            crime_bucket['summer temp 90-100'] = {}
            crime_bucket['summer temp above 100'] = {}

    # fourth level of the tree is winter low temp
    # for each summer high temp bucket (a dict itself), create a key-value pair of winter low temp buckets
    # note that the values here are empty lists, and not dictionaries like the previous levels
    # this is because we will be appending cities to these lists
    for price_bucket in search_tree.values():
        for crime_bucket in price_bucket.values():
            for summer_temp_bucket in crime_bucket.values():
                summer_temp_bucket['winter temp below 40'] = []
                summer_temp_bucket['winter temp 40-50'] = []
                summer_temp_bucket['winter temp above 50'] = []
    
    print('\nSuccessfully created an empty search tree')
    return search_tree

def add_city_to_search_tree(city, search_tree):
    '''
    This function adds a city to the search tree.

    Parameters:
    city (City): a City class object
    search_tree (dict): a nested dictionary that represents the search tree

    Returns:
    None
    
    '''

    price_key = lookup_house_price(city.house_price)
    crime_key = lookup_crime_rate(city.crime_rate)
    summer_temp_key = lookup_summer_temp(city.summer_high_temp)
    winter_temp_key = lookup_winter_temp(city.winter_low_temp)
    search_tree[price_key][crime_key][summer_temp_key][winter_temp_key].append(city)


def lookup_house_price(house_price):
    '''
    This function returns a key for the search tree based on the house price.

    Parameters:
    house_price (str): house price

    Returns:
    key (str): a key for the search tree
    '''

    if int(house_price) < 200000:
        return 'price below 200k'
    elif int(house_price) < 400000:
        return 'price 200-400k'
    elif int(house_price) < 600000:
        return 'price 400-600k'
    else:
        return 'price above 600k'
    
def lookup_crime_rate(crime_rate):
    '''
    This function returns a key for the search tree based on the crime rate
    '''
    if float(crime_rate) < 0.0165:
        return 'crime rare'
    elif float(crime_rate) < 0.025:
        return 'crime medium'
    else:
        return 'crime frequent'
    
def lookup_summer_temp(summer_temp):
    '''
    This function returns a key for the search tree based on the summer high temp
    '''
    if float(summer_temp) < 90:
        return 'summer temp below 90'
    elif float(summer_temp) < 100:
        return 'summer temp 90-100'
    else:
        return 'summer temp above 100'
    
def lookup_winter_temp(winter_temp):
    '''
    This function returns a key for the search tree based on the winter low temp
    '''
    if float(winter_temp) < 40:
        return 'winter temp below 40'
    elif float(winter_temp) < 50:
        return 'winter temp 40-50'
    else:
        return 'winter temp above 50'
    
def do_sanity_count_check(search_tree):
    '''
    This function does a sanity check on the search tree to make sure that 
    the total number of cities in the tree is correct.

    Parameters:
    search_tree (dict): a nested dictionary that represents the search tree

    Returns:
    None
    '''
    count = 0
    for price_bucket in search_tree.values():
        for crime_bucket in price_bucket.values():
            for summer_temp_bucket in crime_bucket.values():
                for winter_temp_bucket in summer_temp_bucket.values():
                    count += len(winter_temp_bucket)
    return f'Sanity check: total number of cities in the search tree is {count}'

