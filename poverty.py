# Gets the NYCgov poverty rate at the community district level
import urllib2
import urllister
import re
import pandas as pd
import ast

###
# Gets the NYCgov Poverty Rate data from NYCO website
###
def getNYCGovPoverty():
  # read the data from the nycopp site
  jsfile = "https://www1.nyc.gov/assets/opportunity/js/agencies/cd_data.js"
  con = urllib2.urlopen(jsfile)
  nycgov_str = con.read()
  con.close()

  # replace strings
  nycgov_str = re.sub("cd_data\[[0-9]*\]\ =\ ", "", nycgov_str)
  nycgov_str = re.sub(";", "", nycgov_str)

  # convert strings to lists
  nycgov_list = nycgov_str.split('\n')
  nycgov_list.pop(0)
  nycgov_list.pop(len(nycgov_list)-1)

  nycgov_list = [ast.literal_eval(i) for i in nycgov_list]

  # create a dataframe
  nycgov_df = pd.DataFrame(nycgov_list)[[11, 12]]
  # if the community district column does not contain any of the boroughs, then, remove it from the dataframe
  nycgov_df = nycgov_df[~nycgov_df[11].str.contains(
      'Manhattan|Bronx|Brooklyn|Queens|Staten') == False]

  nycgov_df[[11, 'Neighborhood']] = nycgov_df[11].str.split(' \(', expand=True)
  nycgov_df[11] = nycgov_df[11].str.replace('Staten Island', 'StatenIsland')

  temp_df = nycgov_df[11].str.split(" ", 1, expand=True)
  temp_df[1] = temp_df[1].str.replace(' & ', ',')

  # prefix community district code with Manhattan
  temp_df[1] = temp_df[1].str.replace(r'(?is)[0-9]+2', r'M\g<0>')
  temp_df[1] = temp_df[1].str.replace(r'(?is)\b\d\b', r'M0\g<0>')
  temp_df[1] = temp_df[1].str.replace(r'^[0-9]{1,2}', r'M\g<0>')

  # update the community district codes
  temp_df.loc[temp_df[0] == 'Bronx', 1] = temp_df[1].str.replace('M', 'B')
  temp_df.loc[temp_df[0] == 'Brooklyn', 1] = temp_df[1].str.replace('M', 'K')
  temp_df.loc[temp_df[0] == 'Queens', 1] = temp_df[1].str.replace('M', 'Q')
  temp_df.loc[temp_df[0] == 'StatenIsland', 1] = temp_df[1].str.replace('M', 'S')

  nycgov_df = nycgov_df.join(temp_df)
  collist = [12, 1]
  nycgov_df = nycgov_df[collist]

  nycgov_df.rename(columns={
      12: 'nycgov_cd_pov_rate',
      1: 'community_districts'
  }, inplace=True)

  return nycgov_df

###
# Connects to the Census API and gets the population in poverty and total pop, calculates the poverty rate
###
def getCensusPoverty(year, zipcodes):
  success = False
  while success == False:
    try:
      url = 'https://api.census.gov/data/' + str(year) + '/acs/acs5?get=B06012_002E,B06012_001E&for=zip+code+tabulation+area:' + str(zipcodes)
      print('Connecting to ' + url)
      con = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
      print(e)
      year = year - 1
    else:
      print("Connection a success!")
      print(year)
      success = True
      census_data = con.read()
      con.close()

  # make a call to the api to see if anything returns. If it doesn't decrement the year
  census_data = ast.literal_eval(census_data)
  census_data.pop(0)

  # convert the response into a dataframe
  census_df = pd.DataFrame(census_data)
  census_df.rename(columns={
      0: 'census_total_pov',
      1: 'census_total_pop',
      2: 'zcta'
  }, inplace=True)

  # create the poverty rate column by dividing total in pov by the total pop
  census_df['census_pov_rate'] = (pd.to_numeric(
      census_df['census_total_pov'])/pd.to_numeric(census_df['census_total_pop']))*100

  return census_df
