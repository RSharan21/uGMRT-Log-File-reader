This is a collection of python scripts that helps the user to get the uGMRT log information from the locally stored email files.
The python script `all_zip_filesextract_no_of_ant_beam_mode.py` collects all the log file information (number of antenna used, frequency and mode of observation) and stores in a text file named `Final_outputs.txt`.
Then `fetch_log_info.py` prints the fetched information depending on the mjd (any mjd during the observation), frequency and the selected mode (optional) of the observation
