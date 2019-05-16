# Downloads, extracts, and merges US Census shapefiles
# to generate a usable zip code geodataframe for NYC

## Importing necessary libraries and files
import os
import datetime
import ndash_func
import geopandas as gpd
import matplotlib.pyplot as plt
from glob import glob

# Get the current working directory
os.getcwd()
print(os.getcwd())

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
county_url=ndash_func.findFile(cur_date.year, 'COUNTY')
ndash_func.downloadFile(county_url)
if ndash_func.fileExists(county_url):
  county_file=ndash_func.extractFile(county_url)
  print(county_file)

county_file='tl_2018_us_county'
county_shp = gpd.read_file(county_file + '.shp')

# EXTRACT: only the NYC counties that fall in NYS
nyc_counties=county_shp[(county_shp['NAME'].isin(counties)) & (county_shp['STATEFP']==fips) ]

###############
# PUBLIC USE MICRODATA AREAS (PUMA) Download and Extraction
puma_url=ndash_func.findFile(cur_date.year, 'PUMA')
ndash_func.downloadFile(puma_url)
if ndash_func.fileExists(puma_url):
  puma_file=ndash_func.extractFile(puma_url)
  print(puma_file)

puma_file='tl_2018_36_puma10'
puma_shp = gpd.read_file(puma_file + '.shp')

# OVERLAY: Overlay PUMA and NYC Counties
nyc_puma = gpd.overlay(puma_shp, nyc_counties, how='intersection')

###############
# TIGER Zip Code Tabulation Areas Census Data Set Download and Extraction
zcta_url=ndash_func.findFile(cur_date.year, 'ZCTA5')
ndash_func.downloadFile(zcta_url)
if ndash_func.fileExists(zcta_url):
  zcta_file=ndash_func.extractFile(zcta_url)
  print(zcta_file)

zcta_file='tl_2018_us_zcta510'
zcta_shp = gpd.read_file(zcta_file + '.shp')

###############
# MERGING DATASETS
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

# UPDATE: Borough Names
nyc_zipcodes['NAME'] = nyc_zipcodes['NAME'].str.replace('Kings','Brooklyn')
nyc_zipcodes['NAME'] = nyc_zipcodes['NAME'].str.replace('Richmond','Staten Island')

# SPLIT: NAMESLAD into Community Districts and Neighborhoods
nyc_zipcodes[['NAMELSAD10','NBH']] = nyc_zipcodes['NAMELSAD10'].str.split('--',expand=True)
nyc_zipcodes['NBH'] = nyc_zipcodes['NBH'].str.replace(' PUMA','')

# RENAME: columns
nyc_zipcodes.rename(columns={
  'NAMELSAD10':'CD',
  'NAME':'BORO',
  'ALAND10_2' : 'ALAND10',
  'AWATER10_2' : 'AWATER10',
  'INTPTLAT10_2' : 'INTPTLAT10',
  'INTPTLON10_2' : 'INTPTLON10'
  }, inplace=True)

# REARRANGE: column order
nyc_zipcodes = nyc_zipcodes[[
'ZCTA5CE10',
'BORO',
'CD',
'NBH',
'STATEFP',
'COUNTYFP',
'COUNTYNS',
'PUMACE10',
'ALAND10',
'AWATER10',
'INTPTLAT10',
'INTPTLON10',
'geometry'
]]

# PLOT: the merged dataset
nyc_zipcodes.plot()
plt.show()

# EXPORT: GeoJSON
nyc_zipcodes.to_file("nyco-nyc_zipcodes.geojson", driver='GeoJSON')

###############
# CLEAN: remove the downloaded files
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