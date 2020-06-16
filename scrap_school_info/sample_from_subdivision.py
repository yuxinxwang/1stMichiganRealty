# -*- coding: utf-8 -*-
"""
Sample from Subdivision
Author: Yuxin WANG
Last Modified: 6/15/2020
"""

import pandas as pd
import pickle
import os
import re
import random
from collections import defaultdict

"""
Need to change these to the directories on your computer
"""
# SAVING_DIR: directory to save computed results
SAVING_DIR = None
# DATA_DIR: directory where data are stored
DATA_DIR = None
# CITY_NAME: name of city that you are working on
CITY_NAME = None

"""
Load public record method
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

# Read data
df = load_public_record(DATA_DIR, CITY_NAME)

"""
Find stem (i.e. main part) of each subdivision
"""

# Initialize related variables
subdivision_to_stem = dict()
stem_to_subdivision = defaultdict(set)

# Get stem of subdivisions
# For instance, stem of "Jamestown No 2" and "Jamestown No 3" would both  be
#   "Jamestown".
for name in df['Subdivision Name'].dropna().unique():
    # find main part
    stem = re.split(r"\sNO\s|\sOCCPN\s", name)[0]
    # record stem corresponding to name
    subdivision_to_stem[name] = stem
    # record name corresponding to stem
    stem_to_subdivision[stem].add(name)

# Create a column for stem
df['Subdivision Stem'] = df['Subdivision Name'].replace(subdivision_to_stem)

# Drop nan values
df = df.dropna(subset=['Subdivision Stem'])

# Sample from each stem
stem_to_address = df[['Subdivision Stem', 'Address']]\
                  .groupby('Subdivision Stem')\
                  .agg(lambda x: random.sample(set(x),1)[0])\
                  .to_dict()['Address']

# Check that is stem is sampled
assert len(stem_to_subdivision) == len(stem_to_address)

# Get list of sample addresses
sample_address = list(map(lambda x: x.strip()+", "+CITY_NAME+" MI",
                          list(stem_to_address.values())))

# Save data
with open(os.path.join(SAVING_DIR, 'subdivision_to_stem.pickle'), 'wb') as h:
    pickle.dump(subdivision_to_stem, h, protocol=pickle.HIGHEST_PROTOCOL)

with open(os.path.join(SAVING_DIR, 'stem_to_address.pickle'), 'wb') as h:
    pickle.dump(stem_to_address, h, protocol=pickle.HIGHEST_PROTOCOL)

with open(os.path.join(SAVING_DIR, 'stem_to_subdivision.pickle'), 'wb') as h:
    pickle.dump(stem_to_subdivision, h, protocol=pickle.HIGHEST_PROTOCOL)

with open(os.path.join(SAVING_DIR, 'sample_addresses.pickle'), 'wb') as h:
    pickle.dump(sample_address, h, protocol=pickle.HIGHEST_PROTOCOL)
