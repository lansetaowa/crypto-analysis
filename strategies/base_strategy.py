# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 15:16:31 2025

@author: elisa
"""

from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    All derived classes must implement the generate_signal() method.
    """
    def __init__(self, data, params=None):
        """
        :param data: A pandas DataFrame or dictionary of DataFrames. 
                     Each DataFrame typically has columns such as 
                     ['time', 'open', 'high', 'low', 'close', 'volume', 'macd', 'rsi'].
        :param params: Dictionary or object containing strategy parameters (if any).
        """
        self.data = data
        self.params = params if params else {}
        
    @abstractmethod 
    def generate_signals(self):
        """
        This method should create a 'signal' column (or columns) in self.data, 
        indicating buy/sell/hold signals, e.g.:
            +1 for buy, -1 for sell, 0 for hold
        """
        pass