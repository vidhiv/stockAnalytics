# IMPORTS for Stock Analytics
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
import math

# STOCKS USED:
# The 10 stocks with their tickers used for the purpose of this project:
# 1. Amazon - AMZN
# 2. Apple - AAPL
# 3. Tesla - TSLA
# 4. Microsoft - MSFT
# 5. Square - SQ
# 6. Alphabet - GOOGL
# 7. Shopify - SHOP
# 8. NVIDIA - NVDA
# 9. SE - Sea Ltd
# 10. Airbnb - ABNB

# DOWNLOAD stock data from yahoo finance api 
def download_data(stocks):
    data = yf.download(
            # tickers list or string as well
            tickers = stocks,

            # use "period" instead of start/end
            # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            # (optional, default is '1mo')
            period = "10y",

            # fetch data by interval (including intraday if period < 60 days)
            # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            # (optional, default is '1d')
            interval = "1d",

            # group by ticker (to access via data['SPY'])
            # (optional, default is 'column')
            group_by = 'ticker',

            # adjust all OHLC automatically
            # (optional, default is False)
            auto_adjust = True,

            # download pre/post regular market hours data
            # (optional, default is False)
            prepost = True,

            # use threads for mass downloading? (True/False/Integer)
            # (optional, default is True)
            threads = True,

            # proxy URL scheme use use when downloading?
            # (optional, default is None)
            proxy = None
        )
    return data

# DATA PREPROCESSING 
def preprocess_data(data, stocks):
    data_denormalized = data.reset_index(level=0)
    data_denormalized.rename(columns={'index':'datetime'})

    # Append data of all stocks as rows
    frames = []
    for i in stocks:
        frames.append(data[i])
    df = pd.concat(frames, keys=stocks).reset_index()

    # Rename columns of data
    data_columns = ["stock_ticker", "stock_time", "open_price", "high_price", "low_price", "close_price", "volume"]
    df.columns = data_columns

    # Convert data type of timestamp to pandas datetime
    df['stock_time'] = pd.to_datetime(df['stock_time'])

    # Drop null rows
    df.dropna(inplace=True)
    df.reset_index(drop=True)
    
    return df