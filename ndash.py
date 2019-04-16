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

    arr_file=[]

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
            arr_file.insert(len(arr_file), tiger_path + str(year) + "/ZCTA5/")
            print("connection a success!")
            success=True
            parser=urllister.URLLister()
            parser.feed(usock.read())
            usock.close()
            parser.close()
            zipfile=[s for s in parser.urls if ".zip" in s]

    arr_file=arr_file + zipfile

##    filename=tiger_path + str(year) + "/ZCTA5/" + zipfile[0]
    return arr_file

##Takes a url and downloads the file to the local repository
def downloadFile(file_list):
    ## Download the zip file
    print("downloading the shapefile")
    download=urllib2.urlopen(file_list[0] + file_list[1])
    data=download.read()

    ##Save the file
    print("saving the zipfile")
    save_file=open(file_list[1], "wb")
    save_file.write(data)
    save_file.close()

##########

## Get list containing the path of zip file and the zip file name
tiger_zcta=findFile(cur_date.year)
print(tiger_zcta)

downloadFile(tiger_zcta)


