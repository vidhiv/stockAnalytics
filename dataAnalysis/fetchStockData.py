import pandas as pd
import pymysql
from sqlalchemy import create_engine
import get_data as gd

# Download and preprocess data
stocks = ["AMZN", "AAPL", "TSLA", "MSFT", "SQ", "GOOGL", "SHOP", "NVDA", "SE", "ABNB"] 
data = gd.download_data(stocks, "1d", "5m")
df = gd.preprocess_data(data, stocks)

# Insert data in mysql table
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
