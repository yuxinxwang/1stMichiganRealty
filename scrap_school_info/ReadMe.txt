Instructions:

1. Make sure that your working directory contains "scrap.py" and "sample_addresses_novi.pickle".

2. Run "scrap.py" using python3. If the program exists with a "module not found" error, download the appropriate modules.

3. For now, "scrap.py" is only a demo version that downloads 3 html pages only, and it should take less than 1 minute to run. Once it's done, open the "saved_html" directory and make sure that the downloaded html files look similar to the ones in "saved_html_sample" directory.

4. If the downloaded files in Step 3 do not look right, contact Yuxin.

5. If the downloaded files in Step 3 look correct (specifically, it contains "School District & School Zones") information, proceed to the next step.

6. In line 77 in "scrap.py", change "NEEDED_ADDRESSES[:3]" to "NEEDED_ADDRESSES". This will download all data, which takes about 60 minutes.

7. When scrap.py stopped running, make sure that "saved_html" contains 275 files (you don't need to count -- just make sure it contains a lot of html files.)

8. Run "parse_html.py" using Python3. It should take less than 1 minute.

9. A directory called "school_info" should appear. Make sure that it contains a file called "school_info.csv", and check that it contains school information.

10. Send "school_info.csv" to yuxin.wang@1stmichiganrealty.com. 
