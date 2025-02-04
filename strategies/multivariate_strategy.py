# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 16:26:00 2025

@author: elisa
"""

import pandas as pd
from strategies.base_strategy import BaseStrategy

class MACDRSIStrategy(BaseStrategy):
    """
    Example strategy that combines MACD and RSI conditions.
    - Buy if MACD > MACD signal AND RSI < some threshold
    - Sell if MACD < MACD signal AND RSI > some threshold
    """
    def __init__(self, data, params=None):
        super().__init__(data, params=params)
        # Use MACD/RSI thresholds from params or defaults
        self.rsi_buy_threshold = self.params.get('rsi_buy_threshold', 35)
        self.rsi_sell_threshold = self.params.get('rsi_sell_threshold', 65)
        
    def generate_signals(self):
        
        df = self.data.copy()
        
        condition_buy = (df['macd'] > df['macd_signal']) & (df['rsi'] < self.rsi_buy_threshold)
        condition_sell = (df['macd'] < df['macd_signal']) & (df['rsi'] > self.rsi_sell_threshold)
        
        df['signal']=0
        df.loc[condition_buy, 'signal'] = 1
        df.loc[condition_sell, 'signal'] = -1
        
        return df
    
    