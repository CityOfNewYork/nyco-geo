# Functions to retrieve, extract, and transform US Census Bureau
# Zip Code Tabulation Data

import urllib2
import requests
import urllister
import zipfile
import sys
import os, os.path

#####
# Checks to see if there is a zip for the current year
# If it does not exist, then decrements year until a
# file is found
def findFile(year, dataset):
    data_path="https://www2.census.gov/geo/tiger/TIGER"

    success=False
    print(data_path + str(year) + "/" + dataset)
    
    while success==False:
        try:
			con=urllib2.urlopen(data_path + str(year) + "/" + dataset)
        except urllib2.HTTPError, e:
            print(str(e.code) + " connection failed! Decrementing year and trying again.")
            year = year -1
        except urllib2.URLError, e:
            print(str(e.args)  + " connection failed! Decrementing year and trying again.")
            year = year -1
        else:
            print("Connection a success!")
            success=True
            parser=urllister.URLLister()
            parser.feed(con.read())
            con.close()
            parser.close()
            zipfile=[s for s in parser.urls if ".zip" in s]

    file_url=data_path + str(year) + "/"+ dataset + "/" + ''.join(zipfile)

    return file_url

#####
# Takes a url and downloads the file to the local repository
def downloadFile(file_url):
	success=False

	if file_url.endswith('.zip'):
		filename=downloadZip(file_url)
	else:
		filename=downloadUrl(file_url)
	
	return filename

#####
# Used when the URL is a direct source of the file
def downloadZip(file_url):
	con=urllib2.urlopen(file_url)

	filename=file_url.split('/')[-1]

	if os.path.isfile(filename):
		print(filename + ' already exists!')
		return filename
	else:
		print('Downloading ' + filename)
		total_size = con.info().getheader('Content-Length').strip()
		total_size = int(total_size)

		bytes_so_far = 0

		save_file=open(filename, "wb")

		while bytes_so_far < total_size:
		    buff = con.read(8192)
		    save_file.write(buff)
		    bytes_so_far += len(buff)

		    percent = float(bytes_so_far) / total_size
		    percent = round(percent*100, 2)
		    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))

		save_file.close()

		if bytes_so_far == total_size:
			print(filename + ' successfully downloaded!')
			return filename

#####
# Used when the URL triggers a download of a zip file
def downloadUrl(file_url):
	req=requests.get(file_url)

	cd = req.headers['Content-Disposition'].split('"')
	index_match=[i for i, s in enumerate(cd) if ".zip" in s]
	filename=cd[index_match[0]]

	if os.path.isfile(filename):
		print(filename + ' already exists!')
		return filename
	else:
		print('Downloading ' + filename)
		
		with open(filename, 'wb') as f:
			f.write(req.content)

		print(filename + ' successfully downloaded!')

		return filename


#####
# Extract the zip file
def extractFile(filename):
	current_dir= os.getcwd()

	output_dir=os.path.join(current_dir, os.path.splitext(filename)[0])
	
	if not os.path.exists(output_dir):
	    os.makedirs(output_dir)

	# check to see that the file exists, or exit
	if not os.path.isfile(filename):
		print('Cannot find + ' + filename)
		sys.exit()

	print('Beginning extraction')
	
	zipfile.ZipFile(filename).extractall(output_dir)
	print(filename + ' extraction complete!')

