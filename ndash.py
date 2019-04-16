## This script makes the following assumptions:
## 1. The Census will not update their domain or their file system

## Importing necessary libraries and files
import urllib2
import urllister
import os
import datetime

# Get the current working directory
os.getcwd()

cur_date = datetime.datetime.now()

# Checks to see if there is a zip for the current year
# If it does not exist, then decrements year until a
# file is found
def findFile(year):
    tiger_path="https://www2.census.gov/geo/tiger/TIGER"

    success=False

    while success==False:
        try:
            usock=urllib2.urlopen(tiger_path + str(year) + "/ZCTA5")
        except urllib2.HTTPError, e:
            print(e.code)
            year = year -1
        except urllib2.URLError, e:
            print(e.args)
            year = year -1
        else:
            success=True
            parser=urllister.URLLister()
            parser.feed(usock.read())
            usock.close()
            parser.close()
            zipfile=[s for s in parser.urls if ".zip" in s]

    filename=tiger_path + str(year) + "/ZCTA5/" + zipfile[0]
    return filename


## Get path for a TIGER file to download
tiger_zcta=findFile(cur_date.year)
print(tiger_zcta)

## Download the zip file
