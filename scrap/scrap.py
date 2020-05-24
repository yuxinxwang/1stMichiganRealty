from selenium import webdriver
from time import sleep
import sys, os, inspect
import pickle
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select




def load_file(file_name='sample_addresses.pickle'):
    with open(file_name,'rb') as f:
        needed_addresses = pickle.load(f)
    return needed_addresses


def download(list_of_address):
    problems = []
    driver = webdriver.Chrome(ChromeDriverManager().install())

    for address in list_of_address:
        try:
            address = str(address)
            print('Starting with, ', address)

            driver.get('https://michigan.hometownlocator.com/schools/')
            sleep(2.17)
            # user_decision = input("Ready to proceed to searchbox? Y/N ")
            # if user_decision.strip()=='Y':
            search_box = driver.find_element_by_xpath('//*[@id="gcForm"]/fieldset/p/input[1]')
            # search_box.click()
            # search_box.clear()
            search_box.send_keys(address)
            user_decision = input('Input correct? Y/N ')
            if user_decision == 'y':
                search_box.submit()
                # search_box.send_keys(Keys.ENTER)


            ### Let user decide when to proceed
            sleep(2.89)
            user_decision = input("Ready to download? Y/N ")
            if user_decision.strip() == 'y':
                html_source = driver.page_source
                target_file_name = \
                    'html/'+address+'.html'

                with open(target_file_name, "w") as file:
                    file.write(html_source)
                print('Done with', address)
            elif user_decision.strip()=='q':
                driver.quit()
                problems.append(address)
                return problems
            else:
                problems.append(address)


        except Exception as e:
            print(e)
            problems.append(address)
        # else:
    driver.quit()
    return problems


if __name__ == '__main__':
    needed_addresses = load_file()
    problems = download(needed_addresses[:50])

    if len(problems)>0:
        print(problems)
        with open('html/problem.pickle', 'wb') as b:
            pickle.dump(problems,b)
