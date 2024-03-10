import pandas as pd
import numpy as np	  	   		 	   			  		 			     			  	 
from util import get_data

def author():
    return 'mnavazhylau3'

def get_order_book_from_df_trades(df_trades):
    df_trades_symbol = df_trades.columns[0]
    df_trades_order_book = df_trades.loc[df_trades[df_trades_symbol] != 0].copy()

    complete_order_frame = {
        "Date": [],
        "Symbol": [],
        "Order": [],
        "Shares": []
    }

    for idx,row in df_trades_order_book.iterrows():
        shares = row[df_trades_symbol]
        
        order_type = "BUY"
        if shares < 0:
            order_type = "SELL"
            
        complete_order_frame["Date"].append(pd.Timestamp(idx))
        complete_order_frame["Symbol"].append(df_trades_symbol)
        complete_order_frame["Order"].append(order_type)
        complete_order_frame["Shares"].append(abs(shares))
        
    return pd.DataFrame(complete_order_frame)

def compute_portvals_from_tradedf(
    df_trades,
    start_val=1000000,  		  	   		 	   			  		 			     			  	 
    commission=9.95,  		  	   		 	   			  		 			     			  	 
    impact=0.005, 
):
    min_date = df_trades.index.min()
    max_date = df_trades.index.max()
    orders = get_order_book_from_df_trades(df_trades)
    return compute_portvals(orders, min_date, max_date, start_val, commission, impact)

def compute_portvals(  		  	   		 	   			  		 			     			  	 
    orders,  		 
    sd,
    ed,  	   		 	   			  		 			     			  	 
    start_val=1000000,  		  	   		 	   			  		 			     			  	 
    commission=9.95,  		  	   		 	   			  		 			     			  	 
    impact=0.005,
 		  	   		 	   			  		 			     			  	 
):  		  	   		 	   			  		 			     			  	 
    """  		  	   		 	   			  		 			     			  	 
    Computes the portfolio values.  		  	   		 	   			  		 			     			  	 
  		  	   		 	   			  		 			     			  	 
    :param orders_file: Path of the order file or the file object  		  	   		 	   			  		 			     			  	 
    :type orders_file: str or file object  		  	   		 	   			  		 			     			  	 
    :param start_val: The starting value of the portfolio  		  	   		 	   			  		 			     			  	 
    :type start_val: int  		  	   		 	   			  		 			     			  	 
    :param commission: The fixed amount in dollars charged for each transaction (both entry and exit)  		  	   		 	   			  		 			     			  	 
    :type commission: float  		  	   		 	   			  		 			     			  	 
    :param impact: The amount the price moves against the trader compared to the historical data at each transaction  		  	   		 	   			  		 			     			  	 
    :type impact: float  		  	   		 	   			  		 			     			  	 
    :return: the result (portvals) as a single-column dataframe, containing the value of the portfolio for each trading day in the first column from start_date to end_date, inclusive.  		  	   		 	   			  		 			     			  	 
    :rtype: pandas.DataFrame  		  	   		 	   			  		 			     			  	 
    """  		  	   		 	   			  		 			     			  	 
        
    ticker_symbols = list(orders['Symbol'].unique())
    stock_date_range = pd.date_range(sd, ed)
    ticker_data = get_data(ticker_symbols, stock_date_range, addSPY=False).dropna()
    tradable_days = list(ticker_data.index)
    
    shares_dataframe = pd.DataFrame({'Date': pd.to_datetime(tradable_days) })
    shares_dataframe['Cash'] = np.nan

    stock_holdings = {}
    stock_holding_np = {}
    cash_impact_array = np.full(len(orders), 0, dtype=float)
        
    for ticker_symbol in ticker_symbols:
        shares_dataframe[ticker_symbol] = np.nan
        
        stock_holdings[ticker_symbol] = 0
        stock_holding_np[ticker_symbol] = np.full(len(orders), 0, dtype=int)

    orders['order_amount'] = np.where(orders['Order'] == "BUY", orders['Shares'], -orders['Shares'])
    cash_impact_array = -orders.apply(lambda x: (x['order_amount'] * float(ticker_data.loc[x['Date']][x['Symbol']])) + abs(impact * x['order_amount'] * float(ticker_data.loc[x['Date']][x['Symbol']])) + commission, axis=1).values

    for idx, row in orders.iterrows():
        stock_holding_np[row['Symbol']][idx] = row['order_amount']
        
    cumsum_df = pd.DataFrame({'Date': pd.to_datetime(orders['Date']) })
    cumsum_df['Cash'] = start_val + np.cumsum(cash_impact_array)
    
    for ticker_symbol in ticker_symbols:
        cumsum_df[ticker_symbol] = np.cumsum(stock_holding_np[ticker_symbol])
        
    merged_dataframe = pd.merge(shares_dataframe, cumsum_df, on='Date', how='left', suffixes=('', '_cumsum'))
    shares_dataframe['Cash'] = merged_dataframe['Cash_cumsum'] 

    for ticker in ticker_symbols:
        shares_dataframe[ticker] = merged_dataframe[ticker + "_cumsum"]

    if shares_dataframe.iloc[0].isna().any():
        shares_dataframe['Cash'].iloc[0] = start_val
        
        for ticker_symbol in ticker_symbols:
            shares_dataframe[ticker_symbol].iloc[0] = 0
            

    shares_dataframe.ffill(inplace=True)

    for ticker in ticker_symbols:
        shares_dataframe[ticker] = shares_dataframe[ticker].values * ticker_data[ticker].values
                                            
    return pd.DataFrame(index=shares_dataframe['Date'], data=shares_dataframe.sum(axis=1).values)