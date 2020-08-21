from lxml import html
import requests
import unicodecsv as csv
from urllib.request import Request, urlopen
import argparse
import json
import pandas as pd

argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
argparser.add_argument('filename', help='')

args = argparser.parse_args()
filename = args.filename

filename = filename.replace(".csv", "").strip()

df = pd.read_csv(filename+'.csv')

try:
    df['price'] = df['price'].astype(float)
except:
    df['price'] = df['price'].apply(lambda x: float(x.replace('$', '').replace(',', '')))

df = df.loc[df['daysOnZillow'] <= 15]

MIN_PRICE = 300000
MAX_PRICE = 550000
df = df.loc[(df['price']>=MIN_PRICE) & (df['price']<=MAX_PRICE)]

print("There are %s records in total" %(len(df)))
print(df[['price', 'daysOnZillow']])
print('------------------------')
user_input = input("Proceed? press control+Z to kill the program. ")

def read_url(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

    if not req:
        print("Failed to fetch the page, please check `response.html` to see the response received from zillow.com.")
        return None

    # req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    # parser = html.fromstring(response.text)
    parser = html.fromstring(webpage)


    try:
        saves = parser.xpath('//*[@id="ds-data-view"]/ul/li[2]/div/div/div[1]/div[3]/div[3]/div[2]')[0].text
        views = parser.xpath('//*[@id="ds-data-view"]/ul/li[2]/div/div/div[1]/div[3]/div[2]/div[2]')[0].text

        '//*[@id="ds-data-view"]/ul/li[3]/div/div[3]/div[1]/div[2]'

        return (saves, views)

    except:
        try:
            views = parser.xpath('//*[@id="ds-data-view"]/ul/li[3]/div/div[3]/div[1]/div[2]')[0].text
            saves = parser.xpath('//*[@id="ds-data-view"]/ul/li[3]/div/div[3]/div[2]/div[2]')[0].text
        except:
            print("Unable to find item from", url)
            return (-1,-1)


out = df['url'].apply(read_url)

df['saves'], df['views'] = zip(*out)
df.to_csv(filename+'_views_saves.csv', index=False)

# for i, row in df.iterrows():
#     url = row['url']
#     print(url)
#     print(read_url(url))

# df.to_csv('test_out.csv')
