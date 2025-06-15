# run_pipeline.py

from bitcoin_utils import (
    configure_streaming_paths_and_schedule,
    start_file_producer,
    aggregate_hourly_daily_moving_average,
    train_and_evaluate_gbt_regressor,
    plot_actual_vs_predicted_prices
)

print("🚀 Starting full Bitcoin pipeline...")

configure_streaming_paths_and_schedule()
start_file_producer()
aggregate_hourly_daily_moving_average()
train_and_evaluate_gbt_regressor()
plot_actual_vs_predicted_prices()

print("✅ Pipeline run complete.")
