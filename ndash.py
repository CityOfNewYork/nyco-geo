## This script makes the following assumptions:
## 1. The Census will not update their domain or their file system

## Importing necessary libraries and files

import os
import datetime
import censusdata

# Get the current working directory
os.getcwd()

cur_date = datetime.datetime.now()

##########

## Get list containing the path of zip file and the zip file name
tiger_zcta=censusdata.findFile(cur_date.year)
print(tiger_zcta)

censusdata.downloadFile(tiger_zcta)
print("FILE DOWNLOADED")
# make a call to extract the 
# extractFile(tiger_zcta[1])



