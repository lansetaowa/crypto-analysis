# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 14:50:03 2025

@author: elisa

Module to handle db interactions, including:
    - get max_timestamp from an existing db table
    - save a df to db 
    - read from db and return a df
"""

import sqlite3
import pandas as pd

class DbHandler:
    def __init__(self, db_file='Data/crypto.db'):
        self.db_file = db_file
    
    def get_max_timestamp(self, table):
        """Get the largest timestamp from the specified table."""
        conn = sqlite3.connect(self.db_file)
        query = f"select max(time) from {table}"
        result = pd.read_sql(query, conn)
        conn.close()
        
        return result.iloc[0,0] 
    
    def save_to_db(self, df, table):
        """Save a df to a specified db table"""
        conn = sqlite3.connect(self.db_file)
        df.to_sql(table, conn, if_exists="append", index=False)
        conn.close()
    
    def read_from_db(self, sql_query):
        """return a dataframe from a sql query"""
        conn = sqlite3.connect(self.db_file)
        df = pd.read_sql(sql_query, conn)
        conn.close()
        return df
    
    def table_exists(self, table):
        """check if a table exists in the database"""
        conn = sqlite3.connect(self.db_file)
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
        result = pd.read_sql(query, conn)
        conn.close()
        return not result.empty