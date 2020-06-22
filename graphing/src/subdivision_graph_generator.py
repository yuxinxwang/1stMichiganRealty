# -*- coding: utf-8 -*-
"""
subdivision_graph_generator.py
Generates graphics for subdivision
Author: Yuxin WANG
Last modified: 06/21/2020

NOTE:
(1) Remember to put in the correct CLEAN_DIR and TRANSACTION_DIR
(2) Recommended CLEAN_DIR is
        "1MR - BigData/Project 2020/City Transaction Data/OUTPUT/cleaned/
        basic_info/"
(3) Recommended TRANSACTION_DIR is
        "/content/drive/Shared drives/1MR - BigData/Project 2020/
        City Transaction Data/OUTPUT/merged_may2020/"
(4) WARNING: if TRANSACTION_DIR is not as above, the clean dataset will NOT
             merge with transaction dataset correctly, hence generating useless
             graphs
(5) Searching "TODO" will lead you to all the places where you need to fill
        in the correct paths
(6) To install plotly, try the following (omit the $ sign):
        $ pip install plotly==4.8.1
            or
        $ conda install -c plotly plotly=4.8.1
        For more information, visit
            https://plotly.com/python/getting-started/#installation
(7) To install pandas, try the following (omit the $ sign):
        $ pip install pandas
            or
        $ conda install pandas
        For more information, visit
            https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html
"""

import pandas as pd
import os
import random
import string
import plotly.graph_objects as go
from plotly.subplots import make_subplots


"""
Load dataset
"""

# Define paths
# absolute path to directory that contains clean data
## TODO:
CLEAN_DIR = None
assert os.path.exists(CLEAN_DIR), "Clean data path {} does not exist!".format(CLEAN_DIR)
# Recommend the following path:
# CLEAN_DIR = "/content/drive/Shared drives/1MR - BigData/Project 2020/City Transaction Data/OUTPUT/cleaned/basic_info/"

# absolute path to directory that contains transaction data (may be messy)
## TODO:
TRANSACTION_DIR = None
assert os.path.exists(TRANSACTION_DIR), "Transaction data path {} does not exist!".format(TRANSACTION_DIR)
# Recommend the following path:
# TRANSACTION_DIR = "/content/drive/Shared drives/1MR - BigData/Project 2020/City Transaction Data/OUTPUT/merged_may2020/"

# absolute path to directory that you want to save the data
# If the specified directory does not exist, we will create the directory
## TODO:
TARGET_PATH = os.path.join(os.getcwd(), CITY_NAME+"_graphs")
if not os.path.exists(TARGET_PATH):
    # Create dir if does not exist
    os.makedirs(TARGET_PATH, exist_ok=False)

# Define city name and subdivision name
CITY_NAME = input('City name: ').strip().lower()
SUB_NAME = input('Subdivision name: ').strip().upper()
TRANSACTION_TYPE = input('Transaction type: sale/lease: ').strip().lower()


# Define columns to use from transaction dataset
IMPORTANT_COLS = ['RATIO_Close Price Per Sqft', 'Close Price',
                  'Transaction Type', 'Ty',
                  'Beds Total', 'Est Fin Abv Grd SqFt',
                  'Est Fin Lower Floor SqFt',
                  'Garage Size', 'Baths Full', 'Baths Half', 'Close Year',
                  'Close Month', 'Close Date', 'Pending Date', 'DOM.1']

# Load clean dataset
for f in os.listdir(os.fsencode(CLEAN_DIR)):
    filename = os.fsdecode(f)
    if filename.lower().startswith(CITY_NAME.lower()):
        print("Loading clean dataset from {}".format(filename))
        df_clean = pd.read_csv(os.path.join(CLEAN_DIR, filename))
        print(" Clean dataset has been loaded!")
        break

# Load transaction dataset
for f in os.listdir(os.fsencode(TRANSACTION_DIR)):
    filename = os.fsdecode(f)
    if filename.lower().startswith(CITY_NAME.lower()):
        print("Loading transaction dataset from {}".format(filename))
        df_transaction = pd.read_csv(os.path.join(TRANSACTION_DIR, filename))
        print(" Transaction dataset has been loaded!")
        break

# Merge clean dataset with full transaction info
df_all = df_clean.merge(df_transaction[IMPORTANT_COLS].reset_index(),
                        left_on='index_raw',
                        right_on='index',
                        how='left')
df_all = df_all.drop(columns=['index_clean', 'index_raw'])
df_all['Subdivision Name'] = \
    df_all['Subdivision Name_y'].fillna(df_all['Subdivision Name_x'])

"""
Get info for subdivision
"""

# Extract relevant subdivision(s)
# extract subdivision
df_sub = df_all.loc[df_all['Subdivision Name'].fillna('').str.lower()\
                .str.contains(SUB_NAME.lower())]

# if multiple relevant subdivisions are found, user should choose one
if len(df_sub['Subdivision Name'].value_counts()) != 1:
    print("There are multiple subdivisions that are like {}".format(SUB_NAME))
    print(df_sub['Subdivision Name'].value_counts())
    SUB_NAME_new = input("""\nYour choice of subdivision is? (Please type exact subdivision name).
If you would like to keep all of these, press enter. """).strip()
    if SUB_NAME_new and len(SUB_NAME_new)>0:
        SUB_NAME = SUB_NAME_new
    df_sub = df_all.loc[df_all['Subdivision Name'].fillna('').str.lower().str.contains(SUB_NAME.lower())]


# Extract relevant transaction type
df_sub = df_sub.loc[df_sub['Transaction Type'].str.lower()\
                    == TRANSACTION_TYPE.lower()]

# for lease, sometimes ratio will be constantly 1
if (df_sub['RATIO_Close Price Per Sqft']==1.).all():
    df_sub['RATIO_Close Price Per Sqft_old'] = df_sub['RATIO_Close Price Per Sqft']
    df_sub['RATIO_Close Price Per Sqft'] = df_sub['Close Price']/df_sub['Est Fin Abv Grd SqFt']


"""
Generate close price graph
"""

print("=============================")
print(" Generating graphs...")
print("=============================")
# Graph with only per SqFt close price
temp = df_sub
x_var = 'Close Year'
y_var = 'RATIO_Close Price Per Sqft'
hue_var = 'Close Price'
df_plot = temp[[x_var, y_var, hue_var]].dropna().groupby(['Close Year']).median().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_plot[x_var],
                         y=df_plot[y_var],
                         mode='lines+markers',
                         name='Price per SqFt',
                         marker=dict(size=10),
                         line=dict(color='blue', width=3)))

fig.update_layout(
    title_text='Median Close Price/SqFt of ' + SUB_NAME,
    xaxis_title="Close Year",
    yaxis_title="$/SqFt")

save_to_file_name = os.path.join(TARGET_PATH,
                                 SUB_NAME+'_med_perSqFt_price.html')
# Avoid clash of file
while os.path.isfile(save_to_file_name):
    save_to_file_name = os.path.join(TARGET_PATH, SUB_NAME+'_med_perSqFt_price'+ ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))+'.html' )

fig.write_html(save_to_file_name)
print("Med per SqFt price chart saved in {}".format(TARGET_PATH))

# Graph with per SqFt close price, close price, and num sold.

fig = make_subplots(specs=[[{"secondary_y": True}]])
temp = df_sub
x_var = 'Close Year'
y_var = 'RATIO_Close Price Per Sqft'
hue_var = 'Close Price'
df_plot = temp[[x_var, y_var, hue_var]].dropna().groupby(['Close Year']).median().reset_index()


fig.add_trace(go.Scatter(x=df_plot[x_var],
                         y=df_plot[y_var],
                         mode='lines+markers',
                         name='Price per SqFt',
                         marker=dict(size=10),
                         line=dict(width=3)),
              secondary_y=False)

fig.add_trace(go.Scatter(x=df_plot[x_var],
                         y=df_plot[hue_var],
                         mode='lines+markers',
                         name='Close Price',
                         marker=dict(size=10),
                         line=dict(width=3)),
              secondary_y=True)

fig.add_trace(go.Bar(x=df_plot[x_var],
                     y=temp[[x_var, y_var, hue_var]].dropna().groupby(['Close Year']).size().values,
                     opacity=0.6, name='Num sold'),
              secondary_y=False)


fig.update_yaxes(title_text="Price per SqFt in $", secondary_y=False)
fig.update_yaxes(title_text="Close Price in $", secondary_y=True)
fig.update_layout(title='Median Price/SqFt and Close Price for ' + SUB_NAME,
                  xaxis_title='Close Year')

save_to_file_name = os.path.join(TARGET_PATH, SUB_NAME+'_med_all_price.html')

# Avoid clash of file
while os.path.isfile(save_to_file_name):
    save_to_file_name = os.path.join(TARGET_PATH, SUB_NAME+'_med_all_price'+ ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))+'.html' )

fig.write_html(save_to_file_name)
print("Med price chart saved in {}".format(TARGET_PATH))

print("=============================")
print(" Graphs ready!")
print("=============================")
