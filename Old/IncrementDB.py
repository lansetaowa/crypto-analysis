# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 21:06:01 2024

@author: elisa
"""

import json, requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import sqlite3

# Get the current date and time in UTC
now_utc = datetime.now(timezone.utc)
utc_timestamp = int(now_utc.timestamp())

# get the largest timestamp from existing data
db_file = "Data/crypto.db"
conn = sqlite3.connect(db_file)
query = "SELECT max(time) FROM btc_hourly "
result = pd.read_sql(query, conn)
max_timestamp = result.iloc[0,0]

# get the final timestamp and number of records
diff = np.floor((utc_timestamp - max_timestamp)/3600)
ts_to = int(max_timestamp + 3600*diff)

def get_price_hour(crypto, num_records, to):
    url = 'https://min-api.cryptocompare.com/data/v2/histohour?fsym={0}&tsym=USD&limit={1}&toTs={2}'.format(crypto,num_records,to)
    res = requests.get(url).text
    data = json.loads(res)
    return data

res = get_price_hour(crypto="BTC", num_records = diff-1, to=ts_to)
df = pd.DataFrame(res['Data']['Data'])

# clean and transform
df['utc_dt'] = df['time'].apply(lambda x: datetime.utcfromtimestamp(x).replace(tzinfo=ZoneInfo("UTC")))
df['nyc_dt'] = df['utc_dt'].apply(lambda x: x.astimezone(ZoneInfo("America/New_York")))
df.drop(['conversionType','conversionSymbol'], axis=1, inplace=True)

# avg trade price during this hour
df['avg'] = df['volumeto']/df['volumefrom']

# order columns
columns = ['time','utc_dt','nyc_dt','high','low','open','close','volumefrom','volumeto','avg']
df = df[columns]

# save to db
db_file = "Data/crypto.db"
conn = sqlite3.connect(db_file)
df.to_sql("btc_hourly", conn, if_exists="append", index=False)
conn.close()

