from QlikAnalysis_utils import (
    load_bitcoin_data,
    add_time_series_features,
    forecast_bitcoin,
    save_dataframe
)

BITCOIN_CSV = "bitcoin_realtime.csv"
ANALYTICS_CSV = "bitcoin_analytics.csv"
FORECAST_CSV = "bitcoin_forecast.csv"

def main():
    df = load_bitcoin_data(BITCOIN_CSV)
    df = add_time_series_features(df, ma_window=6, vol_window=12)
    save_dataframe(df, ANALYTICS_CSV)
    forecast_df = forecast_bitcoin(df, periods=24, freq='h')
    if forecast_df is not None:
        save_dataframe(forecast_df, FORECAST_CSV)

if __name__ == "__main__":
    main()
