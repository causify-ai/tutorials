# template.example.py

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from statsmodels.tsa.seasonal import seasonal_decompose
from template import API

def main():
    # Fetch Bitcoin transaction count
    df = API.fetch_bitcoin_metric("transaction_count")

    # Clean & prepare
    df["value"].interpolate(method="linear", inplace=True)
    df["rolling_mean"] = df["value"].rolling(window=10, min_periods=1).mean()
    df["rolling_std"] = df["value"].rolling(window=10, min_periods=1).std()
    df["z_score"] = (df["value"] - df["rolling_mean"]) / df["rolling_std"]

    # Decompose
    decomposition = seasonal_decompose(df["value"], model="additive", period=10)
    df["trend"] = decomposition.trend
    df["seasonal"] = decomposition.seasonal
    df["residual"] = decomposition.resid

    # Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["value"], mode="lines", name="Value"))
    fig.add_trace(go.Scatter(x=df.index, y=df["rolling_mean"], mode="lines", name="Rolling Mean"))
    
    # Highlight anomalies
    anomalies = df[df["z_score"].abs() > 2]
    fig.add_trace(go.Scatter(x=anomalies.index, y=anomalies["value"],
                             mode="markers", name="Anomalies", marker=dict(color="red", size=8)))

    fig.update_layout(title="Bitcoin Transaction Count with Anomalies", xaxis_title="Date", yaxis_title="Count")
    fig.show()

if __name__ == "__main__":
    main()