# NYCO ZIP CODES

This repository contains python scripts that generate a GeoJSON containing NYC zip codes, community districts, and public use microdata areas (PUMAs) compiled using the Zip code tabulation areas provided by the US Census Bureau.

`crosswalk.py` - Generates a Excel workbook of zip code relationships with PUMAs and total population via US Census.
`nyco-zipcodes.py` - Relies on the Crosswalk workbook and US Census Tiger/Line geospatial datasets to generate a geoJSON that contains NYC zip codes, their community districts, neighborhoods, PUMAs, and population.
