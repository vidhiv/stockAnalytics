# IMPORTS for Stock Analytics
import numpy as np
import pandas as pd
import sklearn
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import style
from datetime import datetime
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import PolynomialFeatures, scale, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import datetime
import math

# STOCK PREDICTION FUNCTIONS

# Prepare the dataframe using the appropriate features
def prepare_dataframe(df, st):
    # select data for a stock
    dfst = df[df["stock_ticker"]==st].reset_index(drop=True)
    
    # make timestamp column as index
    dfst.set_index('stock_time', inplace=True)
    
    # create a new dataframe for our model
    dfreg = dfst.loc[:,["close_price","volume"]]
    dfreg["high_low_percentage"] = (dfst["high_price"] - dfst["low_price"]) / dfst["close_price"] * 100.0
    dfreg["percentage_change"] = (dfst["close_price"] - dfst["open_price"]) / dfst["open_price"] * 100.0
    
    # Drop missing values
    dfreg.dropna(inplace=True)
    
    return dfreg

# Add forecast stock price column to the prepared dataframe
def add_forecast_column(dfreg):
    # Separating next four weeks data to forecast
    forecast_out = 20 #int(math.ceil(0.01 * len(dfreg)))
    
    # Separating the label - close_price column for forecasting (prediction)
    forecast_col = 'close_price'
    dfreg['label'] = dfreg[forecast_col].shift(-forecast_out)
    
    return dfreg, forecast_out

# Prepare date into features and label and separate the forecast data
def prepare_data(dfreg, forecast_out):
    X = np.array(dfreg.drop(['label'], 1))
    
    # Scaling X for same distribution in regression model
    X = scale(X)
    
    # To forecast the stock prices for 1 percent data at the end of our dataset, we split it from the dataset
    X = X[:-forecast_out]
    X_forecast = X[-forecast_out:]
    
    # Labels for the remaining 99 percent data
    y = np.array(dfreg['label'])
    y = y[:-forecast_out]
    
    return X, y, X_forecast

# Split data into training and testing set
def split_train_test_data(X, y):
    return train_test_split(X, y, test_size=0.33, random_state=42)

# Calculate confidence score of given model
def confidence_score(model, X_test, y_test):
    return model.score(X_test, y_test)
    
# Linear regression
def model_linear_regression(X_train, y_train, X_test, y_test):
    model = LinearRegression(n_jobs=-1)
    model.fit(X_train, y_train)
    cnfscore = confidence_score(model, X_test, y_test)
    return model, cnfscore

# Quadratic regression
def model_qudratic_regression(X_train, y_train, X_test, y_test, num_features):
    model = make_pipeline(PolynomialFeatures(num_features), Ridge())
    model.fit(X_train, y_train)
    cnfscore = confidence_score(model, X_test, y_test)
    return model, cnfscore
    
# K-Nearest Neighbor (KNN) Regression
def model_knn_regression(X_train, y_train, X_test, y_test, num_neighbors):
    # KNN uses feature similarity to predict values of data points. 
    # This ensures that the new point assigned is similar to the points in the data set. 
    # To find out similarity, we will extract the points to release the minimum distance.
    model = KNeighborsRegressor(n_neighbors=num_neighbors)
    model.fit(X_train, y_train)
    cnfscore = confidence_score(model, X_test, y_test)
    return model, cnfscore

# Predict stock price from the model
def predict(X, model):
    return model.predict(X)

# Helper function to get future dates
def get_next_date(next_unix):
    next_unix += datetime.timedelta(days=1)
    if next_unix.weekday()==5:
        next_unix += datetime.timedelta(days=2)
    elif next_unix.weekday()==6:
        next_unix += datetime.timedelta(days=1)
    return next_unix

# Add forecast to dataframe
def get_predictions(dfreg, forecast_set):
    dfreg['forecast'] = np.nan
    last_date = dfreg.iloc[-1].name
    next_date = last_date
    next_unix = get_next_date(next_date)
    for i in forecast_set:
        next_date = next_unix
        next_unix = get_next_date(next_date)
        dfreg.loc[next_date] = [np.nan for _ in range(len(dfreg.columns)-1)]+[i]
    return dfreg

# Plot the forecasted prices
def plot_forecast(dfreg, st):
    plt.figure(figsize=(10,10))
    dfreg['close_price'].tail(150).plot()
    dfreg['forecast'].tail(150).plot()
    plt.legend(loc=4)
    plt.title("Forecasting stock "+st)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.savefig("/home/ubuntu/CS623StockAnalytics/static/images/charts/"+st.lower()+".png", format="png")
    plt.show()
    plt.close()
