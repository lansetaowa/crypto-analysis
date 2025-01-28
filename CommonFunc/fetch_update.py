# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 08:40:48 2025

@author: elisa

Module that fetches from api for the 1st time for a specified start time
"""

import time
from datetime import datetime, timezone
import pandas as pd

from CommonFunc.crypto_api import CryptoAPI
from CommonFunc.db_handler import DbHandler

class FetcherUpdater:

    def __init__(self, db_file='Data/crypto.db'):
        self.handler = DbHandler(db_file)   
    
    def get_start_time(self, table, interval='hour'):
        "get start_time from a timestamp, which adds interval to max timestamp of existing data"
        
        max_timestamp = self.handler.get_max_timestamp(table)
        interval_seconds = 3600 if interval=='hour' else 60
        
        start_timestamp = max_timestamp + interval_seconds
        
        # convert to 'YYYY-MM-DD HH:MM:SS' format in utc
        start_time = datetime.utcfromtimestamp(start_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        return start_time
  
    def first_price_fetch(self, crypto, start_time, interval='hour', api_limit=2000):
        """
        Fetch and store historical price data starting from a given timestamp.
        
        Args:
            crypto(str): BTC/ETH/SOL, etc. 
            start_time(str): start time in format "YYYY-MM-DD HH:MM:SS" 
            interval(str): hour or minute 
                - (only support hour for now)
            api_limit(int): number of records per api call (default 2000)
        
        Returns:pd.DataFrame, the resulting DataFrame with all fetched data
        """
               
        # determine the interval in seconds
        interval_seconds = 3600 if interval=='hour' else 60
        
        # convert to unix timestamp
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            start_dt = start_dt.replace(tzinfo=timezone.utc) # ensure it's treated as utc
            start_ts = int(start_dt.timestamp())          
        except ValueError:
            raise ValueError("start_time must be in the format 'YYYY-MM-DD HH:MM:SS'.") 
            
        current_ts = int(time.time())
        
        # fetch and append data in chunks 
        result_df = pd.DataFrame()
        ts = start_ts
        
        while ts < current_ts:
            end_ts = min(ts+interval_seconds*api_limit, current_ts)
            
            # fetch data from API
            data = CryptoAPI.fetch_hourly_data(crypto=crypto, 
                                             end_ts=end_ts,
                                             num_records=api_limit)
            
            # transform and append to result_df
            df = CryptoAPI.transform_price_data(data)
            result_df = pd.concat([result_df, df], axis=0)
            
            # update ts for next loop
            ts = end_ts
        
        # drop duplicates
        result_df = result_df.drop_duplicates()
        result_df = result_df[result_df['time']>=start_ts]
        
        return result_df

    
    def add_price_data(self, crypto, table, interval='hour'):
        """
        Parameters
            crypto : str, type of crypto to fetch, BTC/ETH/SOL, etc.
            table : str, the table that gets updated later.
            interval : str (optional), level of price. The default is 'hour'.

        Returns: pd.DataFrame
        """
        
        max_timestamp = self.handler.get_max_timestamp(table)
        if not max_timestamp:
            raise ValueError(f"No existing data found in {table}. Use initial data fetch.")
        
        current_ts = int(time.time())
        interval_seconds = 3600 if interval=='hour' else 60
        
        if current_ts - max_timestamp < interval_seconds:
            print("Data is already up-to-date.")
            return
        else: 
            # get start_time in string
            start_time = self.get_start_time(table = table, 
                                             interval = interval) 
            
            df = self.first_price_fetch(crypto=crypto,
                                                    start_time = str(start_time),
                                                    interval=interval,
                                                    api_limit=2000)
        
        return df
        
        
        
        
        
        
        
        
        