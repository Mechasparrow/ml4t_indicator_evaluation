import pandas as pd
import numpy as np
from util import get_data

def author():
    return 'mnavazhylau3'

# Indicator 1: SMA (20 day window)
def compute_sma(price_data, period):
    return price_data.rolling(window=period).mean()

def EMA(prices_df, days):
    ema_df = prices_df.copy()
    
    prices = prices_df.values
    smoothing = 2 / (days + 1)
    ema = np.zeros(prices.shape[0])
    ema[0] = prices[0][0]

    for i in range(1, len(prices)):
        ema[i] = (prices[i] * smoothing) + (ema[i - 1] * (1 - smoothing))

    return ema_df


# Indicator 2: PPO
def PPO(prices_df):
    short_period = 12
    long_period = 26
    
    # Calculate short-term EMA
    EMA_short = EMA(prices_df, short_period)
    
    # Calculate long-term EMA
    EMA_long = EMA(prices_df, long_period)
    
    # Calculate PPO
    PPO_values = [(short - long) / long * 100 for short, long in zip(EMA_short, EMA_long)]
    Signal_Line = EMA(prices_df, 9)
    
    return PPO_values, Signal_Line

# Indicator 3: Bollinger Bands
def bollinger_bands(price_data):
    middle_band = price_data.rolling(window=20).mean()
    bb_std = middle_band.std()
    
    upper_band = middle_band + (2 * bb_std)
    lower_band = middle_band + (2 * bb_std)
    
    return lower_band, middle_band, upper_band

# Indicator 4: Momentum

# Momentum / Rate of Change
def rate_of_change(price_data, n_periods):
    close_n_periods_ago = price_data.shift(n_periods)
    roc = ((price_data - close_n_periods_ago) / close_n_periods_ago)
    return roc

# Indicator 5:  Stochastic Indicator
def stochastic_K(high, low, close):
    # Calculate L14 and H14
    L14 = low.rolling(window=14).min()
    H14 = high.rolling(window=14).max()
    
    # Calculate %K
    percent_K = ((close - L14) / (H14 - L14)) * 100
    
    return percent_K

def stochastic_D(percent_K):
    # Calculate %D
    percent_D = percent_K.rolling(window=3).mean()
    
    return percent_D


def run():
    pass

if __name__ == "__main__":
    run()