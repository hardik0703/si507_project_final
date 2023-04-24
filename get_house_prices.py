import csv
from pprint import pprint

# Notes on data sources
# I explored Zillow's API, but it requires a paid subscription.
# Instead, I found a dataset on Kaggle that contains house price data for top US cities
# https://www.kaggle.com/datasets/paultimothymooney/zillow-house-price-data


SOURCE_FILE = 'Sale_Prices_city.csv'
def get_data():
    '''
    This function returns a list of dictionaries

    Returns:
    house_prices_trimmed (list): list of dictionaries, where each dictionary is a city with house price info
    '''
    house_prices = []

    # read the csv file
    with open(SOURCE_FILE, 'r', encoding = 'utf-8') as file_obj:
        reader = csv.DictReader(file_obj, delimiter=',')
        for row in reader:
            house_prices.append(row)
    
    # retain data only from 3 columns - RegionName, StateName, 2019-08 (price)
    house_prices_trimmed = []
    for row in house_prices:
        house_prices_trimmed.append({
            'City': row['RegionName'],
            'State': row['StateName'],
            'Price': row['2019-08']          
        })

    return house_prices_trimmed

'''
def main():
    house_prices_final = get_data()
    # pprint(house_prices_final[0:3])
    print(len(house_prices_final))

if __name__ == '__main__':
    main()
'''