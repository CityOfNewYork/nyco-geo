# Downloads, extracts, and merges US Census shapefiles
# to generate a usable zip code geodataframe for NYC

## Importing necessary libraries and files
import os
import datetime
import re
import ndash_func
import poverty
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from glob import glob

# Get the current working directory
os.getcwd()

cur_date = datetime.datetime.now()

# census values for state and counties
fips='36'
counties = [
'Bronx', 
'Kings', 
'New York', 
'Queens', 
'Richmond']

###############
# COUNTY Download and Extraction
print('#####\n')
print('Downloading and extracting US County Data')
county_url=ndash_func.findFile(cur_date.year, 'COUNTY')
ndash_func.downloadFile(county_url)
if ndash_func.fileExists(county_url):
  county_file=ndash_func.extractFile(county_url)
  print(county_file)

# county_file='tl_2018_us_county'
county_shp = gpd.read_file(county_file + '.shp')

# EXTRACT: only the NYC counties that fall in NYS
nyc_counties=county_shp[(county_shp['NAME'].isin(counties)) & (county_shp['STATEFP']==fips) ]

###############
# PUBLIC USE MICRODATA AREAS (PUMA) Download and Extraction
print('#####\n')
print('Downloading and extracting PUMA Data')
puma_url=ndash_func.findFile(cur_date.year, 'PUMA')
ndash_func.downloadFile(puma_url)
if ndash_func.fileExists(puma_url):
  puma_file=ndash_func.extractFile(puma_url)
  print(puma_file)

# puma_file='tl_2018_36_puma10'
puma_shp = gpd.read_file(puma_file + '.shp')
puma_shp['PUMACE10']=puma_shp['PUMACE10'].astype(int)

# OVERLAY: Overlay PUMA and NYC Counties
nyc_puma = gpd.overlay(puma_shp, nyc_counties, how='intersection')

###############
# TIGER Zip Code Tabulation Areas Census Data Set Download and Extraction
print('#####\n')
print('Downloading and extracting US ZCTA Data')
zcta_url=ndash_func.findFile(cur_date.year, 'ZCTA5')
ndash_func.downloadFile(zcta_url)
if ndash_func.fileExists(zcta_url):
  zcta_file=ndash_func.extractFile(zcta_url)
  print(zcta_file)

# zcta_file='tl_2018_us_zcta510'
zcta_shp = gpd.read_file(zcta_file + '.shp')

###############
# OVERLAY: Overlaying PUMA and counties on top of ZCTA
nyc_zcta_puma = gpd.overlay(nyc_puma, zcta_shp, how='intersection')

# DISSOLVE: by zipcode
nyc_zcta_puma_dissolved = nyc_zcta_puma.dissolve(by='GEOID10_2')

# FILTER: keeping relevant columns
nyc_zipcodes=nyc_zcta_puma_dissolved.filter([
'ZCTA5CE10',
'NAMELSAD10',
'NAME',
'STATEFP',
'COUNTYFP',
'COUNTYNS',
'PUMACE10',
'ALAND10_2',
'AWATER10_2',
'INTPTLAT10_2',
'INTPTLON10_2',
'geometry'
])

###############
# CROSSWALK COMPARISON
print('#####\n')
print('Beginning comparison and merge of crosswalk data\n')
xls = pd.ExcelFile('zcta_puma_crosswalk.xlsx')
crosswalk = pd.read_excel(xls, 'zcta_puma')
crosswalk.rename(columns={
  'ZCTA5':'ZCTA5CE10',
  }, inplace=True)

crosswalk['ZCTA5CE10']=crosswalk['ZCTA5CE10'].astype(str)

# perform a merge based on ZCTACE10
nyc_zip_crosswalk = nyc_zipcodes.merge(crosswalk, on='ZCTA5CE10')
nyc_zip_crosswalk['PUMACE10']=nyc_zip_crosswalk['PUMACE10'].astype(int)

# FIND MATCHES
mismatches = nyc_zip_crosswalk.query('PUMACE10 != PUMA5CE')

# replace the original NAMELSAD10
for index, mm in mismatches.iterrows():
  mismatches['NAMELSAD10'][index] = puma_shp[puma_shp['PUMACE10']==mm['PUMA5CE']]['NAMELSAD10'].values[0]

# replace NAMELSAD10 with the new PUMA names
nyc_zip_crosswalk.ix[mismatches.index, 'NAMELSAD10'] = mismatches.NAMELSAD10

# drop unnecessary columns
nyc_zip_crosswalk = nyc_zip_crosswalk.drop(['NAME', 'STATEFP_x', 'COUNTYFP_x', 'COUNTYNS','PUMACE10', 'assigned'], axis=1)

###############
print('#####\n')
print('Breaking down neighborhoods and community districts into columns\n')
# SPLIT: NAMESLAD into Community Districts and Neighborhoods
nyc_zip_crosswalk[['NAMELSAD10','NBH']] = nyc_zip_crosswalk['NAMELSAD10'].str.split('--',expand=True)
nyc_zip_crosswalk['NBH'] = nyc_zip_crosswalk['NBH'].str.replace(' PUMA','')

# create community district column
nyc_zip_crosswalk = nyc_zip_crosswalk[nyc_zip_crosswalk['NAMELSAD10'].str.contains("Community District")]
nyc_zip_crosswalk[['NAMELSAD10','CD_CODE']] = nyc_zip_crosswalk['NAMELSAD10'].str.split('District ',expand=True)
nyc_zip_crosswalk['CD_CODE'] = nyc_zip_crosswalk['CD_CODE'].str.replace(' & ',',')

# prefix community district code with Manhattan
nyc_zip_crosswalk['CD_CODE'] = nyc_zip_crosswalk['CD_CODE'].str.replace(r'(?is)[0-9]+2', r'M\g<0>')
nyc_zip_crosswalk['CD_CODE'] = nyc_zip_crosswalk['CD_CODE'].str.replace(r'(?is)\b\d\b', r'M0\g<0>')
nyc_zip_crosswalk['CD_CODE'] = nyc_zip_crosswalk['CD_CODE'].str.replace(r'^[0-9]{1,2}', r'M\g<0>')

# re-assign correct prefix for community district based on borough
nyc_zip_crosswalk.loc[nyc_zip_crosswalk.borough == 'Bronx', 'CD_CODE'] = nyc_zip_crosswalk['CD_CODE'].str.replace('M','B')
nyc_zip_crosswalk.loc[nyc_zip_crosswalk.borough == 'Brooklyn', 'CD_CODE'] = nyc_zip_crosswalk['CD_CODE'].str.replace('M','K')
nyc_zip_crosswalk.loc[nyc_zip_crosswalk.borough == 'Queens', 'CD_CODE'] = nyc_zip_crosswalk['CD_CODE'].str.replace('M','Q')
nyc_zip_crosswalk.loc[nyc_zip_crosswalk.borough == 'Staten Island', 'CD_CODE'] = nyc_zip_crosswalk['CD_CODE'].str.replace('M','S')

# drop unnecessary columns
nyc_zip_crosswalk = nyc_zip_crosswalk.drop(['NAMELSAD10'], axis=1)

###############
print('#####\n')
print('Preparing export - renaming and reordering columns\n')
# rename columns
nyc_zip_crosswalk.rename(columns={
  'ZCTA5CE10': 'zcta',
  'ALAND10_2' : 'area_land',
  'AWATER10_2': 'area_water',
  'INTPTLAT10_2': 'internal_lat',
  'INTPTLON10_2': 'internal_lon',
  'geometry': 'geometry',
  'STATEFP_y': 'state_fp',
  'COUNTYFP_y': 'county_fp',
  'borough': 'borough',
  'PUMA5CE': 'puma_code',
  'pop2010': 'pop_zcta_puma',
  'pop2010_zcta_total': 'pop_zcta',
  'pop2010_puma_total': 'pop_puma',
  'per_in_puma': 'percent_zcta_puma',
  'per_of_puma': 'percent_puma_zcta',
  'NBH': 'neighborhoods',
  'CD_CODE': 'community_districts'
  }, inplace=True)

# reorder columns
nyc_zip_crosswalk = nyc_zip_crosswalk[[
  'zcta',
  'borough',
  'neighborhoods',
  'community_districts',
  'puma_code',
  'county_fp',
  'state_fp',
  'pop_zcta_puma',
  'pop_zcta',
  'pop_puma',
  'percent_zcta_puma',
  'percent_puma_zcta',
  'area_land',
  'area_water',
  'internal_lat',
  'internal_lon',
  'geometry'
  ]]

##############
# NYCGOV: attach the NYCgov poverty rate
print('###### Adding the NYCgov Poverty')
nycgov_df = poverty.getNYCGovPoverty()

# copy the poverty rate to the main df
for i, cd in nycgov_df.iterrows():
  nyc_zip_crosswalk.loc[nyc_zip_crosswalk['community_districts'] == cd.community_districts, 'nycgov_cd_pov_rate'] = cd.nycgov_cd_pov_rate

##############
# CENSUS: attach the Census poverty data
print('###### Adding the Census Poverty')
census_df = poverty.getCensusPoverty(cur_date.year, ','.join(nyc_zip_crosswalk.zcta.values.tolist()))
nyc_zip_crosswalk = nyc_zip_crosswalk.merge(census_df, on='zcta', how='left')

# calculate the poverty rate based on the community district
cd_df = pd.DataFrame()
cds = nyc_zip_crosswalk['community_districts'].unique()

for cd in cds:
  temp_df = nyc_zip_crosswalk.loc[nyc_zip_crosswalk['community_districts'] == cd][[
      'community_districts', 'census_total_pov', 'census_total_pop']]
  temp_df['census_total_pov'] = pd.to_numeric(temp_df['census_total_pov'])
  temp_df['census_total_pop'] = pd.to_numeric(temp_df['census_total_pop'])
  temp_df_summed = temp_df.groupby(temp_df.community_districts).sum()
  cd_df = cd_df.append(temp_df_summed, sort=False)

# calculate the povertt rate for the cd
cd_df['census_cd_pov_rate'] = (
    cd_df['census_total_pov']/cd_df['census_total_pop'])*100
cd_df.reset_index(level=0, inplace=True)
cd_df = cd_df[['community_districts', 'census_cd_pov_rate']]

nyc_zip_crosswalk = nyc_zip_crosswalk.merge(cd_df, on='community_districts', how='left')

print(nyc_zip_crosswalk)

###############
# EXPORT: GeoJSON
print('#####\n')
print('Exporting GeoJSON, nyco-zipcodes.geojson\n')
nyc_zip_crosswalk.to_file("nyco-zipcodes.geojson", driver='GeoJSON')

##############
# CLEAN: remove the downloaded files
print('#####\n')
print('Removing shapefiles and zips\n')
ext = [
  '*.cpg',
  '*.dbf',
  '*.prj',
  '*.shp',
  '*.shx',
  '*.zip',
  '*.xml'
  ]

for e in ext:
  for file in glob(e):
    os.remove(file)
