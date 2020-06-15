from bs4 import BeautifulSoup
import os
import pandas as pd
import pickle


def gen_path():
    path = os.path.join(os.getcwd(), 'saved_html')
    return path

def find_useful(path, file_name, errors=[]):
    # Initiate dataframe
    df = pd.DataFrame(columns=["Address", "District", "Elementary", "Middle", "High"])

    try:
        # load html
        with open(os.path.join(path, file_name), 'r', encoding='utf-8') as f:
            source_code = f.read()

        # create BeautifulSoup object
        soup = BeautifulSoup(source_code, features='lxml')

        # Create dict to store results
        new_record = dict()
        # Read address from filename
        new_record['Address'] = file_name.split(', Novi')[0].strip()
        # Look for relevant information
        for result in soup.find_all('a'):
            if "Elementary School" in result.text:
                new_record['Elementary'] = result.text
            elif "Middle School" in result.text:
                new_record['Middle'] = result.text
            elif "High School" in result.text:
                new_record['High'] = result.text
            elif "School District" in result.text:
                new_record['District'] = result.text
        # Change result to dataframe
        df = df.append(new_record, ignore_index=True)


    except:
        errors.append(file_name)

    return df


if __name__=='__main__':
    HTML_PATH = gen_path()
    not_parsed = []
    VERBOSE = True

    ### Initialize Dataframe
    df = pd.DataFrame(columns=["Address", "District", "Elementary", "Middle", "High"])

    ### PARSE HTML
    i = 0
    for file in os.listdir(HTML_PATH):
        filename = os.fsdecode(file)
        new_df = find_useful(HTML_PATH, filename, not_parsed)
        try:
            df = df.append(new_df, ignore_index=True, sort=False)
        except:
            not_parsed.append(filename)
        i += 1
        if (i%20==1) and VERBOSE:
            print('Complete {} items'.format(i))

    ### Save parsed result
    RESULT_PATH = "school_info"
    # Check that the directory exists
    if not os.path.exists(os.path.join(os.getcwd(), RESULT_PATH)):
        # Create dir if does not exist
        os.makedirs(os.path.join(os.getcwd(), RESULT_PATH), exist_ok=False)
    # Confirm result path exists
    RESULT_PATH = os.path.join(os.getcwd(), RESULT_PATH)
    try:
        assert (os.path.exists(RESULT_PATH)), \
                "Path {} does not exist!!!\nSaving to pwd...".format(RESULT_PATH)
    except:
        RESULT_PATH = os.getcwd()

    ### Save df to result
    try:
        df.to_csv(os.path.join(RESULT_PATH, "school_info.csv"), index=False)
    except:
        with open(os.path.join(RESULT_PATH, "school_info.pickle"), 'wb') as b:
            pickle.dump(df, b)
