import pandas as pd
import numpy as np	  	   		 	   			  		 			     			  	 
from util import get_data

def compute_portvals_from_tradedf(
    df_trades,
    start_val=1000000,  		  	   		 	   			  		 			     			  	 
    commission=9.95,  		  	   		 	   			  		 			     			  	 
    impact=0.005, 
):
    pass

def author():
    return 'mnavazhylau3'

def compute_portvals(  		  	   		 	   			  		 			     			  	 
    orders_file="./orders/orders.csv",  		  	   		 	   			  		 			     			  	 
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
    
    # Load in the orders
    orders = pd.read_csv(orders_file)
    orders['Date'] = pd.to_datetime(orders['Date'])
    orders = orders.sort_values(by='Date', ascending=True)

    min_date = orders['Date'].min()
    max_date = orders['Date'].max()
    ticker_symbols = list(orders['Symbol'].unique())
    stock_date_range = pd.date_range(min_date, max_date)

    pertinent_stock_data = get_data(ticker_symbols, stock_date_range)
    pertinent_stock_data.drop(columns=['SPY'], inplace=True)

    pertinent_stock_data_with_filled_data = pd.DataFrame({'Date': pd.date_range(min_date, max_date) }).set_index('Date').join(pertinent_stock_data).fillna(method='ffill')

    shares_dataframe = pd.DataFrame({'Date': pd.date_range(min_date, max_date) })

    shares_dataframe['Cash'] = np.nan
    shares_dataframe.loc[0,'Cash'] = start_val

    for ticker in ticker_symbols:
        shares_dataframe[ticker] = np.nan
        shares_dataframe.loc[0,ticker] = 0
        
    # Convert 'Date' column to datetime type in shares_dataframe DataFrame
    shares_dataframe['Date'] = pd.to_datetime(shares_dataframe['Date'])

    for _, row in orders.iterrows():    
        order_date = row['Date']
        order_symbol = row['Symbol']
        shares_amount = row['Shares']
        order_type = row['Order']
        
        previous_order_date = order_date - pd.Timedelta(days=1)
        shares_dataframe.loc[shares_dataframe['Date'] <= previous_order_date] = shares_dataframe.loc[shares_dataframe['Date'] <= previous_order_date].fillna(method='ffill')
        
        if (shares_dataframe.loc[shares_dataframe['Date'] == order_date, order_symbol].isnull().values.any() and not shares_dataframe.loc[shares_dataframe['Date'] == previous_order_date,order_symbol].empty):
            previous_stock_amount = shares_dataframe.loc[shares_dataframe['Date'] == previous_order_date, order_symbol].iloc[0]
            shares_dataframe.loc[shares_dataframe['Date'] == order_date, order_symbol] = previous_stock_amount
            
        if (shares_dataframe.loc[shares_dataframe['Date'] == order_date, 'Cash'].isnull().values.any() and not shares_dataframe.loc[shares_dataframe['Date'] == previous_order_date,'Cash'].empty):
            previous_order_cash = shares_dataframe.loc[shares_dataframe['Date'] == previous_order_date, 'Cash'].iloc[0]
            shares_dataframe.loc[shares_dataframe['Date'] == order_date, 'Cash'] = previous_order_cash
        
        if order_type == "BUY":
            order_amount = shares_amount
        else:
            order_amount = -shares_amount

        share_cost = float(pertinent_stock_data.loc[order_date][order_symbol])
        order_cost = share_cost * order_amount
            
        current_shares = float(shares_dataframe.loc[shares_dataframe['Date'] == order_date, order_symbol].iloc[0])
        current_cash = float(shares_dataframe.loc[shares_dataframe['Date'] == order_date,'Cash'].iloc[0])
        
        shares_dataframe.loc[shares_dataframe['Date'] == order_date,order_symbol] = current_shares + order_amount
        shares_dataframe.loc[shares_dataframe['Date'] == order_date,'Cash'] = current_cash - order_cost - abs(impact * order_cost) - commission
        
    shares_dataframe.ffill(inplace=True)  

    full_value_dataframe = shares_dataframe.copy()
    full_value_dataframe[ticker_symbols] = shares_dataframe[ticker_symbols].multiply(pertinent_stock_data_with_filled_data[ticker_symbols].values, axis='index')
    
    df1 = pd.DataFrame({"Date": full_value_dataframe['Date'], "Values": full_value_dataframe.sum(axis=1).values})
    df2 = pd.DataFrame({"Date": list(pertinent_stock_data.index)})

    daily_port_val = pd.merge(df1, df2, on="Date")

    # Set "Date" as the index of the daily_port_val dataframe
    daily_port_val.set_index("Date", inplace=True)
     	   			  		 			     			     			  	 
    return pd.DataFrame(index=daily_port_val.index, data=daily_port_val.values)