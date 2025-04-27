import cudf

def add_to_dataframe(gdf, timestamp, price):
    new_row = cudf.DataFrame({"timestamp": [timestamp], "price": [price]})
    return cudf.concat([gdf, new_row], ignore_index=True)

def compute_moving_averages(gdf, window=5):
    gdf["SMA"] = gdf["price"].rolling(window=window).mean()
    return gdf

def compute_volatility(gdf, window=5):
    gdf["Volatility"] = gdf["price"].rolling(window=window).std()
    return gdf

def compute_rate_of_change(gdf, periods=1):
    gdf["ROC"] = gdf["price"].pct_change(periods=periods) * 100
    return gdf

def save_to_csv(gdf, filename="bitcoin_prices.csv"):
    gdf.to_pandas().to_csv(filename, index=False)