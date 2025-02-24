# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 21:46:31 2025

@author: elisa

Function that updates all price data.
"""
import os

from commonfunc.db_handler import DbHandler
from commonfunc.fetch_update import FetcherUpdater
import pandas as pd

def update_crypto_prices(cryptos, db):
    """
    Updates price data for multiple cryptocurrencies and saves to the database.

    Parameters:
        cryptos (list): List of crypto symbols (e.g., ['BTC', 'ETH', 'SOL'])
        db (DbHandler): Database handler instance
    """
    fetch_update = FetcherUpdater()
    
    for crypto in cryptos:
        
        table_name = f"{crypto.lower()}_hourly"
        try:
            print(f"Updating {crypto} data...")
            update_df = fetch_update.add_price_data(crypto=crypto, table=table_name)
            
            # Check if update_df is valid before proceeding
            if update_df is not None and isinstance(update_df, pd.DataFrame) and not update_df.empty:
                db.save_to_db(update_df, table_name)
                print(f"{crypto} data successfully updated and saved.")
            else:
                print(f"No new data for {crypto} or API did not return valid data.")
                
        except Exception as e:
            print(f"Error updating {crypto}: {e}")



db = DbHandler()
# print(os.getcwd())

# List of cryptocurrencies to update
cryptos = ['BTC', 'ETH', 'SOL']

update_crypto_prices(cryptos, db)
    

# -----------------------------------------------------
# # add ETH price
# eth_df = fetch_update.first_price_fetch('ETH', start_time='2018-01-01 00:00:00')
# db.save_to_db(eth_df, 'eth_hourly')

# # add SOL price
# sol_df = fetch_update.first_price_fetch('SOL', start_time='2021-01-01 00:00:00')
# db.save_to_db(sol_df, 'sol_hourly')    
        