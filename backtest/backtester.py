# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 21:01:46 2025

@author: elisa
"""

import pandas as pd
import numpy as np

class Backtester:
    """
    Class to handle the backtesting process.
    """
    def __init__(self, data, initial_capital=10000,
                 stop_loss=None, take_profit=None, position_sizing_func=None):
        """
        
        """
        
        self.data = data
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.position_sizing_func = position_sizing_func
        if self.position_sizing_func is None:
            # default position sizing func that invests 20% of total capital
            self.position_sizing_func = lambda cap: cap*0.2
        
        self.trades = [] # to record trades
        self.positions = 0 # how many coins/shares currently held
        self.results_df = None # will store the full equity curve
        
    def run_backtest(self):
        """ Runs the backtest based on generated signals, returns a result DataFrame."""
        
        # make sure df already has columns "signal":
        # Columns such as: ['time', 'utc_dt', 'nyc_dt', 'high', 'low', 'open', 'close', 
        #                   'volumefrom', 'volumeto', 'avg', 'signal']
        df = self.data.copy()  
        df = df.reset_index(drop=True)
        
        df['capital'] = np.nan
        df['positions'] = 0
        df['pnl'] = 0
        
        # track open price for the position
        entry_price = None 
        
        for i in range(len(df)):
            price = df.loc[i,'close']
            signal = df.loc[i,'signal']
            
            if self.positions == 0: # means currently no open position
                
                if signal == 1: # buy signal
                    # how many units to buy
                    size_value = self.position_sizing_func(self.current_capital)
                    units_to_buy = size_value / price
                    
                    # update capital
                    self.current_capital -= size_value
                    self.positions = units_to_buy
                    entry_price = price
                    
                    # record this trade
                    self.trades.append({
                        'index': i,
                        'time': df.loc[i,'nyc_dt'],
                        'type': 'buy',
                        'units': units_to_buy,
                        'price': price,
                        'capital_before': self.current_capital + size_value,
                        'capital_after': self.current_capital
                        })
                
            
            else:
                # means there's an open position
                current_pnl = (price - entry_price) * self.positions
                
                # check for stop loss/take profit
                if self.stop_loss is not None:
                    if price <= entry_price*(1 - self.stop_loss):
                        signal = -1
                
                if self.take_profit is not None:
                    if price >= entry_price*(1 + self.take_profit):
                        signal = -1
                
                if signal == -1: # sell signal
                    proceeds = price * self.positions
                    self.current_capital += proceeds
                    self.trades.append({
                        'index': i,
                        'time': df.loc[i,'nyc_dt'],
                        'type': 'sell',
                        'units': units_to_buy,
                        'price': price,
                        'capital_before': self.current_capital - proceeds,
                        'capital_after': self.current_capital
                        })
                
                    # reset to 0 and None
                    self.positions = 0
                    entry_price = None 
            
            # log performance each row
            df.loc[i,'capital'] = self.current_capital
            df.loc[i,'positions'] = self.positions
            
            if entry_price and self.positions:
                df.loc[i,'pnl'] = (df.loc[i,'close'] - entry_price) * self.positions
            else:
                df.loc[i,'pnl'] = 0
        
        self.results_df = df
        
        return df
            
            
    def get_report(self):
        """
        Summarize results: final capital, total pnl, etc.
        """
        total_trades = len(self.trades)
        final_capital = self.current_capital
        profit = final_capital - self.initial_capital
        roi_percentage = (profit / self.initial_capital) * 100
        max_drawdown = self._calculate_max_drawdown(self.results_df['capital'])
        
        report = {
            'Initial Capital': self.initial_capital,
            'Final Capital': final_capital,
            'Total Profit': profit,
            'ROI (%)': roi_percentage,
            'Number of Trades': total_trades,
            'Max Drawdown': max_drawdown,
            'Trade Details': self.trades
            }
        
        return report
            
            
    @staticmethod 
    def _calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """
        Calculates the Maximum Drawdown of an equity curve (capital over time).
        Max Drawdown = Maximum peak-to-trough decline, as a fraction of the peak.
        
        E.g., if the equity peaked at 12000, then dropped to 9000,
        drawdown = (12000 - 9000)/12000 = 0.25 or 25%.
        """
        # Rolling maximum of the equity
        rolling_max = equity_curve.cummax()
        # Drawdown at each point
        drawdown = (equity_curve - rolling_max) / rolling_max
        # Max drawdown is the minimum of that series
        max_dd = drawdown.min()
        return float(max_dd)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        