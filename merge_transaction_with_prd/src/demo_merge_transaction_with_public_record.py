# -*- coding: utf-8 -*-
"""
DEMO_merge_transaction_with_public_record
Author: Yuxin WANG
Last Modified: 6/15/2020
"""

### Import libraries
import numpy as np
import pandas as pd
import re
import os
import sys

# Before importing fuzzywuzzy, you need to install the library
# !pip install -q fuzzywuzzy
# !pip install -q fuzzywuzzy[speedup]
from fuzzywuzzy import fuzz

# Before importing address_parser, download address_parser from
#   https://github.com/yuxinxwang/address_parser
# Address_parser contains methods to help clean up messy addresses
PARSER_PATH = None # Download address_parser and link its path here
sys.path.append(PARSER_PATH)
import address_parser.address_methods as amod
from address_parser_class import AddressParser
ap = AddressParser()

"""
Define paths
"""
TRANSACTION_PATH = None # path that contains transaction dataset
PRD_PATH = None # path to directory that contains public record
RESULT_PATH = None # path to directory that saves output
CITY_NAME = None # city name. Note that public records should start with CITY_NAME exactly

"""
Define functions
"""
def gen_raw_index(df):
    return df.reset_index().rename(columns={'index':'index_raw'})

def gen_PIN_len(df):
    df['PIN_len'] = df['PIN'].apply(lambda x: len(str(x)))
    return df

def clean_PIN_by_row(row):
    try:
        if (row['PIN_len'] == 12) and (str(row['PIN'])[:2] in ('50', '88', '80')):
            return str(row['PIN'])[2:]
    except:
        pass
    return str(row['PIN'])

def split_mult_PIN(x):
    x = x.replace('-', '')
    if any([c.isnumeric() for c in x]):
        temp = re.split(r"[^\d]", x)
        ans = []
        for i,p in enumerate(temp):
            if len(p)>0:
                ans.append(temp[0][:-len(p)] + p)
        return ans
    else:
        return [x]

def gen_mult_PIN_list(df):
    df['PIN'] = df.apply(clean_PIN_by_row, axis=1)
    df['temp'] = df['PIN'].astype('str').apply(split_mult_PIN)
    return df

def split_PIN_list(df):
    return pd.DataFrame({col: np.repeat( df[col].values, df['temp'].str.len()) \
            for col in df.columns.drop('temp') })\
            .assign(**{'temp':np.concatenate(df['temp'].values)})[df.columns]

def gen_index(df):
    return df.reset_index().rename(columns={'index':'index_clean'})

def clean_temp_col(df):
    df['PIN'] = df['temp']
    return df.drop(columns=['PIN_len','temp']).drop_duplicates(subset=['Address_x', 'PIN'])

def cut_PIN(x):
    if len(x)>10 and x[:2] == '88':
        return x[2:]
    return x

"""
Load transaction dataset
"""

# if SIMPLE_VERSION, only basic info is loaded, but operations are faster
SIMPLE_VERSION = True
if SIMPLE_VERSION:
    df_transaction = pd.read_csv(TRANSACTION_PATH)\
                          .rename(columns={'Parcel Number':'PIN'})
else:
    df_transaction = pd.read_csv(TRANSACTION_PATH,
                                 usecols=['Address_x', 'Subdivision Name',
                                          'Parcel Number', 'City',
                                          'School District'])\
                       .rename(columns={'Parcel Number':'PIN'})

# Clean up duplicated PINs etc
df_test = gen_raw_index(df_transaction)
df_test = gen_PIN_len(df_test)
df_test = gen_mult_PIN_list(df_test)
df_test = split_PIN_list(df_test)
df_test = clean_temp_col(df_test)
df_test = amod.gen_index(df_test)
df_test['PIN'] = df_test['PIN'].apply(cut_PIN)



"""
Merge with public record
"""
# Define function that reads public record
def load_public_record(path, starting_pattern, full_record=False):
    """ Loads public record from multiple datasets
    Paramters:
        path: (str) path to directory that contains the data
        starting_pattern: (str) the files that contain public record data
                          should all start with starting_pattern
        full_record: (bool) if True, load full public record; if false, only
                     read PIN, Address, Subdivision Name.
    Returns:
        public_record: (DataFrame) a pandas dataframe that contains all public
                        record information for this city, with no duplicates.
    """
    dir_prd = os.fsencode(path)
    public_record = pd.DataFrame()
    for f in os.listdir(dir_prd):
        if (not starting_pattern) or (os.fsdecode(f).startswith(starting_pattern)):
            # print(os.fsdecode(f))
            if full_record:
                new_record = pd.read_csv(path+os.fsdecode(f)).rename(\
                                         columns={'Property ID':'PIN',
                                                  'Property Address':'Address'})
            else:
                new_record = pd.read_csv(path+os.fsdecode(f),
                                         usecols=[0, 1, 15],
                                         skiprows=1,
                                         names=['PIN', 'Address',
                                                'Subdivision Name'])
            public_record = public_record.append(new_record, ignore_index=True)

    return public_record.drop_duplicates()

def merge_public_record(df, public_record):
    return df.astype({'PIN':str}).merge(public_record.astype({'PIN':str}),
                                        on='PIN', how='inner')

def gen_not_matched(df_merged, df_all):
    return df_all.loc[~(df_all['index_clean'].isin(
        df_merged['index_clean']))]

# Load public records
public_record = load_public_record(PRD_PATH, CITY_NAME, False)

# Merge transaction with public record
df_merged = merge_public_record(df_test, public_record)

# Separate not matched records
df_not_matched = gen_not_matched(df_merged, df_test)

print(len(df_merged), len(df_not_matched), len(df_test))

"""
Try to match based on address
"""

# Prepare datasets to analyze in details
# i.e., split 'Address' in parts like "street name", "street suffix" etc
split_address = amod.parse_street_series(df_not_matched['Address_x'],
                                         df_not_matched)

prd_split = amod.parse_street_series(public_record['Address'],
                                     public_record[['PIN', 'Address']])

# Summarize information
name_to_suffix_dict = amod.get_combinations_as_dict(prd_split, ['Street Name', 'Street Suffix'])
std_name_set = set(prd_split['Street Name'].unique())
std_address_set = set( zip(prd_split['Street Name'], prd_split['Street Suffix']) )

def close_match_row(row):
    name_sug, suffix_sug, score = ap.close_match(row['Street Name'],
                                              row['Street Suffix'], std_address_set, std_name_set,
                          name_to_suffix_dict)
    return (name_sug, suffix_sug, score, row['index'])

def agg_func(x):
    if len(x)==1:
        return list(x)[0]
    return x

# Create empty dataset to store matches based on address
temp = pd.DataFrame(columns=['Name_sug', 'Suffix_sug', 'Score', 'index'])

# Get suggested name and suffix
temp['Name_sug'], temp['Suffix_sug'], temp['Score'], temp['index'] = \
    zip(*split_address.reset_index().apply(close_match_row, axis=1))

# Incorporate information from split_address
temp = split_address.reset_index().merge(temp, on='index', how='inner')

# If match score >= 90, replace old 'Street Name' and 'Street Suffix' with
#     suggested ones.
temp.loc[temp.Score>=90, ['Street Name', 'Street Suffix']] = np.nan, np.nan
temp['Street Name'] = temp['Street Name'].fillna(temp['Name_sug'])
temp['Street Suffix'] = temp['Street Suffix'].fillna(temp['Suffix_sug'])

# Merge with public record to get standard PIN
temp = temp.merge(prd_split, on=['Street Number', 'Street Name', 'Street Suffix'], how='inner')

# There might be multiple matching address (different units in the same address)
# We group by index to make the match one-to-many (i.e. multiple matches with
#   the same address should appear in the same row)
# g = temp[['index', 'Address_x', 'PIN_x', 'Address', 'PIN_y', 'index_clean',
#           'index_raw', 'City', 'School District']].groupby('index')
g = temp.groupby('index')
temp = pd.concat([g.agg(lambda x: set(x)).applymap(agg_func), g.size()],
                 axis=1).rename(columns={0:'num_match'})

# Get the ones with unique match. These can be appended to df_merged
temp1 = temp.rename(columns={'PIN_x':'PIN_from_transaction', 'PIN_y':'PIN'})\
    .loc[temp.num_match==1].drop(columns=['num_match'])
temp1['Subdivision Name'] = np.nan
df_merged1 = merge_public_record(temp1[(df_test.columns)], public_record)
df_merged = df_merged.append(df_merged1, ignore_index=True, sort=False)

# Re-calculate the records that are not maatched
df_not_matched = gen_not_matched(df_merged, df_test)

# Check that the original file has indeed been split into 2 disjoint sets
print(len(df_not_matched), len(df_merged), len(df_test))

# Save the results to your dir
gen_not_matched(df_merged, temp).to_csv(os.path.join(RESULT_PATH,
                                                     'matched_on_address.csv'))
df_merged.to_csv(os.path.join(RESULT_PATH, 'merged.csv'))
df_not_matched.to_csv(os.path.join(saving_dir, 'not_matched.csv'))
