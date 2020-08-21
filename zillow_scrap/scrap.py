from lxml import html
import requests
import unicodecsv as csv
import argparse
from urllib.request import Request, urlopen
import json
import pandas as pd
import os
from parse_json import list_to_df, load_raw_json, get_data_from_json


def clean(text):
    if text:
        return ' '.join(' '.join(text).split())
    return None


def get_headers():
    # Creating headers.
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'accept-encoding': 'gzip, deflate, sdch, br',
               'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
               'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
    return headers


def create_url(city_name):
    """ Generates url to scrap
    Args:
        city_name (str): city name, such as "Novi,MI" (notice no space)
    Returns:
        url (str): a zillow url to scrap

    """

    url = "https://www.zillow.com/homes/for_sale/{0}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(city_name)

    return url

def save_to_html(response):
    # saving response to `response.html`
    with open("response.html", 'w') as fp:
        fp.write(response.text)


def get_response(url):
    """ Get response from Zillow
    Args:
        url (str): the url to scrap
    Returns:
        response if exists, None otherwise
    """
    for i in range(5):
        response = requests.get(url, headers=get_headers())
        print("status code received:", response.status_code)

        if response.status_code != 200:
            # Error receiving response
            # saving response to file for debugging purpose.
            save_to_file(response)
            return None

        save_to_file(response)
        return response



def get_data_from_json(raw_json_data):
    # getting data from json (type 2 of their A/B testing page)

    cleaned_data = clean(raw_json_data).replace(r'\"', '"').replace(r'"<!--', "").replace('-->\"', "")
    # cleaned_data = cleaned_data.replace(r'\"', '"')
    assert ('\"' not in cleaned_data)
    properties_list = []

    try:
        json_data = json.loads(cleaned_data)[0]
        search_results = json_data.get("searchResults").get('listResults', [])

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


def parse(zipcode, OUTPUT_DIR):

    # Generate url
    url = create_url(zipcode)

    # Obtain request
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    # Parse response
    if not req:
        # Failure, parsing aborted.
        print("Failed to fetch the page, please check `response.html` to see the response received from zillow.com.")
        return None

    webpage = urlopen(req).read()
    parser = html.fromstring(webpage)
    search_results = parser.xpath("//div[@id='search-results']//article")

    if not search_results:
        print("Saving data to json...")
        # identified as type 2 page
        raw_json_data = parser.xpath('//script[@data-zrr-shared-data-key="mobileSearchPageStore"]//text()')
        try:
            raw_json_data = clean(raw_json_data)
            raw_json_data = raw_json_data.replace('"<!--', "").replace('-->"', "")

        except:
            pass
        with open(os.path.join(OUTPUT_DIR, 'raw_data.json'), 'w') as outfile:
            json.dump(raw_json_data, outfile)
        return None

    print("parsing from html page")
    properties_list = []
    for properties in search_results:
        raw_address = properties.xpath(".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()")
        raw_city = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()")
        raw_state = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()")
        raw_postal_code = properties.xpath(".//span[@itemprop='address']//span[@itemprop='postalCode']//text()")
        raw_price = properties.xpath(".//span[@class='zsg-photo-card-price']//text()")
        raw_info = properties.xpath(".//span[@class='zsg-photo-card-info']//text()")
        raw_broker_name = properties.xpath(".//span[@class='zsg-photo-card-broker-name']//text()")
        url = properties.xpath(".//a[contains(@class,'overlay-link')]/@href")
        raw_title = properties.xpath(".//h4//text()")

        address = clean(raw_address)
        city = clean(raw_city)
        state = clean(raw_state)
        postal_code = clean(raw_postal_code)
        price = clean(raw_price)
        info = clean(raw_info).replace(u"\xb7", ',')
        broker = clean(raw_broker_name)
        title = clean(raw_title)
        property_url = "https://www.zillow.com" + url[0] if url else None
        is_forsale = properties.xpath('.//span[@class="zsg-icon-for-sale"]')

        properties = {'address': address,
                      'city': city,
                      'state': state,
                      'postal_code': postal_code,
                      'price': price,
                      'facts and features': info,
                      'real estate provider': broker,
                      'url': property_url,
                      'title': title}
        if is_forsale:
            properties_list.append(properties)
    return properties_list


if __name__ == "__main__":

    # Reading arguments
    argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('city_name', help='')
    args = argparser.parse_args()
    city_name = args.city_name


    # Create directory to save scrapped data
    TODAY = pd.to_datetime('today').strftime('%Y%m%d_%H%M')
    if not os.path.exists(os.path.join('output', city_name, TODAY)):
        os.makedirs(os.path.join('output', city_name, TODAY))
    OUTPUT_DIR = os.path.join('output', city_name, TODAY)

    # Scrap data
    print ("Fetching data for %s" % (city_name))
    scraped_data = parse(city_name, OUTPUT_DIR)


    if scraped_data is not None:
        df = pd.DataFrame(scraped_data)

        if not os.path.exists(os.path.join('output', city_name)):
            os.makedirs(os.path.join('output', zipcode))
        df.to_csv(os.path.join(OUTPUT_DIR, 'output.csv'), index=False)
    else:
        # Parse json
        print('Need to parse data from json...')
        print('The json file is located at', OUTPUT_DIR)

        # json_data = load_raw_json(os.path.join(OUTPUT_DIR, 'raw_data.json'))
        # properties = get_data_from_json(json_data)
        # df = list_to_df(properties)
