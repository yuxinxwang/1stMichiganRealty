This is a short demo of how the scrapping works. 

* Navigate to the folder that contains ```scrap.py```

* Type ```pip install -r requirements.txt``` to install the required packages 

* Type ```python3  scrap.py <city_name>``` to scrap data for ```city_name```. 
For instance ```python3  scrap.py Novi,MI```. Notice that there is no space between ```Novi,``` and ```MI```. 

* If the console prints out a line saying ```Need to parse data from json...
The json file is located at <location>```, then type ```python3 parse_json.py <location>``` to parse this file. 

* The console will say ```Data saved to <csv_location>```. 
Now type 	```python3 get_daysOnZillow_saves.py <csv_location>``` to scrap saves and views data. 