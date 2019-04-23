## This script makes the following assumptions:
## 1. The Census will not update their domain or their file system

## Importing necessary libraries and files

import os
import datetime
import ndash_func
from nycdatasets import *

# Get the current working directory
os.getcwd()

cur_date = datetime.datetime.now()

#####
# TIGER Zip Code Tabulation Areas Census Data Set Download and Extraction
zcta_url=ndash_func.findFile(cur_date.year, 'ZCTA5')
zcta_fn=ndash_func.downloadFile(zcta_url)

# download the tiger files and pass the output name
if zcta_fn != '':
	# extract the file
	ndash_func.extractFile(zcta_fn)
else:
	print('Something went wrong. Inform the team.')

#####
# TIGER County Census Data Set Download and Extraction
county_url=ndash_func.findFile(cur_date.year, 'COUNTY')
county_fn=ndash_func.downloadFile(county_url)

# download the tiger files and pass the output name
if county_fn != '':
	# extract the file
	ndash_func.extractFile(county_fn)
else:
	print('Something went wrong. Inform the team.')

#####
# Neighborhood Tabulation Areas (NTA) Download and Extraction
# Download the data from the open data portal
nta_fn=ndash_func.downloadFile(nta_url)
if nta_fn !='':
	# extract the file
	ndash_func.extractFile(nta_fn)
else:
	print('Something went wrong. Inform the team.')