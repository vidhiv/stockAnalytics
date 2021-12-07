import get_data as gd
import stock_predictions as sp
import correlation as cl

# MAIN FUNCTION
def main():
    stocks = ["AMZN", "AAPL", "TSLA", "MSFT", "SQ", "GOOGL", "SHOP", "NVDA", "SE", "ABNB"]
    data = gd.download_data(stocks, "10y", "1d")
    df = gd.preprocess_data(data, stocks)
    
    # Plot Correlation
    corr = cl.get_correlation(df)
    cl.plot_correlation(corr)
    
    # Predict Stock Prices
    for st in stocks:
        dfreg = sp.prepare_dataframe(df, st)
        dfreg, forecast = sp.add_forecast_column(dfreg)
        X, y, X_forecast = sp.prepare_data(dfreg, forecast)

        # Split arrays into random train and test subsets
        X_train, X_test, y_train, y_test = sp.split_train_test_data(X, y)

        # Run 4 models on the data
        # Linear regression
        clfreg, confidencereg = sp.model_linear_regression(X_train, y_train, X_test, y_test)
        # Quadratic Regression 2
        clfpoly2, confidencepoly2 = sp.model_qudratic_regression(X_train, y_train, X_test, y_test, 2)
        # Quadratic Regression 3
        clfpoly3, confidencepoly3 = sp.model_qudratic_regression(X_train, y_train, X_test, y_test, 3)
        # KNN Regression
        clfknn, confidenceknn = sp.model_knn_regression(X_train, y_train, X_test, y_test, 2)

        # Select best model for forecasting
        models = {clfreg: confidencereg, clfpoly2: confidencepoly2, clfpoly3: confidencepoly3, clfknn: confidenceknn}
        selected_model = max(models, key=models.get)

        # Predict stock prices
        forecast_set = sp.predict(X_forecast, selected_model)
        
        # Add forecasted prices to dataframe
        dfreg = sp.get_predictions(dfreg, forecast_set)
        
        # Save predictions to csv 
        dfpred = dfreg[-len(forecast_set):]
        dfpred = dfpred.dropna(axis=1)
        dfpred = dfpred.reset_index()
        dfpred["forecast"] = dfpred["forecast"].round(4)
        dfpred.columns = ["Date", "Forecasted Price"]
        dfpred[:5].to_csv("/home/ubuntu/CS623StockAnalytics/static/predictions/"+st.lower()+".csv", sep=',')
        
        # Plot forecasted prices
        sp.plot_forecast(dfreg, st)

if __name__ == "__main__":
    main()
