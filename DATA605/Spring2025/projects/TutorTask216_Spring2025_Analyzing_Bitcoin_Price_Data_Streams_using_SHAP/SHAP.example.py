# SHAP.example.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Import custom utilities
from ingestion.fetch_data import load_realtime_btc_data
from preprocessing.eda_hourly_data import (
    plot_price_over_time, plot_volume_over_time, plot_distribution
)
from preprocessing.stationarity_checks import plot_rolling_stats, run_adf_test
from shap_utils.shap_analysis import SHAPAnalyzer

import warnings
warnings.filterwarnings("ignore")

def engineer_features(df):
    df = df.copy()
    df = df.sort_values("timestamp")

    # Lag features
    df["price_lag_1"] = df["price"].shift(1)
    df["price_lag_3"] = df["price"].shift(3)
    df["volume_lag_1"] = df["volume"].shift(1)

    # Rolling stats
    df["price_ma_6"] = df["price"].rolling(window=6).mean()
    df["price_ma_24"] = df["price"].rolling(window=24).mean()
    df["price_std_6"] = df["price"].rolling(window=6).std()
    df["price_std_24"] = df["price"].rolling(window=24).std()
    df["volume_std_6"] = df["volume"].rolling(window=6).std()

    # Target
    df["target_price"] = df["price"].shift(-1)

    # Drop rows with NaNs from rolling and shifting
    df = df.dropna()
    return df

def evaluate_model(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print(f"Model Evaluation:\nMAE: {mae:.2f}\nRMSE: {rmse:.2f}\nR²: {r2:.4f}")
    return mae, rmse, r2

def main():
    print("Loading real-time Bitcoin data...")
    df = load_realtime_btc_data(days=90)

    print("Running EDA...")
    plot_price_over_time(df)
    plot_volume_over_time(df)
    plot_distribution(df, column="price")

    print("Checking stationarity...")
    plot_rolling_stats(df["price"], window=24, title="Rolling Stats for Price")
    run_adf_test(df["price"])

    print("Engineering features...")
    df_feat = engineer_features(df)
    feature_cols = [col for col in df_feat.columns if col not in ["timestamp", "target_price"]]
    X = df_feat[feature_cols]
    y = df_feat["target_price"]

    print("Training model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    model = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    evaluate_model(y_test, y_pred)

    print("Running SHAP explanations...")
    shap_engine = SHAPAnalyzer(model)
    shap_engine.compute_shap_values(X_test)

    # Global explanation
    shap_engine.plot_global_importance()
    shap_engine.plot_summary_beeswarm(X_test)

    # Local explanation
    shap_engine.plot_local_waterfall(index=0)
    shap_engine.plot_dependence("price_lag_1", X_test)
    shap_engine.plot_decision(X_test.iloc[:50])

if __name__ == "__main__":
    main()
