# Functions to retrieve, extract, and transform US Census Bureau
# Zip Code Tabulation Data

import urllib2
import urllister
import zipfile

#####
# Checks to see if there is a zip for the current year
# If it does not exist, then decrements year until a
# file is found
def findFile(year):
    data_path="https://www2.census.gov/geo/tiger/TIGER"

    file_list=[]

    success=False
    print(data_path + str(year) + "/ZCTA5")
    
    while success==False:
        try:
			con=urllib2.urlopen(data_path + str(year) + "/ZCTA5")
        except urllib2.HTTPError, e:
            print(str(e.code) + " connection failed! Decrementing year and trying again.")
            year = year -1
        except urllib2.URLError, e:
            print(str(e.args)  + " connection failed! Decrementing year and trying again.")
            year = year -1
        else:
            print("Connection a success!")
            success=True
            file_list.insert(len(file_list), data_path + str(year) + "/ZCTA5/")
            parser=urllister.URLLister()
            parser.feed(con.read())
            con.close()
            parser.close()
            zipfile=[s for s in parser.urls if ".zip" in s]

    file_list=file_list + zipfile

    return file_list

#####
# Takes a url and downloads the file to the local repository
# Extracts the zip file
def downloadFile(file_list):
	success=False

	print(file_list[0] + file_list[1])
	while success==False:
		try:
			con=urllib2.urlopen(file_list[0] + file_list[1])
		except urllib2.HTTPError, e:
			if e.code==500:
				print(e.code + " connection failed!")
				break
			print(e.code + " connection failed! Trying again.")
		except urllib2.URLError, e:
			if e.code==500:
				print(e.code + " connection failed!")
				break
			print(e.code + " connection failed! Trying again.")
        else:
			success=True
			print("Downloading the file: " + file_list[1])
			data=con.read()

			##Save the file
			print("saving the zipfile")
			save_file=open(file_list[1], "wb")
			save_file.write(data)
			save_file.close()

	return success

def extractFile(filename):
	print("extracting file " + filename)
	zipfile.ZipFile(filename)
