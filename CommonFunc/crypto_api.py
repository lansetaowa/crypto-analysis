# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 15:28:48 2025

@author: elisa

Module that manages API calls to fetch data for:
    - different crypto currencies and intervals (from cryptocompare.com)
    - funding rates (from binance)
"""

import json
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

class CryptoAPI:
    
    PRICE_BASE_URL = "https://min-api.cryptocompare.com/data/v2/"
    BINANCE_BASE_URL = "https://fapi.binance.com/fapi/v1/"
    
    @staticmethod
    def fetch_hourly_data(crypto: str, end_ts: int, num_records: int=2000):
        """
        Fetch 2000 records of historical data that ends at end_ts
        crypto: type of crypto currency, such as: BTC, ETH, SOL
        num_records: default 2000 for this api
        """
        
        url = f"{CryptoAPI.PRICE_BASE_URL}histohour?fsym={crypto}&tsym=USD&limit={num_records}&toTs={end_ts}"
        res = requests.get(url).text
        data = json.loads(res)
        
        return data['Data']['Data']
    
    @staticmethod
    def transform_price_data(data):
        "Transform and create columns from fetched price data"
        
        df = pd.DataFrame(data)
        df = df.drop_duplicates()
        df['utc_dt'] = df['time'].apply(lambda x: datetime.utcfromtimestamp(x).replace(tzinfo=ZoneInfo("UTC")))
        df['nyc_dt'] = df['utc_dt'].apply(lambda x: x.astimezone(ZoneInfo("America/New_York")))
        
        # avg trade price during this hour
        df['avg'] = df['volumeto']/df['volumefrom']

        # order columns
        columns = ['time','utc_dt','nyc_dt','high','low','open','close','volumefrom','volumeto','avg']
        df = df[columns]
        
        return df
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    