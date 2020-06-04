# -*- coding: utf-8 -*-

### Import libraries
from fuzzywuzzy import fuzz
import numpy as np
import os
import pandas as pd
import pickle
import re
import sys

# !pip install -q fuzzywuzzy
# !pip install -q fuzzywuzzy[speedup]


def load_mile_road_dict():
    mile_road_dict =   {'1': 'One',
                        '2': 'Two',
                        '3': 'Three',
                        '4': 'Four',
                        '5': 'Five',
                        '6': 'Six',
                        '7': 'Seven',
                        '8': 'Eight',
                        '9': 'Nine',
                        '10': 'Ten',
                        '11': 'Eleven',
                        '12': 'Twelve',
                        '13': 'Thirteen',
                        '14': 'Fourteen',
                        '15': 'Fifteen',
                        '16': 'Sixteen',
                        '17': 'Seventeen',
                        '18': 'Eighteen',
                        '19': 'Nineteen',
                        '20': 'Twenty'}
    return mile_road_dict


def save_resource(data, file_name,
                        file_path="resources"):
    """ Save resource to directory
    Args:
        data: the data to be stored.
        file_name (str): save data to file_name.
        file_path (str): directory to save data. Default is ```resources```
    Returns:
        None
    """
    # Check path exists
    current_dir, _ = os.path.split(__file__)
    data_path = os.path.join(current_dir+"/../", file_path)
    assert (os.path.exists(data_path)), \
        "Directory {} does not exist! ".format(data_path)

    ### Save data
    with open(os.path.join(data_path,file_name), 'wb') as handle:
        pickle.dump(data, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)


def load_resource(file_name, rel_path="resources"):
    """ Load resource
    Args:
        file_name (str): full file name. This should be included in
                         ```resources``` directory.
        rel_path (str): path to ```file_name```.  Default value
                        is ```resources```.

    Returns:
        data: the data consistant with pickle file data.
    """
    # Get directory
    current_dir, _ = os.path.split(__file__)
    data_path = os.path.join(current_dir+"/../", rel_path, file_name)

    # Read resource file
    assert (os.path.exists(data_path)), \
        "Resource {} does not exist! ".format(data_path)

    with open(data_path, 'rb') as handle:
        data = pickle.load(handle)

    return data

def compile_re(pattern):
    """ Compile a regular expression with pattern
    Args:
        pattern (str): a string representing the pattern
        e.g. "NoviPRD-.*" means strings that start with "NoviPRD-"
        e.g. ".*\.csv" means strings that end with ".csv"
        e.g. ".*xxx.*" means strings that contain "xxx" in the middle

    Returns:
        regular expression object
    """
    return re.compile(pattern)


def find_within(path, pattern, name_only=True):
    """ Find fileds in path with pattern
    Args:
        path (str): path to data
        pattern (str): a string representing the pattern
            e.g. "NoviPRD-.*" means strings that start with "NoviPRD-"
            e.g. ".*\.csv" means strings that end with ".csv"
            e.g. ".*xxx.*" means strings that contain "xxx" in the middle
    Returns:
        an iterable of files in path whose name matches with pattern
    """

    assert(os.path.exists(path)), "Path {} does not exist!".format(path)
    regex = compile_re(pattern)

    for file in os.listdir(path):
        file_name = os.fsdecode(file)
        if regex.search(file_name):
            if name_only:
                yield file_name
            else:
                yield file


def load_df(file_name, path="resources", **kwargs):
    """ Load resource
    Args:
        file_name (str): full file name. This should be included in
                         ```resources``` directory.
        path (str): path to ```file_name```.  Default value
                        is ```resources```.
        **kwargs: kwargs to be passeed into pd.read_csv
    Returns:
        data: the data from the csv file
    """
    # Get directory
    if os.path.exists(path):
        # this is an absolute path
        data_path = os.path.join(path, file_name)
    else:
        # this is a relative path
        current_dir, _ = os.path.split(__file__)
        data_path = os.path.join(current_dir+"/../", path, file_name)

    # Read resource file
    assert (os.path.exists(data_path)), \
        "Resource {} does not exist! ".format(data_path)
    if file_name.endswith('.csv'):
        df = pd.read_csv(data_path, **kwargs)
    else:
        df = pd.read_excel(data_path, **kwargs)

    return df


def load_sample(file_name="addresses.csv",
                rel_path="resources/datasets"):
    """ Load resource
    Args:
        file_name (str): full file name. This should be included in
                         ```resources``` directory.
        rel_path (str): path to ```file_name```.  Default value
                        is ```resources```.

    Returns:
        data: the data consistant with pickle file data.
    """
    # Get directory
    current_dir, _ = os.path.split(__file__)
    data_path = os.path.join(current_dir+"/../", rel_path, file_name)

    # Read resource file
    assert (os.path.exists(data_path)), \
        "Resource {} does not exist! ".format(data_path)


    sample = pd.read_csv(data_path)
    return sample
