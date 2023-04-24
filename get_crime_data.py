import requests
import json
from pprint import pprint
import csv

# Note on data sources. 
# There are API's with population at the county or fips_code level. 
# For instance, I could have used the census API and aggregated the data at the state level. 
# I chose to use a self-made csv file for the sake of simplicity.

# get the list of states and their population from a csv file
STATES_LIST = []
with open('state_list.csv', 'r', encoding = 'utf-8-sig') as file_obj:
    reader = csv.reader(file_obj)  # alternatively, we can use DictReader
    for row in reader:
        new_dict = {}
        new_dict['state'] = row[0]
        new_dict['full_name'] = row[1]
        new_dict['population'] = row[2]
        STATES_LIST.append(new_dict)


# pprint(STATES_LIST)

def construct_url(state):
    '''
    This function constructs the url for the crime API.

    Parameters:
    state (str): state for which the crime data is needed

    Returns:
    url (str): url for the API call
    params (dict): parameters for the API call
    
    '''
    # api documentation: https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi
    # sample api = https://api.usa.gov/crime/fbi/cde/arrest/state/CA/all?from=2020&to=2022&API_KEY=WfbWxVqRDseuwGbOzoIMhNQyVKBWy01Fc7yoiay9
    baseurl = 'https://api.usa.gov/crime/fbi/cde'
    endpoint = '/arrest/state'
    with open('crime_api_key.txt', 'r') as f:
        api_key = f.read()
    state_param = '/' + str(state)
    crime_type_param = '/all'
    # taking a 3 year average
    params = {'api_key': api_key, 'from': 2019, 'to': 2022}
    url = baseurl + endpoint + state_param + crime_type_param
    return url, params

def get_data():
    '''
    This function gets the crime data for each state and calculates the crime rate for each state.
    
    Parameters:
    None

    Returns:
    STATES_LIST (list): list of dictionaries with crime data for each state
    
    '''
    
    progress_counter = 0
    print('Downloading crime data for all states...')
    for state in STATES_LIST:
        # call the API
        url, params = construct_url(state['state'])
        data = requests.get(url, params=params).json()['data']
        # pprint(data, depth=2)

        # process the data
        total_crime = 0
        for crime_dict in data:
            for k, v in crime_dict.items():
                if k != 'data_year':
                    total_crime += v
        # print(total_crime)
    
        crime_rate = total_crime / int(state['population'])
    
        # taking a 3 year average
        crime_rate = round(crime_rate/3, 4)
        # print(str(crime_rate*100)+'%')

        # add the crime data to the dictionary
        state['crime rate'] = crime_rate

        # print progress every 20%
        progress_counter += 1
        if abs((progress_counter*100/len(STATES_LIST))%20 == 0):
            print('   ...' + str(round(progress_counter/len(STATES_LIST),2) * 100) + '% done')

    return STATES_LIST


'''
def main():
    # get crime data for each state
    crime_data = get_data()
    pprint(crime_data)


if __name__ == '__main__':
    main()
'''