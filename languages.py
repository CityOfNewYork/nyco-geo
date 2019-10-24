import requests
import pandas as pd
import json

url = "https://api.census.gov/data/2018/acs/acs1?get=B16002_002E,B16002_003E,B16002_006E,B16002_012E,B16002_015E,B16002_018E,B16002_021E,B16002_033E&for=public%20use%20microdata%20area:03701,03702,03703,03704,03705,03706,03707,03708,03709,03710,03801,03802,03803,03804,03805,03806,03807,03808,03809,03810,03901,03902,03903,04001,04002,04003,04004,04005,04006,04007,04008,04009,04010,04011,04012,04013,04014,04015,04016,04017,04018,04101,04102,04103,04104,04105,04106,04107,04108,04109,04110,04111,04112,04113,04114&in=state:36"

response = requests.get(url)
str_data = response.content

data = json.loads(str_data)

data_df = pd.DataFrame(data)

data_df.columns = data_df.iloc[0]
data_df = data_df[1:]

data_df.rename(columns={
  "B16002_002E": "census_english",
  "B16002_003E": "census_spanish",
  "B16002_006E": "census_french_haitian_cajun",
  "B16002_012E": "census_russian_polish",
  "B16002_015E": "census_indo_european",
  "B16002_018E": "census_korean",
  "B16002_021E": "census_chinese",
  "B16002_033E": "census_arabic",
  "state": "state",
  "public use microdata area": "puma_code"
  }, inplace=True)

del data_df['state']


# save as a csv
data_df.to_csv('language_spoken.csv', index=False)