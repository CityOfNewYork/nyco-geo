# Functions to retrieve, extract, and transform US Census Bureau
# Zip Code Tabulation Data

import urllib2
import urllister
import zipfile
import sys
import os

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

	print("Preparing to download: " + file_list[0] + file_list[1])
	con=urllib2.urlopen(file_list[0] + file_list[1])
	
	total_size = con.info().getheader('Content-Length').strip()
	total_size = int(total_size)

	bytes_so_far = 0

	save_file=open(file_list[1], "wb")

	while bytes_so_far < total_size:
	    buff = con.read(8192)
	    save_file.write(buff)
	    bytes_so_far += len(buff)

	    percent = float(bytes_so_far) / total_size
	    percent = round(percent*100, 2)
	    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))

	save_file.close()

	if bytes_so_far == total_size:
		success=True

	return success

#####
# Extract the zip file
def extractFile(filename):
	current_dir= os.getcwd()
	output_dir=os.path.join(current_dir, 'temp')
	
	if not os.path.exists(output_dir):
	    os.makedirs(output_dir)

	print("extracting file " + filename)
	zipfile.ZipFile(filename).extractall(output_dir)
