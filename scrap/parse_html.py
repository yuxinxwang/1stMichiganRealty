from bs4 import BeautifulSoup
import re
import os
import pandas as pd
import pickle


def gen_path():
    pwd = os.getcwd()
    path = pwd+"/html_safari/"
    return path

def find_useful(file_name, errors=[]):
    # Initiate dataframe
    df = pd.DataFrame(columns=["Address", "PIN", "Name"])

    try:
        # load html
        with open("html_safari/"+file_name, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # create BeautifulSoup object
        soup = BeautifulSoup(source_code, features='lxml')

        # Create matching pattersn
        pin_pattern = re.compile(r"(\s){0,1}[\d\-].+?(?=\s\(Parcel\sNumber\))")
        name_pattern = re.compile(r"^[A-Z(&amp;),\s']+$")
        address_pattern = re.compile(r"\d+\s([A-Za-z0-9]+\s{0,1})+")



        # Create lists to store results
        pin_list = []
        name_list = []
        address_list = []

        for bulk in soup.find_all('tr', {'class':"site-search-row"}):
            # print('\nNew Record:')
            new_record = {}
            for x in bulk.find_all('td'):
                pin_matching_status = pin_pattern.search(x.text)
                name_matching_status = name_pattern.search(x.text)
                address_matching_status = address_pattern.search(x.text)
                if bool(pin_matching_status):
                    new_record['PIN']=pin_matching_status.group()
                    # print(pin_matching_status.group())
                if bool(name_matching_status):
                    new_record['Name'] = name_matching_status.group()
                    # print(name_matching_status.group())
                if bool(address_matching_status):
                    new_record['Address']= address_matching_status.group()
                    # print(address_matching_status.group())
            # print(new_record)
            # if len(temp)>1:
            #     # new_record['PIN'] = temp[0]
            #     print(temp)
            df = df.append(new_record, ignore_index=True)


        df['Address'] = address_list
        df['PIN'] = pin_list
        df['Owner'] = name_list

    except:
        errors.append(file_name)

    return df



if __name__=='__main__':
    path = gen_path()
    errors = []

    ### Initialize Dataframe
    df = pd.DataFrame(columns=["Address", "PIN", "Name"])
    ### PARSE HTML
    for file in os.listdir(path):
        filename = os.fsdecode(file)
        # if filename.startswith('Bayview Drive0'):
        new_df = find_useful(filename, errors)
        try:
            df = pd.concat([df, new_df], axis=0)
        except:
            errors.append(filename)

    ### Save parsed result
    try:
        df.to_csv('output/df20200516.csv')
    except:
        with open('output/df20200516.pickle', 'wb') as b:
            pickle.dump(df,b)






####################### OLD
    #         add_len = len(new_df)
    #         if add_len != 0:
    #             count += 1
    # print(count)
            # new_len = len(df)
            # assert(old_len+add_len==new_len), "Old length is {}, newly added {} entries, new length should be {} but is {}. This occured with file {}.".format(old_len, add_len, old_len+add_len, new_len, filename)
            # print('Done with ', filename)
            # old_len = new_len
    # print("Final answer:\n", df)

    # try:
    #     df.to_csv('output/test.csv')
    # except:
    #     with open('output/test.pickle', 'wb') as b:
    #         pickle.dump(df,b)
    # # store errors
    # if len(errors)>0:
    #     print(errors)
    #     with open('issues/errors.pickle', 'wb') as b:
    #         pickle.dump(errors,b)
