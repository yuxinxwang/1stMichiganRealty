from lxml import html
import requests
import unicodecsv as csv
import argparse
from urllib.request import Request, urlopen
import json
import pandas as pd
import os


def load_raw_json(data_path):
    with open(data_path, 'r') as in_file:
        raw_json_data = in_file.read().replace('\n', '')

    raw_json_data = raw_json_data.replace('"<!--', "").replace('-->"', "")

    raw_json_data = raw_json_data.replace(r'\"', '"')
    # print(raw_json_data[145680:145690])
    # raw_json_data = raw_json_data[:-1]
    # print(len(raw_json_data))
    clean_json_data = json.loads(raw_json_data)
    return clean_json_data


def get_data_from_json(json_data):
    properties_list = []

    try:
        # json_data = json.loads(json_data)
        # print(type(json_data))
        # print(json_data.keys())
        try:
            search_results = json_data['cat1']
            search_results = search_results["searchResults"]
        except:
            search_results = json_data['searchResults']

        search_results = search_results['listResults']

        for properties in search_results:
            address = properties.get('address')
            # latlong = properties.get('latLong')
            img = properties.get('imgSrc')
            property_info = properties.get('hdpData', {}).get('homeInfo', {})
            zestimate = property_info.get('zestimate')
            rentZestimate = property_info.get('rentZestimate')
            daysOnZillow = property_info.get('daysOnZillow')
            photoCount = property_info.get('photoCount')
            lat = property_info.get('latitude')
            long = property_info.get('longitude')
            city = property_info.get('city')
            state = property_info.get('state')
            postal_code = property_info.get('zipcode')
            price = property_info.get('price')
            bedrooms = properties.get('beds')
            bathrooms = properties.get('baths')
            area = properties.get('area')
            info = f'{bedrooms} bds, {bathrooms} ba ,{area} sqft'
            broker = properties.get('brokerName')
            property_url = properties.get('detailUrl')
            title = properties.get('statusText')

            data = {'address': address,
                    'city': city,
                    'state': state,
                    'postal_code': postal_code,
                    'price': price,
                    'facts and features': info,
                    'real estate provider': broker,
                    'url': property_url,
                    'title': title,
                    'property_info': property_info,
                    'img': img,
                    'zestimate': zestimate,
                    'daysOnZillow': daysOnZillow,
                    'rentZestimate': rentZestimate,
                    'lat': lat,
                    'long': long}
            properties_list.append(data)

        return properties_list

    except ValueError:
        print("Invalid json")
        return None

def list_to_df(properties_list):
    if properties_list is None:
        return pd.DataFrame()
    else:
        return pd.DataFrame(properties)

if __name__=='__main__':
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('filename', help='')

    args = argparser.parse_args()
    filename = args.filename

    DIR = os.path.join(filename)
    DIR_JSON = os.path.join(DIR, "raw_data.json")

    json_data = load_raw_json(DIR_JSON)
    properties = get_data_from_json(json_data)
    print('Parsed json successfully!')
    df = pd.DataFrame(properties)
    df.to_csv(os.path.join(DIR, "output.csv"), index=False)
    print('Data saved to \n', os.path.join(DIR, "output.csv"))
