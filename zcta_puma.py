## import package, library
import pandas as pd
import numpy as np
import urllib
import requests
import os
import io
import json
import pylab as pl
import zipfile, os, natsort

## Load a crosswalk table for ZCTA and Census Tract
zcta_tract_url = 'https://www2.census.gov/geo/docs/maps-data/data/rel/zcta_tract_rel_10.txt?#'
## File layout including column descriptions here - https://www.census.gov/programs-surveys/geography/technical-documentation/records-layout/2010-zcta-record-layout.html#par_textimage_3
zcta_tr = pd.read_csv(zcta_tract_url, sep = ',')

## Geographic codes for NYC
ny_fp = 36
nyc_county_fp = [5, 47, 61, 81,85]

## Select rows for NYC, population-related columns for a weighting variable 
zcta_tr_nyc = zcta_tr[(zcta_tr['STATE'] == ny_fp) & (zcta_tr['COUNTY'].isin(nyc_county_fp))]
zcta_tr_nyc = zcta_tr_nyc[['ZCTA5', 'COUNTY', 'TRACT', 'POPPT', 'ZPOP', 'TRPOP', 'ZPOPPCT', 'TRPOPPCT']] 

## Load a crosswalk table for PUMA and Census Tract
tract_puma_url = 'https://www2.census.gov/geo/docs/maps-data/data/rel/2010_Census_Tract_to_2010_PUMA.txt'
tr_puma = pd.read_csv(tract_puma_url, sep = ',')

## Select rows for NYC
tr_puma_nyc = tr_puma[(tr_puma['STATEFP'] == ny_fp) & (tr_puma['COUNTYFP'].isin(nyc_county_fp))]

## Merge two crosswalk table by County and tract number
zcta_puma = pd.merge(zcta_tr_nyc, tr_puma_nyc,
                     how = 'outer', left_on = ['COUNTY', 'TRACT'], right_on = ['COUNTYFP', 'TRACTCE'])

## 11 combinations of County and Tract don't have ZCTA. Why? Are these Census Tract water areas? Need to investigate later
missing_zcta = zcta_puma[zcta_puma['ZCTA5'].isnull()]

## Exclude missing_zcta for now 
zcta_puma = zcta_puma[zcta_puma['ZCTA5'].notnull()]

## Create population columns
zcta_puma['pop2010'] = zcta_puma.groupby(['PUMA5CE','ZCTA5'])['POPPT'].transform('sum') ## population lives in each relation (ZCTA that within in a specific PUMA)
zcta_puma['pop2010_zcta_total'] = zcta_puma.groupby('ZCTA5')['POPPT'].transform('sum') ## Total Population of each ZCTA
zcta_puma['pop2010_puma_total'] = zcta_puma.groupby('PUMA5CE')['POPPT'].transform('sum') ## Total Population of each PUMA
zcta_puma['per_in_puma'] = zcta_puma.pop2010 / zcta_puma.pop2010_zcta_total ## % of total ZCTA population that lives in that PUMA
zcta_puma['per_of_puma'] = zcta_puma.pop2010 / zcta_puma.pop2010_puma_total ## % of total PUMA population that lives in that ZCTA
zcta_puma = zcta_puma.round(decimals = 2)


## Create a table which one row for every ZCTA/PUMA combination
zcta_puma_combo = zcta_puma.drop_duplicates(subset = ['ZCTA5', 'PUMA5CE'])

## Create a column of NYC Borough name 

def county_borough(COUNTYFP):
    if COUNTYFP == 5:
        return 'Bronx'
    elif COUNTYFP == 47:
        return 'Brooklyn'
    elif COUNTYFP == 61:
        return 'Manhattan'
    elif COUNTYFP == 81:
        return 'Queens'
    else:
        return 'Staten Island'

zcta_puma_combo['borough'] = zcta_puma_combo.COUNTYFP.apply(county_borough)

## Drop unnecessary columns 
col_zcta_puma = ['ZCTA5', 'STATEFP', 'COUNTYFP', 'borough' ,'PUMA5CE', 'pop2010', 'pop2010_zcta_total', 'pop2010_puma_total', 'per_in_puma', 'per_of_puma']
zcta_puma_combo = zcta_puma_combo[col_zcta_puma]

## Sort rows based on ZCTA and PUMA
zcta_puma_combo = zcta_puma_combo.sort_values(by = ['ZCTA5', 'PUMA5CE'])

## Create a flag column ('assigned') to identify a PUMA where the majority of a ZCTA's popuation lives
zcta_puma_combo['max_share'] = zcta_puma_combo.groupby('ZCTA5')['per_in_puma'].transform('max')
zcta_puma_combo['assigned'] = pd.np.where(zcta_puma_combo.per_in_puma == zcta_puma_combo.max_share, 1, 0)
zcta_puma_combo.loc[zcta_puma_combo['pop2010_zcta_total'] == 0, 'assigned'] = 1
zcta_puma_combo.drop(columns = 'max_share', inplace= True) 

## Crosswalk table for ZCTA to PUMA
zcta_puma = zcta_puma_combo[zcta_puma_combo['assigned'] == 1]

## Exporting two dfs into one excel file

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('zcta_puma_crosswalk.xlsx', engine='xlsxwriter')

# Write each dataframe to a different worksheet.
zcta_puma_combo.to_excel(writer, sheet_name='zcta_puma_combo', index = False)
zcta_puma.to_excel(writer, sheet_name='zcta_puma', index = False)