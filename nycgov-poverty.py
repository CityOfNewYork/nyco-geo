# Gets the NYCgov poverty rate at the community district level
import urllib2
import urllister
import re
import pandas as pd
import ast

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
      12: 'nycgov_poverty_rate',
      1: 'community_districts'
  }, inplace=True)

  return nycgov_df
