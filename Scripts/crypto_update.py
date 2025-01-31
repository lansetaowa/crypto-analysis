# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 21:46:31 2025

@author: elisa

WILL CONSOLIDATE TO FUNCTIONS LATER
"""

from CommonFunc.db_handler import DbHandler
from CommonFunc.fetch_update import FetcherUpdater


db = DbHandler()
fetch_update = FetcherUpdater()

# update BTC
update_df = fetch_update.add_price_data(crypto='BTC', table='btc_hourly')
db.save_to_db(update_df, 'btc_hourly')


# update ETH
update_df = fetch_update.add_price_data(crypto='ETH', table='eth_hourly')
db.save_to_db(update_df, 'eth_hourly')


# update SOL
update_df = fetch_update.add_price_data(crypto='SOL', table='sol_hourly')
db.save_to_db(update_df, 'sol_hourly')






# -----------------------------------------------------
# add ETH price
eth_df = fetch_update.first_price_fetch('ETH', start_time='2018-01-01 00:00:00')
db.save_to_db(eth_df, 'eth_hourly')

# add SOL price
sol_df = fetch_update.first_price_fetch('SOL', start_time='2021-01-01 00:00:00')
db.save_to_db(sol_df, 'sol_hourly')    
        