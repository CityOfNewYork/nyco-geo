## This script makes the following assumptions:
## 1. The Census will not update their domain or their file system

## Importing necessary libraries and files

import os
import datetime
import censusdata
import opendata

# Get the current working directory
os.getcwd()

cur_date = datetime.datetime.now()

##########

## Get list containing the path of zip file and the zip file name
tiger_zcta=censusdata.findFile(cur_date.year)
print(tiger_zcta)

if censusdata.downloadFile(tiger_zcta):
    print(tiger_zcta[1] + "Successfully Downloaded")

	# extract the file
	censusdata.extractFile(tiger_zcta[1])
else:
	print('Something went wrong. Inform the team.')