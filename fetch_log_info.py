from astropy.time import Time
from datetime import datetime
import numpy as np
import os
import re

all_logs = '/home/rsharan/Desktop/PhD_project/MSP Spectra/GTAC_logs/All_log_info_main.txt'

with open(all_logs, 'r') as email_file:
	all_log_content = email_file.read()


obs_log_section = all_log_content.split('################################################################################################')

#Select_mode_only = ['PA']
Select_mode_only = ['PA', 'IA']
band_func = lambda nu : 5 if 1000<=nu<=1460 else (4 if 550<=nu<=1000 else (3 if 250<=nu<=500 else (2 if 125<=nu<=250 else 'No Band info')))



def get_log_info(given_mjd, freq_=None, Select_mode_only=['PA', 'IA']):
	pattern_mjd_start_stop = r'MJD_start\s*=\s*(\d*[.]*\d*);\s*MJD_stop\s*=\s*(\d*[.]*\d*).*'
	pattern_info = r'beam_dict\s*=\s*(.*)'
	for section_iter in obs_log_section:
		if not re.search(pattern_mjd_start_stop, section_iter):
			continue
		
		mjd_start, mjd_stop = list(map(float, re.search(pattern_mjd_start_stop, section_iter).groups()))
		if not bool(mjd_start < given_mjd < mjd_stop):
			continue

		if re.search(pattern_info, section_iter):
			beam_dict = eval(re.findall(pattern_info, section_iter)[0])
		else:
			continue

		if not any(Select_mode_only):
			return eval(re.findall(pattern_info, section_iter)[0])

		for mode_only in Select_mode_only:
			for beam_mode_val in beam_dict.values():
				if band_func(float(freq_)) != band_func(float(beam_mode_val['Freq'])):
					continue
				if beam_mode_val['Mode'].lower() == mode_only.lower():
					try:
						return beam_mode_val
					except:
						pass
					
