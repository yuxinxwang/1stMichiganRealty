from bs4 import BeautifulSoup
import re
import os
import pandas as pd
from datetime import date


def gen_path(subdir_name):
    path = os.path.join(os.getcwd(), subdir_name)
    return path

def find_useful(subdir_name, file_name, errors=[]):
    # Initiate dataframe
    df = pd.DataFrame(columns=["Address", "PIN", "Name"])

    try:
        # load html
        with open(os.path.join(subdir_name, file_name), 'r', encoding='utf-8') as f:
            source_code = f.read()

        # create BeautifulSoup object
        soup = BeautifulSoup(source_code, features='lxml')

        # Create matching pattersn
        pin_pattern = re.compile(r"(\s){0,1}[\d\-].+?(?=\s\(Parcel\sNumber\))")
        name_pattern = re.compile(r"^[A-Z(&amp;),\s']+$")
        address_pattern = re.compile(r"\d+\s([A-Za-z0-9]+\s{0,1})+")

        for bulk in soup.find_all('tr', {'class':"site-search-row"}):
            # print('\nNew Record:')
            new_record = {}
            for x in bulk.find_all('td'):
                pin_matching_status = pin_pattern.search(x.text)
                name_matching_status = name_pattern.search(x.text)
                address_matching_status = address_pattern.search(x.text)
                if bool(pin_matching_status):
                    new_record['PIN']=pin_matching_status.group()

                if bool(name_matching_status):
                    new_record['Name'] = name_matching_status.group()

                if bool(address_matching_status):
                    new_record['Address']= address_matching_status.group()

            df = df.append(new_record, ignore_index=True)


    except Exception as e:
        print('Error with {}'.format(file_name))
        print(e)
        errors.append(file_name)

    return df


if __name__=='__main__':
    SUBDIR = 'test_html'
    path = gen_path(SUBDIR)
    errors = []

    ### Initialize Dataframe
    df = pd.DataFrame(columns=["Address", "PIN", "Name"])
    ### PARSE HTML
    for file in os.listdir(path):
        filename = os.fsdecode(file)
        if filename.endswith('.html'):
            print(filename)
            new_df = find_useful(SUBDIR, filename, errors)
            df = df.append(new_df, ignore_index=True)
    if errors:
        print(errors)

    ### Clean up df
    df = df.dropna(subset=['Address', 'PIN'])

    ### Save parsed result
    RESULT_PATH = "demo_parsed_address_PIN"
    # Check that the directory exists
    if not os.path.exists(os.path.join(os.getcwd(), RESULT_PATH)):
        # Create dir if does not exist
        os.makedirs(os.path.join(os.getcwd(), RESULT_PATH), exist_ok=False)
    # Confirm result path exists
    RESULT_PATH = os.path.join(os.getcwd(), RESULT_PATH)
    TODAY = str(date.today()).replace('-','')
    df.to_csv(os.path.join(RESULT_PATH, 'addressPIN_'+TODAY+'.csv'), index=False)
