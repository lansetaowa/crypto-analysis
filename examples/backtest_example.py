# -*- coding: utf-8 -*-

"""
Example usage of backtest and strategy modules for MACD strategy
"""

import pandas as pd

from commonfunc.db_handler import DbHandler
from strategies.univariate_strategy import MACDStrategy, RSIStrategy
from strategies.multivariate_strategy import MACDRSIStrategy
from backtest.backtester import Backtester

# get data
db = DbHandler()

crypto = 'SOL'
table_name = f"{crypto.lower()}_hourly"
query = f'select * from {table_name}'
df = db.read_from_db(query)

def compute_macd(df, short_window=12, long_window=26, signal_window=9):

    df['ema_short'] = df['close'].ewm(span=short_window, adjust=False).mean()
    df['ema_long'] = df['close'].ewm(span=long_window, adjust=False).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['macd_signal'] = df['macd'].ewm(span=signal_window, adjust=False).mean()
    return df

def compute_rsi(df, window=14):
    """
    Compute the Relative Strength Index (RSI).

    Args:
        df (pd.DataFrame): DataFrame containing a 'close' column.
        window (int): Lookback period for RSI calculation.

    Returns:
        pd.Series: RSI values.
    """
    # Calculate price changes
    delta = df['close'].diff()

    # Calculate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate average gains and losses
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    # Calculate RS
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    return rsi

df = compute_macd(df)
df['rsi'] = compute_rsi(df)

df_test = df[(df['nyc_dt']>='2023-08-01')&(df['nyc_dt']<'2024-01-01')] 

# Example 1: MACD Strategy
macd_strategy = MACDStrategy(data=df_test)
df_test = macd_strategy.generate_signals()

backtester_macd = Backtester(
    data=df_test,
    initial_capital=10000,
    stop_loss=0.04,
    take_profit=None,
    position_sizing_func= lambda cap: cap*1)

result_macd = backtester_macd.run_backtest()
report_macd = backtester_macd.get_report()

# Example 2: RSI Strategy
rsi_strategy = RSIStrategy(data=df_test,
                           params={
                               'lower_threshold': 30,
                               'upper_threshold': 70
                               })

df_test = rsi_strategy.generate_signals()

backtester_rsi = Backtester(data = df_test,
                            initial_capital=10000,
                            stop_loss=0.04,
                            take_profit=0.15,
                            position_sizing_func=lambda cap: cap*0.2
                            )

result_rsi = backtester_rsi.run_backtest()
report_rsi = backtester_rsi.get_report()

# Example 3: RSI and MACD strategy
macdrsi_strategy = MACDRSIStrategy(data=df_test,
                                   params={
                                       'lower_threshold': 35,
                                       'upper_threshold': 65
                                       })

df_test = macdrsi_strategy.generate_signals()

backtester_macdrsi = Backtester(data = df_test,
                                initial_capital=10000,
                                stop_loss=0.04,
                                take_profit=0.15,
                                position_sizing_func=lambda cap: cap*1
                                )

result_macdrsi = backtester_macdrsi.run_backtest()
report_macdrsi = backtester_macdrsi.get_report()











