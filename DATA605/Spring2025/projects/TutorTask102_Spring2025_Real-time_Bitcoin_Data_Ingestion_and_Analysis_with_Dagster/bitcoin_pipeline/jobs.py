from dagster import job
from bitcoin_pipeline.ops import (
    fetch_price_op,
    process_price_op,
    save_csv_op,
    fetch_historical_op,
    moving_average_op,
    detect_trend_op,
    detect_anomalies_op,
    forecast_op
)

@job
def bitcoin_analysis_job():
    live_price = fetch_price_op()
    df_live = process_price_op(live_price)
    save_csv_op(df_live)

    historical_df = fetch_historical_op()
    ma_df = moving_average_op(historical_df)
    detect_trend_op(ma_df)
    detect_anomalies_op(ma_df)
    forecast_op(ma_df)
