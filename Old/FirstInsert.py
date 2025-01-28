# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 20:54:27 2024

@author: elisa
"""

import json, requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3

# ------------------------------------btc historical price------------------------
apikey = "96d32d6bab952712bdac0ffdee08f84a394eae5aa10b5483e1ecadf7cc59b4f4"
def get_price_hour(crypto, to):
    url = 'https://min-api.cryptocompare.com/data/v2/histohour?fsym={0}&tsym=USD&limit=2000&toTs={1}'.format(crypto,to)
    res = requests.get(url).text
    data = json.loads(res)
    return data

def to_timestamp(from_dt):
    dt = datetime.strptime(from_dt, "%Y-%m-%d %H:%M:%S")
    timestamp = int(dt.timestamp())
    return timestamp

# res = get_price_hour(crypto="BTC", to=1734908400)

# res['Data']['TimeFrom']
# res['Data']['TimeTo']

# current time: 1734908400, datetime.datetime(2024, 12, 22, 23, 0, tzinfo=zoneinfo.ZoneInfo(key='UTC'))

# btc timestamp list
btc_ts = [1734908400 - x*7200000 for x in range(45)] # 3750 days, back to 2014/12/9 7:00:00

btc_df = pd.DataFrame()
for ts in btc_ts:
    res = get_price_hour(crypto="BTC", to=ts)
    df = pd.DataFrame(res['Data']['Data'])
    btc_df = pd.concat([btc_df, df], axis=0)

btc_df = btc_df.drop_duplicates()
btc_df['utc_dt'] = btc_df['time'].apply(lambda x: datetime.utcfromtimestamp(x).replace(tzinfo=ZoneInfo("UTC")))
btc_df['nyc_dt'] = btc_df['utc_dt'].apply(lambda x: x.astimezone(ZoneInfo("America/New_York")))
btc_df.drop(['conversionType','conversionSymbol'], axis=1, inplace=True)

# avg trade price during this hour
btc_df['avg'] = btc_df['volumeto']/btc_df['volumefrom']

# order columns
columns = ['time','utc_dt','nyc_dt','high','low','open','close','volumefrom','volumeto','avg']
btc_df = btc_df[columns]

# save to db
db_file = "Data/crypto.db"
conn = sqlite3.connect(db_file)
btc_df.to_sql("btc_hourly", conn, if_exists="append", index=False)
conn.close()

# -------------------------------- funding rate btcusdt ---------------------------------
# funding rate timestamp list
start_ts = to_timestamp('2014-12-01 00:00:00')*1000
to_ts = to_timestamp(str(datetime.now().replace(hour=1,minute=0,second=0,microsecond=0)))*1000

funding_start_list = [start_ts]
ts = start_ts
while ts < to_ts:
    ts = ts + 1000*8*3600*1000
    funding_start_list.append(ts)

# get funding rate from Binance
def get_funding_rate(symbol, start_time):
    url = "https://fapi.binance.com/fapi/v1/fundingRate?symbol={0}&startTime={1}&limit=1000".format(symbol, start_time)
    res = requests.get(url).text
    data = json.loads(res)
    return data

btcusdt_funding_df = pd.DataFrame()
for ts in funding_start_list:
    res = get_funding_rate(symbol="BTCUSDT", start_time=ts)
    df = pd.DataFrame(res)
    btcusdt_funding_df = pd.concat([btcusdt_funding_df,df], axis=0)
    
btcusdt_funding_df = btcusdt_funding_df.drop_duplicates()
btcusdt_funding_df = btcusdt_funding_df.sort_values('fundingTime')

btcusdt_funding_df['time'] = btcusdt_funding_df['fundingTime'].apply(lambda x: datetime.utcfromtimestamp(round(x/1000,0)).replace(tzinfo=ZoneInfo("UTC")))
btcusdt_funding_df['diff'] = btcusdt_funding_df['time'] - btcusdt_funding_df['time'].shift()

# btcusdt_funding_df = pd.merge(left=btcusdt_funding_df, right=btc_df[['utc_dt','avg']], left_on='time',right_on='utc_dt',how='left')

# save to db
db_file = "Data/crypto.db"
conn = sqlite3.connect(db_file)
btcusdt_funding_df.to_sql("btc_funding_rate", conn, if_exists="append", index=False)
conn.close()



