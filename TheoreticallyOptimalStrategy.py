import pandas as pd
import numpy as np 		  	   		 	   			     			  	 
import pandas as pd
			     			  	 
from util import get_data

# Helper methods for testPolicy
def nextState(holdings):
    if holdings == 0:  # Current state: S0 (No holdings)
        transitions = np.array([0, 1000, -1000])
    elif holdings == 1000:  # Current state: S1 (Long position)
        transitions = np.array([0, -1000, -2000])
    elif holdings == -1000:  # Current state: S2 (Short position)
        transitions = np.array([0, 1000, 2000])
    else:
        raise ValueError("Invalid holdings value. Must be 0, 1000, or -1000.")
    return transitions

def price_direction(change):
    return np.where(change > 0, 'Up', np.where(change < 0, 'Down', 'No Change'))
    
def get_first_change_that_isnt_nochange(df, start_idx):
    changes = df.loc[start_idx:].query("price_direction != 'No Change'")
    if not changes.empty:
        return changes.iloc[0]['price_direction']
    else:
        return None
    
def get_next_day_direction(df, start_idx, current_direction):
    next_direction = df.loc[start_idx + 1, 'price_direction'] if start_idx + 1 < len(df) else None
    if current_direction == 'Up' and next_direction == 'Down':
        return 'Down'
    elif current_direction == 'Down' and next_direction == 'Up':
        return 'Up'
    else:
        return None

def testPolicy(symbol, sd, ed, sv):
    """
    This function simulates a trading policy for a given stock within a specified date range and starting portfolio value. 
    It generates a series of trades based on an unspecified strategy, aiming to optimize the portfolio's performance over the period.

    Parameters:
    - symbol (str): The ticker symbol of the stock to be traded.
    - sd (DateTime): The start date of the trading period.
    - ed (DateTime): The end date of the trading period.
    - sv (float): The starting value of the portfolio.

    Returns:
    - df_trades (DataFrame): A pandas DataFrame indexed by date, with a single column indicating the trade action for each day. 
      The trade actions are represented as follows:
        +1000.0 or +2000.0 for buying 1000 or 2000 shares, respectively,
        -1000.0 or -2000.0 for selling 1000 or 2000 shares, respectively,
        0.0 for making no trade.
      The net holdings are constrained to be within -1000, 0, or +1000 shares at any time.

    Note: The trade strategy implemented by this function is not detailed here and should be defined to optimize the portfolio's performance based on historical data, technical indicators, or any other defined criteria. The implementation of the strategy must ensure that it does not result in a net holding that exceeds the specified constraints.
    """
    stock_date_range = pd.date_range(sd, ed)
    ticker_data = get_data([symbol], stock_date_range, addSPY=False).dropna()

    tradable_days = list(ticker_data.index)

    mock_order_book = pd.DataFrame({'Date': tradable_days, 'Price': ticker_data[symbol].values})
    mock_order_book[symbol] = 0

    mock_order_book['price_change'] = np.diff(mock_order_book['Price'].values, prepend=0)
    mock_order_book['price_direction'] = price_direction(mock_order_book['price_change'])
    mock_order_book.drop(columns=['price_change'], inplace=True)

    current_holdings = 0
    actions = []

    for index, row in mock_order_book.iterrows():
        transitions = nextState(current_holdings)
        current_direction = row['price_direction']
        
        future_direction = None
        
        if current_direction == 'Up' or current_direction == 'Down':
            future_direction = get_next_day_direction(mock_order_book, index, current_direction)
        elif current_direction == "No Change":
            future_direction = get_first_change_that_isnt_nochange(mock_order_book, index)

        # If no future direction is found, it defaults to "No Change"
        if future_direction is None:
            future_direction = "No Change"
        
        # Choose the best transition based on the predicted future direction
        if future_direction == 'Up':
            best_transition = max(filter(lambda x: x >= 0, transitions), default=0)
        elif future_direction == 'Down':
            best_transition = min(filter(lambda x: x <= 0, transitions), default=0)
        else:
            best_transition = 0
        
        current_holdings += best_transition
        actions.append(best_transition)
        
    mock_order_book[symbol] = actions
    
    df_trades = pd.DataFrame(index=mock_order_book['Date'], data=mock_order_book[symbol].values)
    df_trades.columns = [symbol]
    
    return df_trades

def author():
    return 'mnavazhylau3'