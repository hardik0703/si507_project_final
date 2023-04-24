import zipcodes as zip
from pprint import pprint
import csv
import geonamescache
import numpy as np
import meteostat
from datetime import datetime


def get_cities(min_population):
    '''
    This function returns a list of dictionaries, where each dictionary is a city
    It used multiple python libraries to get the data.
    1. geonamescache: to get the list of all cities in the world
    2. Python Zipcodes: to get the county and state of each city
    3. Meteostat: to get the weather data for each city

    Parameters:
    min_population (int): minimum population of the city to be included in the list

    Returns:
    cities_list (list): list of dictionaries, where each dictionary is a city with its attributes
    '''

    # get all cities globally from this database
    gc = geonamescache.GeonamesCache()
    cities_global = gc.get_cities()
    print('\nDownloaded info on ' + str(len(cities_global.keys())) + ' cities from geonamescache library.')

    # get all cities in the US with population over the stated minimum
    cities_list = []
    for id, city_info in cities_global.items():
        if city_info['countrycode'] == 'US' and cities_global[id]['population'] > min_population:
            city_dict = {}
            city_dict['name'] = city_info['name']
            city_dict['latitude'] = city_info['latitude']
            city_dict['longitude'] = city_info['longitude']
            city_dict['population'] = city_info['population']
            city_dict['countrycode'] = city_info['countrycode']
            cities_list.append(city_dict)

    print('\nWe have now shortlisted ' + str(len(cities_list)) + ' cities in the US with population over ' + str(min_population) + '.')

    # Download all the zipcodes in the US using the Python Zipcodes library
    zipcodes_list = zip.filter_by(country="US")
    print('\nAdding county and state to each city object from the Python Zipcodes library...')
    print('Downloaded info on all ' + str(len(zipcodes_list)) + ' zipcodes in the US.')

    # get the county and state of each city using the closest latitude and longitude
    for city in cities_list:
        city['county'], city['state'], city['example_zipcode'] = get_close_lat_long(zipcodes_list, city['latitude'], city['longitude'])
    print('\nSuccessfully added county and state to each city object using closest coordinate mapping.')

    # WEATHER DATA
    '''
    Meteostat also has an API but it is via rapid API and it is paid. 
    So I am using the python library of meteostat to extract the data.
    Similar issue with openweathermap API, it is paid after the first 1000 calls in a day. 
    And since I need data for potentially thousands of locations, I cannot use it.
    '''

    # now get weather data for each city

    # setting the start time and the end time period for the weather data
    start_weather_data = datetime.strptime('01/01/18', '%m/%d/%y')
    end_weather_data = datetime.strptime('12/31/22', '%m/%d/%y')


    progress_counter = 0
    data_not_found = 0
    print('\nGetting weather data for each city from the Python Meteostat Library...')
    for city in cities_list:
        # get the weather data for each city, from a weather station within a 10 mile radius of the given latitude and longitude
        loc = meteostat.Point(float(city['latitude']), float(city['longitude']), 10)
        data_m = meteostat.Monthly(loc, start_weather_data, end_weather_data).fetch()

        # calculate the summer high temperature and winter low temperature for each city 
        city['summer_high_temp'], city['winter_low_temp'] = calc_weather_params(data_m)

        # show progress in steps of ~25%
        progress_counter += 1
        if abs((progress_counter*100/len(cities_list))%25 - 25) <0.8:
            print('   ...' + str(round(progress_counter/len(cities_list),2) * 100) + '% done')

        # if weather data is not found for a city, keep track of it
        if city['summer_high_temp'] == None or city['winter_low_temp'] == None:
            data_not_found += 1

    print('\nFound weather data for ' + str(len(cities_list) - data_not_found) + ' cities out of ' + str(len(cities_list)) + ' cities. Discarded ' + str(data_not_found) + ' cities.\n')

    # Discard cities for which weather data was not found
    cities_list = [city for city in cities_list if city['summer_high_temp'] != None and city['winter_low_temp'] != None]

    return cities_list


def get_close_lat_long(zipcodes_list, lat, long):
    '''
    This function takes in a latitude and longitude and returns the closest zipcode to it, 
    along with the county and state of that zipcode.

    Parameters:
    lat: float 
        the latitude of the location
    long: float 
        the longitude of the location

    Returns:
    county: string
        the county of the closest zipcode
    state: string
        the state of the closest zipcode
    zipcode: string
        the zipcode of the closest zipcode
    '''
    for zipcode in zipcodes_list:
        if abs(float(zipcode['lat']) - float(lat)) < 0.1 and abs(float(zipcode['long']) - float(long)) < 0.1:
            return zipcode['county'], zipcode['state'], zipcode['zip_code']
    return None


def calc_weather_params(data_m):
    '''
    This function takes in a dataframe of weather data and calculates the average high temperature for the month 
    of July and August, and the average low temperature for the month of December and January.

    Parameters:
    data_m: dataframe from meteostat library

    Returns:
    avg_high_temp: float
        the average high temperature for the month of July and August
    avg_low_temp: float
        the average low temperature for the month of December and January

    '''
    try:
        # calculate the average high temperature for the month of July and August. 
        # Using numpy.nanmean to ignore the NaN values, as many of the cities do not have data for all the months, 
        # or, in some cases, none of the months
        avg_high_temp = np.nanmean([data_m.iloc[6, 2], data_m.iloc[7, 2], data_m.iloc[18, 2], data_m.iloc[19, 2], data_m.iloc[30, 2], data_m.iloc[31, 2], data_m.iloc[42, 2], data_m.iloc[43, 2]])
    except:
        avg_high_temp = None
    try:
        avg_low_temp = np.nanmean([data_m.iloc[11, 1], data_m.iloc[12, 1], data_m.iloc[23, 1], data_m.iloc[24, 1], data_m.iloc[35, 1], data_m.iloc[36, 1], data_m.iloc[47, 1], data_m.iloc[48, 1]])
    except:
        avg_low_temp = None
    # convert to fahrenheit
    try:
        avg_high_temp = round((avg_high_temp * 9/5) + 32, 2)
    except:
        avg_high_temp = None
    try:
        avg_low_temp = round((avg_low_temp * 9/5) + 32, 2)
    except:
        avg_low_temp = None
    return avg_high_temp, avg_low_temp


'''
def main():
    # get the list of cities
    cities_list = get_cities()
    for city in cities_list[0:13]:
        pprint(city)

if __name__ == '__main__':
    main()

'''
