# IMPORTS for Stock Analytics
import pandas as pd
import sklearn
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import style
from datetime import datetime
import datetime

# CORRELATION FUNCTIONS

# Find correlation
def get_correlation(df):
    # Prepare comparison dataframe with close price of all the 10 stocks
    dfcomp = pd.DataFrame()
    dfcomp["Date"] = df["stock_time"].dt.date
    for name, group in df.groupby(["stock_ticker"]):
        dfcomp[name] = df["close_price"][df.stock_ticker==name].reset_index(drop=True)
        dfcomp = dfcomp.reset_index(drop=True)
    dfcomp = dfcomp.groupby(["Date"]).mean()
    dfcomp.dropna(inplace=True)
    dfcomp = dfcomp.reset_index(drop=True)
    
    # Find correlation
    retscomp = dfcomp.pct_change()
    corr = retscomp.corr()
    return corr

# Plot correlation in heatmap
def plot_correlation(corr):    
    # Plot correlation in the form of heatmap
    plt.figure(figsize = (10, 7))
    plt.imshow(corr, cmap='hot', interpolation='none', aspect='auto')
    plt.colorbar()
    plt.xticks(range(len(corr)), corr.columns)
    plt.yticks(range(len(corr)), corr.columns)
    plt.title("Correlation between the competitor stocks")
    plt.savefig('/home/ubuntu/CS623StockAnalytics/static/images/charts/correlation.png', format="png")

# ##### From the Heatmap, we can find great correlations among the competing stocks. However, this might not show causality, and could just show the trend in the technology industry rather than show how competing stocks affect each other.
