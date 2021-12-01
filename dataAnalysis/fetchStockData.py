import yfinance as yf 
import pandas as pd
import pymysql
from sqlalchemy import create_engine
# The 10 stocks used for the purpose of this project: Stock Name : Ticker Name Amazon AMZN Apple AAPL Tesla TSLA Microsoft MSFT Square SQ Google GOOGL Shopify SHOP NVIDIA NVDA 
# SE Sea Ltd Airbnb ABNB
stocks = ["AMZN", "AAPL", "TSLA", "MSFT", "SQ", "GOOGL", "SHOP", "NVDA", "SE", "ABNB"] 
data = yf.download(# or pdr.get_data_yahoo(
     # tickers list or string as well
     tickers = "AMZN AAPL TSLA MSFT SQ GOOGL SHOP NVDA SE ABNB",
     # use "period" instead of start/end valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max (optional, default is '1mo')
     period = "1d",
     # fetch data by interval (including intraday if period < 60 days) valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo (optional, default is '1d')
     interval = "5m",
     # group by ticker (to access via data['SPY']) (optional, default is 'column')
     group_by = 'ticker',
     # adjust all OHLC automatically (optional, default is False)
     auto_adjust = True,
     # download pre/post regular market hours data (optional, default is False)
     prepost = True,
     # use threads for mass downloading? (True/False/Integer) (optional, default is True)
     threads = True,
     # proxy URL scheme use use when downloading? (optional, default is None)
     proxy = None ) 
frames = [] 
for i in stocks: 
	frames.append(data[i])
data_denormalized = data.reset_index(level=0)
data_denormalized.rename(columns={'index':'datetime'})
df = pd.concat(frames, keys=stocks).reset_index()
df.dropna(inplace=True)
df.reset_index(drop=True)
data_columns = ["stock_ticker", "stock_time", "open_price", "high_price", "low_price", "close_price", "volume"]
df.columns = data_columns
db = pymysql.connect(
        host='stockanalytics.cbz7og9zfi6s.us-east-1.rds.amazonaws.com', user="admin",password="Stock65%",
            port=3306, database="StockAnalytics")
try:
    with db.cursor() as cur:
        cur.execute('TRUNCATE TABLE StockAnalytics.accounts_raw_stock_data')
finally:
    db.close()
engine = create_engine("mysql+pymysql://admin:Stock65%@stockanalytics.cbz7og9zfi6s.us-east-1.rds.amazonaws.com/StockAnalytics")
df.to_sql('accounts_raw_stock_data',engine,index=False,if_exists='append')
