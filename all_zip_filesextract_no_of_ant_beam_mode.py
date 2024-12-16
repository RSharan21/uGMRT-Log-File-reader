
import time

start = time.time()
from astropy.time import Time
from datetime import datetime
import numpy as np
import email
import os
import re
# set the path to the folder containing the .eml files and output file location
base_path = '/home/rsharan/Desktop/PhD_project/MSP Spectra/GTAC_logs/Zip_files'
output_file_path = '/home/rsharan/Desktop/PhD_project/MSP Spectra/GTAC_logs/Final_outputs.txt'
####################################################################################################################

# Keywords to search in the log file

keyword_GWB_Setting = r'.+GWB.*\n*.*Setting'

keyword = "gtac observation log"
pattern_0 = r'Start and End Time of Obs.\(IST\):\s*(\d{2}\s*\w{3}\s*\d{4}\s*\d{2}:\s*\d{2}:\s*\d{2})\s*-\s*(\d{2}\s*\w{3}\s*\d{4}\s*\d{2}:\s*\d{2}:\s*\d{2})'
param_0 = r'.*Start and End Time of Obs.\(IST\).*\n*'
#param = r'.*(Start and End Time of Obs.\(IST\)\.*:.*\n*.*)'
pattern_1 = r'.*(GPU_RF(\d))\s*:\s*[+-]*(\d{3,4}).*'
pattern_2 = r'.*(GPU_RF(\d))\s*:\s*[+-]*(\d{,4}).*'
pattern_beam_mode = r'.*(GPU_BEAM_(\d))\s*:\s*(\w*)'
#pattern_ant_no = r'.*(BEAM-([1234]):\d{3}).*\s*::.*Total\s*=\s*(\d{1,2}).*'
pattern_ant_no = r'.*(BEAM-([1234]):\d{3}).*\s*::.*Total\s*=\s*(?:3D)*\s*(\d{1,2}).*'
pattern_ant_no_1 = r'.*(BEAM-([1234]):\d{3}).*\s*::'
#bw_pattern_gsb = r'.*ACQ BW.*\s*:\s*(\d*.\d{,3}).*'
#bw_pattern_gwb = r'.*ACQ BW.*\s*:\s*(\d*.\d{,3}).*'

band_func = lambda nu : 5 if 1000<=nu<=1460 else (4 if 550<=nu<=1000 else (3 if 250<=nu<=500 else (2 if 125<=nu<=250 else 'No Band info')))
items = os.listdir(base_path)


with open(output_file_path, 'w') as output_file:
	# loop through all files in the folder
	for item in items:
		if os.path.isdir(os.path.join(base_path, item)):
			folder_path = os.path.join(base_path, item)
			print('Folder path : ', folder_path)
			output_file.write('Folder path : ' + folder_path + '\n')
			for filename in os.listdir(folder_path):
				# check if the file is a .eml file
				if filename.endswith('.eml'):
					# read the contents of the email file
					with open(os.path.join(folder_path, filename), 'r') as email_file:
						email_content = email_file.read()
						print(os.path.join(folder_path, filename))
						output_file.write('File path : ' + os.path.join(folder_path, filename) + '\n')
						param_0_content = re.search(param_0, email_content)

						if keyword in email_content.lower() and param_0_content:
							# This section Searches for start and stop time from the GMRT log file
							param_line_0 = re.search(pattern_0, email_content)
							if not param_line_0:
								count_start_stop_param = 0
								email_content_line_no,  email_content_line = param_0_content.span()[-1], re.sub("\n*>*=*\s+"," ",param_0_content.group())
								while not re.search(pattern_0, email_content_line) and count_start_stop_param <10:
									add_line = re.search(r'.+\n', email_content[email_content_line_no:]).group()
									email_content_line += re.sub("\n*>*=*\s+"," ",add_line)
									email_content_line_no += re.search(r'.+\n',email_content[email_content_line_no:] ).span()[-1]
									count_start_stop_param += 1
								param_line_0 = email_content_line
								param_line_0 = re.sub("\n*>*=*\s+"," ",param_line_0)
								param_line_0 = re.search(pattern_0,param_line_0)
							start_time, end_time = param_line_0.groups()
							# mjd_start, mjd_stop (in UTC time, subtracted 5.5 hrs from the IST mjd)
							mjd_start, mjd_stop = Time(datetime.strptime(start_time, "%d %b %Y %H:%M:%S")).mjd - round(5.5/24, 3), Time(datetime.strptime(end_time, "%d %b %Y %H:%M:%S")).mjd - round(5.5/24, 3)
							print(param_line_0.group(), ':::::::::::::::', filename)
							output_file.write(param_line_0.group() + ':::::::::::::::' + filename + '\n')
							print( 'MJD_start = ', mjd_start, ';     MJD_stop = ', mjd_stop)
							output_file.write( 'MJD_start = ' +str(mjd_start) +';     MJD_stop = ' + str(mjd_stop) + '\n')
							# This section searches for the Band information from the GMRT log file
							if re.search(keyword_GWB_Setting, email_content):
								if re.search(pattern_1, email_content):
									band_info = re.findall(pattern_1, email_content)
									#band_no = list(map(band_func, map(float,np.asarray(band_info)[:,1] ) ) )
								elif re.search(pattern_2, email_content):
									band_info = re.findall(pattern_2, email_content)
									#band_no = list(map(band_func, map(float,np.asarray(band_info)[:,1] ) ) )
								else:
									print('NO frequency information in GWB Settings section')
									output_file.write('NO frequency information in GWB Settings section' + '\n')
									band_info =[]
								# This section searches for the Beam mode information from the GMRT log file
								beam_modes = re.findall(pattern_beam_mode, email_content)
								# This section searches for the Antenna in Beam information from the GMRT log file
								GWB_ant_lines = []
								start_section = False
								#print('GWB GAC configuration present')
								GWB_section_out = 0
								check_GWB_GAC_configuration = not 'GWB GAC configuration' in email_content
								for line_ind, line in enumerate(email_content.splitlines()):
									possible_line = re.search(pattern_ant_no, line)
									if 'GWB GAC configuration' in line:
										start_section = True
										continue
									elif check_GWB_GAC_configuration and re.search(pattern_ant_no_1, line) and GWB_section_out == 0:
										start_section = True
										pass
									if start_section == True:
										if 'GSB GAC configuration' in line:
											start_section = False
											break
										if 'BEAM' in line:
											GWB_section_out = 0
											while not(re.search(pattern_ant_no,''.join(email_content.splitlines()[line_ind : line_ind +1 + GWB_section_out]))) and GWB_section_out < 17:
												GWB_section_out += 1
											a = ' '.join(email_content.splitlines()[line_ind: line_ind +1 + GWB_section_out])
											a = re.sub("\n*>*\s+"," ",a)
											GWB_ant_lines.append(a)
										else:
											if GWB_section_out < 17:
												GWB_section_out += 1
												continue
											else:
												break
								Ant_no_beam = re.findall(pattern_ant_no, '\n'.join(GWB_ant_lines))
								'''
								#for band_info_i in band_info: print(band_info_i); output_file.write(band_info_i + '\n')
								print('\n'.join(f'{i}' for i in band_info))
								output_file.write('\n'.join(f'{i}' for i in band_info) + '\n')
								#for beam_modes_i in beam_modes: print(beam_modes_i); output_file.write(beam_modes_i + '\n')
								print('\n'.join(f'{i}' for i in beam_modes))
								output_file.write('\n'.join(f'{i}' for i in beam_modes) + '\n')
								#for Ant_no_beam_i in Ant_no_beam: print(Ant_no_beam_i); output_file.write(Ant_no_beam_i + '\n')
								print('\n'.join(f'{i}' for i in Ant_no_beam))
								output_file.write('\n'.join(f'{i}' for i in Ant_no_beam) + '\n')
								#for GWB_ant_lines_i in GWB_ant_lines: print(GWB_ant_lines_i); output_file.write(GWB_ant_lines_i + '\n')
								print('\n'.join(f'{i}' for i in GWB_ant_lines))
								output_file.write('\n'.join(f'{i}' for i in GWB_ant_lines) + '\n')
								'''
								print('--------------------------------------------------------------------------------------------')
								output_file.write('--------------------------------------------------------------------------------------------' + '\n')
								# # This section stiches BEAM MODE, number of ANTENNA used in the beam and Frequency of the BEAM information obtained from above section
								beam_dict = {}
								band_no_count = 0
								beam_mode_list = [int(tup[1]) for tup in beam_modes if tup[2] != 'OFF']
								if len(beam_mode_list) == 0:
									beam_mode_val = 'unknown'
									try:
										beam_mode_list = np.array(beam_modes)[:,1].astype(int)
									except:
										continue
									not_all_beam_off = False
								else:	
									not_all_beam_off = True
								for beam_modes_ind in beam_mode_list:
									beam_dict[beam_modes_ind] = {}
									if not_all_beam_off:
										beam_mode_val = np.array(beam_modes)[beam_modes_ind - 1, -1]
									###############################################################################
									beam_dict[beam_modes_ind]['Mode'] = beam_mode_val
									###############################################################################
									#Ant_beam_i_data = np.where(np.array(Ant_no_beam)[:,1] == str(beam_modes_ind))[0]
									if len(Ant_no_beam)>0:
										Ant_beam_i_data = np.array(Ant_no_beam)[np.array(Ant_no_beam)[:,1] == str(beam_modes_ind)]
										if Ant_beam_i_data.size > 0:
											#for Ant_data in Ant_beam_i_data:
											beam_dict[beam_modes_ind]['Ant_no'] = Ant_beam_i_data[:,2].astype(int).max()
										else:
											beam_dict[beam_modes_ind]['Ant_no'] = None
									else:
										print('No antenna recorded')
										output_file.write('No antenna recorded' + '\n')
									###############################################################################
									if len(band_info)>0:
										if len(np.unique(band_info, axis =0)) == 1:
											band_info_ind = -1
										elif len(beam_mode_list) == len(np.unique(band_info, axis =0)):
											band_info_ind = band_no_count
											band_no_count += 1
										elif len(beam_modes) == len(np.unique(band_info, axis =0)):
											band_info_ind = beam_modes_ind-1
										else:
											band_info_ind = (beam_modes_ind - 1)//len(np.unique(band_info, axis =0))

										try:
											beam_dict[beam_modes_ind]['Freq'] = int(band_info[band_info_ind][-1])
										except:
											beam_dict[beam_modes_ind]['Freq'] = band_info[band_info_ind][-1]
									else:
										print('No Frequency information recorded')
										output_file.write('No Frequency information recorded' + '\n')
							try:
								print('beam_dict = ', beam_dict)
								output_file.write('beam_dict = ' + str(beam_dict) + '\n')
								del band_info, beam_modes, Ant_no_beam, Ant_beam_i_data, beam_mode_list, beam_dict, band_info_ind, mjd_start, mjd_stop
							except:
								print('beam_dict not formed')
								output_file.write('beam_dict not formed' + '\n')
							print('################################################################################################')
							output_file.write('################################################################################################' + '\n')
			print(item, ' ::::::::::::::::::: Ends')
			output_file.write(item + ' ::::::::::::::::::: Ends' + '\n')
			print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
			output_file.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' + '\n')

end = time.time()
print('Time in sec :', end - start)




