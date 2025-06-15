import os
from datetime import datetime
import pyarrow.parquet as pq

from utils import (
    fetch_and_append_new_data,
    calculate_moving_average,
    detect_anomalies,
    save_to_parquet,
    create_log_entry,
    append_log_entry,
    generate_forecast_report
)

# 🔐 Import API key from config
try:
    from config import COINGECKO_API_KEY
except ImportError:
    raise ImportError("Missing COINGECKO_API_KEY in config.py")

PARQUET_PATH = "/workspace/bitcoin-pyarrow/data_ingestion/datalake/bitcoin_price_stream.parquet"
LOG_PATH = "data_ingestion/datalake/load_log.parquet"
REPORT_PATH = "data_ingestion/reports/forecast_report.html"

print("🚀 Starting container and updating from last available timestamp...")

# Track previous row count
try:
    previous_table = pq.read_table(PARQUET_PATH)
    previous_row_count = previous_table.num_rows
except Exception:
    previous_row_count = 0

# Step 1: Fetch new data
fetch_and_append_new_data(api_key=COINGECKO_API_KEY, parquet_path=PARQUET_PATH)

# Step 2: Re-load and post-process the full table
table = pq.read_table(PARQUET_PATH)
table = calculate_moving_average(table)
table = detect_anomalies(table)
save_to_parquet(table, PARQUET_PATH)

# Step 3: Log the update
new_row_count = table.num_rows - previous_row_count
print("New row Count",table.num_rows)
log_entry = create_log_entry(
    timestamp=datetime.utcnow(),
    num_rows=new_row_count,
    source="coingecko",
    status="success",
    message="Data updated and processed."
)
append_log_entry(log_entry, LOG_PATH)

# Step 4: Forecast report generation
df = table.to_pandas()
generate_forecast_report(df, output_path=REPORT_PATH)

# Step 5: Display clickable link
abs_path = os.path.abspath(REPORT_PATH)
print(f"📄 Forecast report generated. Open in browser:\nfile://{abs_path}")
