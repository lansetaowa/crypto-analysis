# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 15:46:03 2025

@author: elisa
"""

import pandas as pd
from strategies.base_strategy import BaseStrategy

class MACDStrategy(BaseStrategy):
    """
    A simple MACD crossover strategy:
    - Buy when MACD crosses above MACD signal
    - Sell when MACD crosses below MACD signal
    """
    def generate_signals(self):
        # for a single DataFrame
        df = self.data.copy()
        
        df['signal'] = 0
        df['signal'] = df.apply(
            lambda row: 1 if row['macd'] > row['macd_signal'] else
                        -1 if row['macd'] < row['macd_signal'] else 0,
                        axis=1
        )
        
        return df


class RSIStrategy(BaseStrategy):
    """
    RSI-based strategy:
        - buy if RSI < lower_threshold (oversold)
        - sell if RSI > upper_threshold (overbought)
    """
    def __init__(self, data, params=None):
        super().__init__(data, params=params)
        # RSI thresholds can be stored in params or use defaults
        self.lower_threshold = self.params.get('lower_threshold',30)
        self.upper_threshold = self.params.get('upper_threshold',70)
        
    def generate_signals(self):
        df = self.data.copy()
        
        df['signal'] = 0
        df.loc[df['rsi'] < self.lower_threshold, 'signal'] = 1
        df.loc[df['rsi'] > self.upper_threshold, 'signal'] = -1
        
        return df
        