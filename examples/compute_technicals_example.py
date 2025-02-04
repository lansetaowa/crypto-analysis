# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 19:02:49 2025

@author: elisa
"""

from commonfunc.db_handler import DbHandler
from dataprocess.tech_indicator import TechnicalIndicators

# get data
db = DbHandler()

crypto = 'SOL'
table_name = f"{crypto.lower()}_hourly"
query = f'select * from {table_name}'
df = db.read_from_db(query)

# 1) If you only need Bollinger, ATR, etc., directly use the specialized classes:
vol = VolatilityIndicators(df.copy())
df_atr = vol.compute_atr(window=14)  # returns a new df with 'atr_14'

# 2) Or do everything in one place:
ti = TechnicalIndicators(df.copy())
df_all = ti.compute_all_indicators()  # returns new df with many indicators
print(df_all.columns)

