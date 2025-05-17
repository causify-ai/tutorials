#!/usr/bin/env python3
import os
import json
import requests
import pandas as pd

# ——— Configuration ———
# Set to True to print the payload instead of actually pushing
DRY_RUN = False

# Your Power BI push URL (streaming dataset)
PUSH_URL = (
    "https://api.powerbi.com/beta/ee2d6d72-9535-4242-a077-acf185782f9b"
    "/datasets/afbad650-0150-4703-bbb9-e046dec7b061/rows"
    "?experience=power-bi&key=YOUR_KEY_HERE"
)

# CSV produced by your forecasting notebook
FORECAST_CSV = "forecast_prophet.csv"

# ——— Functions ———
def load_forecast(csv_path: str) -> pd.DataFrame:
    """
    Load the Prophet forecast output. Expect columns:
      - ds (datetime string)
      - yhat (forecasted price)
      - moving_avg_price
      - volatility_15m
    """
    df = pd.read_csv(csv_path)
    # Ensure numeric types
    for col in ["yhat", "moving_avg_price", "volatility_15m"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def build_rows(df: pd.DataFrame) -> list[dict]:
    """
    Transform each row into the JSON shape Power BI expects.
    """
    rows = []
    for _, row in df.iterrows():
        rows.append({
            "timestamp": row["ds"],                     # ISO 8601 string
            "price_usd": float(row["yhat"]),
            "moving_avg_price": float(row["moving_avg_price"]),
            "volatility_15m": float(row["volatility_15m"])
        })
    return rows

def push_to_powerbi(rows: list[dict]) -> None:
    """
    Send the batched rows to Power BI.
    """
    payload = {"rows": rows}
    if DRY_RUN:
        print("DRY_RUN payload:")
        print(json.dumps(payload, indent=2))
    else:
        resp = requests.post(PUSH_URL, json=payload)
        resp.raise_for_status()
        print(f"Pushed {len(rows)} rows to Power BI.")

# ——— Main ———
if __name__ == "__main__":
    if not os.path.exists(FORECAST_CSV):
        raise FileNotFoundError(f"Forecast CSV not found: {FORECAST_CSV}")

    df = load_forecast(FORECAST_CSV)
    rows = build_rows(df)
    push_to_powerbi(rows)
