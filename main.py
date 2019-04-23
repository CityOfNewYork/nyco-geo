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
# TIGER Census Data Set Download and Extraction
# Get list containing the path of zip file and the zip file name
zcta_url=ndash_func.findFile(cur_date.year)
zcta_fn=ndash_func.downloadFile(zcta_url)

# download the tiger files and pass the output name
if zcta_fn != '':
	# extract the file
	ndash_func.extractFile(zcta_fn)
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