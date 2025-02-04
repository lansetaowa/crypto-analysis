# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 13:42:35 2025

@author: elisa
"""
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 13:42:35 2025

@author: elisa
"""

import numpy as np
import pandas as pd

# -------------------------------------------------------------------
# Base class to handle DataFrame copying and column name parameters.
# -------------------------------------------------------------------
class BaseIndicators:
    """
    A base class to handle DataFrame copying (in-place vs. returning a copy)
    and store column names like close_col, high_col, low_col.
    """
    def __init__(
        self,
        df: pd.DataFrame, 
        close_col: str = "close", 
        high_col: str = "high", 
        low_col: str = "low"
    ):
        self.df = df 
        self.close_col = close_col
        self.high_col = high_col
        self.low_col = low_col

# -------------------------------------------------------------------
# Overlap Indicators: SMAs, EMAs, Bollinger Bands, etc.
# -------------------------------------------------------------------
class OverlapIndicators(BaseIndicators):
    """Indicators that overlap with price, like SMAs, EMAs, Bollinger Bands."""
    def compute_sma(self, windows=[24, 72]):
        """
        Computes Simple Moving Averages for given window sizes.
        Columns added: 'sma_{window}'.
        """
        for window in windows:
            self.df[f"sma_{window}"] = (
                self.df[self.close_col].rolling(window=window).mean()
            )
        return self.df

    def compute_ema(self, windows=[24, 72]):
        """
        Computes Exponential Moving Averages for given window sizes.
        Columns added: 'ema_{window}'.
        """
        for window in windows:
            self.df[f"ema_{window}"] = (
                self.df[self.close_col].ewm(span=window, adjust=False).mean()
            )
        return self.df

    def compute_bollinger_bands(self, window=24, num_std=2):
        """
        Computes Bollinger Bands.
        Columns added: 'bollinger_upper_{window}', 'bollinger_lower_{window}'.
        """
        sma = self.df[self.close_col].rolling(window=window).mean()
        std = self.df[self.close_col].rolling(window=window).std()

        self.df[f"bollinger_upper_{window}"] = sma + (std * num_std)
        self.df[f"bollinger_lower_{window}"] = sma - (std * num_std)

        return self.df


# -------------------------------------------------------------------
# Volatility Indicators: ATR, etc.
# -------------------------------------------------------------------
class VolatilityIndicators(BaseIndicators):
    """Indicators focused on volatility, like ATR."""

    def compute_atr(self, window=14):
        """
        Computes Average True Range (ATR).
        Column added: 'atr_{window}'.
        """
        high_low = self.df[self.high_col] - self.df[self.low_col]
        high_close = np.abs(self.df[self.high_col] - self.df[self.close_col].shift(1))
        low_close = np.abs(self.df[self.low_col] - self.df[self.close_col].shift(1))

        # Combine into a single Series (row-wise max)
        true_range = pd.DataFrame({
            "hl": high_low,
            "hc": high_close,
            "lc": low_close
        }).max(axis=1)

        self.df[f"atr_{window}"] = true_range.rolling(window=window).mean()

        return self.df


# -------------------------------------------------------------------
# Momentum Indicators: RSI, MACD, Stoch, etc.
# -------------------------------------------------------------------
class MomentumIndicators(BaseIndicators):
    """Indicators measuring momentum, such as RSI, MACD, Stoch, etc."""

    def compute_rsi(self, window=14):
        """
        Computes Relative Strength Index (RSI).
        Column added: 'rsi_{window}'.
        """
        delta = self.df[self.close_col].diff(1)
        
        gain = delta.where(delta > 0, 0.0).rolling(window=window).mean()
        loss = -delta.where(delta < 0, 0.0).rolling(window=window).mean()
        
        rs = gain / loss
        self.df[f"rsi_{window}"] = 100 - (100 / (1 + rs))

        return self.df

    def compute_macd(self, short_span=12, long_span=26, signal_span=9):
        """
        Computes Moving Average Convergence Divergence (MACD).
        Columns added: 'macd', 'macd_signal'.
        """
        short_ema = self.df[self.close_col].ewm(span=short_span, adjust=False).mean()
        long_ema = self.df[self.close_col].ewm(span=long_span, adjust=False).mean()

        self.df["macd"] = short_ema - long_ema
        self.df["macd_signal"] = self.df["macd"].ewm(span=signal_span, adjust=False).mean()

        return self.df

    def compute_stochastic_oscillator(self, window=14):
        """
        Computes Stochastic Oscillator.
        Column added: 'stoch_osc_{window}'.
        """
        lowest_low = self.df[self.low_col].rolling(window=window).min()
        highest_high = self.df[self.high_col].rolling(window=window).max()
        
        self.df[f"stoch_osc_{window}"] = 100 * (
            (self.df[self.close_col] - lowest_low) / (highest_high - lowest_low)
        )

        return self.df

    def compute_stoch_rsi(self, window=14):
        """
        Computes Stochastic RSI.
        Column added: 'stoch_rsi_{window}'.
        """
        # We'll reuse the standard RSI logic:
        delta = self.df[self.close_col].diff(1)
        
        gain = delta.where(delta > 0, 0.0).rolling(window=window).mean()
        loss = -delta.where(delta < 0, 0.0).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        lowest_rsi = rsi.rolling(window=window).min()
        highest_rsi = rsi.rolling(window=window).max()
        
        self.df[f"stoch_rsi_{window}"] = 100 * (rsi - lowest_rsi) / (highest_rsi - lowest_rsi)

        return self.df


# -------------------------------------------------------------------
# Trend Indicators: ADX, CCI, etc.
# -------------------------------------------------------------------
class TrendIndicators(BaseIndicators):
    """Indicators measuring trend strength or direction, like ADX, CCI."""

    def compute_cci(self, window=20):
        """
        Computes Commodity Channel Index (CCI).
        Column added: 'cci_{window}'.
        """
        tp = (self.df[self.high_col] + self.df[self.low_col] + self.df[self.close_col]) / 3
        
        sma_tp = tp.rolling(window=window).mean()
        mean_dev = (tp - sma_tp).abs().rolling(window=window).mean()
        
        self.df[f"cci_{window}"] = (tp - sma_tp) / (0.015 * mean_dev)

        return self.df

    def compute_adx(self, window=14):
        """
        Computes Average Directional Index (ADX).
        Column added: 'adx_{window}'.
        """
        # Calculate directional movements
        plus_dm = self.df[self.high_col].diff()
        minus_dm = self.df[self.low_col].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        # Calculate True Range
        high_low = self.df[self.high_col] - self.df[self.low_col]
        high_close = np.abs(self.df[self.high_col] - self.df[self.close_col].shift(1))
        low_close = np.abs(self.df[self.low_col] - self.df[self.close_col].shift(1))
        
        true_range = pd.DataFrame({
            "hl": high_low,
            "hc": high_close,
            "lc": low_close
        }).max(axis=1)
        
        atr = true_range.rolling(window=window).mean()  # simple rolling for ATR

        # Compute +DI, -DI
        plus_di = (plus_dm.ewm(alpha = 1/window).mean() / atr) * 100
        minus_di = (abs(minus_dm).ewm(alpha = 1/window).mean() / atr) * 100

        # Finally compute ADX
        self.df[f"adx_{window}"] = (
            (plus_di - minus_di).abs() / (plus_di + minus_di)
        ) * 100
        self.df[f"plus_di_{window}"] = plus_di
        self.df[f"minus_di_{window}"] = minus_di

        return self.df


# -------------------------------------------------------------------
# "Master" class that composes the other classes internally.
# -------------------------------------------------------------------
class TechnicalIndicators:
    """
    One-stop class that unifies Overlap, Volatility, Momentum, and Trend indicators.
    """
    def __init__(
        self,
        df: pd.DataFrame,
        close_col: str = "close",
        high_col: str = "high",
        low_col: str = "low"
    ):
        """
        :param df: Price DataFrame.
        :param close_col: Column name for close price.
        :param high_col: Column name for high price.
        :param low_col: Column name for low price.
        """

        self.df = df 
        self.close_col = close_col
        self.high_col = high_col
        self.low_col = low_col

        # All sub-classes point to the *same* self.df so that each method modifies it
        self.overlap = OverlapIndicators(self.df, close_col, high_col, low_col)
        self.volatility = VolatilityIndicators(self.df, close_col, high_col, low_col)
        self.momentum = MomentumIndicators(self.df, close_col, high_col, low_col)
        self.trend = TrendIndicators(self.df, close_col, high_col, low_col)

    def compute_all_indicators(self):
        """
        Example method that calls many default indicators. 
        Returns the mutated self.df (with new indicator columns).
        """
        # Overlap
        self.overlap.compute_sma([24,72])
        self.overlap.compute_ema([24,72])
        self.overlap.compute_bollinger_bands(window=24, num_std=2)
        
        # Volatility
        self.volatility.compute_atr(window=14)
        
        # Momentum
        self.momentum.compute_rsi(window=14)
        self.momentum.compute_macd(short_span=12, long_span=26, signal_span=9)
        self.momentum.compute_stochastic_oscillator(window=14)
        self.momentum.compute_stoch_rsi(window=14)
        
        # Trend
        self.trend.compute_cci(window=20)
        self.trend.compute_adx(window=14)

        return self.df


    
    