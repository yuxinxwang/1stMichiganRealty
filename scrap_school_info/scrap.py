import os
import pickle
from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def load_file(file_name='sample_addresses_novi.pickle'):
    with open(file_name, 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data


def download(list_of_address, target_path):
    problems = []
    driver = webdriver.Chrome(ChromeDriverManager().install())
    i = 0
    for address in list_of_address:
        try:
            address = str(address)
            print(i, 'Starting with, ', address)
            i += 1

            # Go to website
            driver.get('https://michigan.hometownlocator.com/schools/')
            sleep(2.58)

            # Find search box
            search_box = driver.find_element_by_xpath('//*[@id="gcForm"]/fieldset/p/input[1]')

            # Enter addrerss into search box
            search_box.send_keys(address)

            # Wait for all advertisement to load
            sleep(7.37)

            # automate submit info
            search_box.submit()

            # Wait for result to be loaded
            sleep(3.12)

            # Download page source
            html_source = driver.page_source

            # Save page source to target_path
            target_file_name = os.path.join(target_path, address+'.html')

            with open(target_file_name, "w", encoding="utf-8") as file:
                file.write(html_source)
            print('Done with', address)

        except Exception as e:
            print(e)
            problems.append(address)
            print('!!! Have problem with, ', address)


    driver.quit()
    return problems


if __name__ == '__main__':
    # Load needed addresses
    NEEDED_ADDRESSES = load_file("sample_addresses_madison_heights.pickle")
    print("There are {} addresses in total; should take about {} minutes to complete!".format(len(NEEDED_ADDRESSES), len(NEEDED_ADDRESSES)*13.07/60))

    # save downloaded data in this (sub)directory
    TARGET_PATH = 'saved_html'

    # Check that the directory exists
    if not os.path.exists(os.path.join(os.getcwd(), TARGET_PATH)):
        # Create dir if does not exist
        os.makedirs(os.path.join(os.getcwd(), TARGET_PATH), exist_ok=False)

    # Download data
    problematic_addresses = download(NEEDED_ADDRESSES[:3], 'saved_html')

    # print addresses that were not successfully downloaded
    if len(problematic_addresses) > 0:
        print('===============================')
        print('Problems:')
        print(problematic_addresses)
        with open(os.path.join(os.getcwd(), TARGET_PATH, 'problems.pickle'), 'wb') as b:
            pickle.dump(problematic_addresses, b)
