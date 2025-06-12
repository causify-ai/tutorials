# scripts/track_anomalies.py
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from send_alert import send_slack_alert
import warnings
warnings.filterwarnings("ignore")

load_dotenv()
INPUT_CSV = "../data/processed/tx_count_1min.csv"
OUTPUT_CSV = "../report/ewma_anomalies.csv"
ALPHA = 0.3
Z_THRESHOLD = 2.0

def apply_ewma_anomaly_detection(df):
    df = df.copy()
    df["ewma"] = df["tx_count_1min"].ewm(alpha=ALPHA).mean()
    df["residual"] = df["tx_count_1min"] - df["ewma"]
    std_dev = df["residual"].std()
    df["z_score"] = df["residual"] / std_dev
    df["is_anomaly"] = (df["z_score"].abs() > Z_THRESHOLD).astype(int)
    return df

def alert_for_anomalies(df):
    anomalies = df[df["is_anomaly"] == 1].copy()
    if anomalies.empty:
        print("[INFO] No anomalies to alert.")
        return

    for _, row in anomalies.iterrows():
        timestamp = row["window_start"]
        count = row["tx_count_1min"]
        z = round(row["z_score"], 2)
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": " Anomaly Detected in Bitcoin Transactions",
                    "emoji": True
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Time:*\n{timestamp}"},
                    {"type": "mrkdwn", "text": f"*Tx Count:*\n{count}"},
                    {"type": "mrkdwn", "text": f"*Z-Score:*\n{z}"}
                ]
            },
            {"type": "context", "elements": [
                {"type": "mrkdwn", "text": "Flagged due to deviation from smoothed EWMA baseline"}
            ]}
        ]

        # Send it via the improved formatting
        send_slack_alert(message="Anomaly Detected!", blocks=blocks)

def main():
    print("[INFO] Running EWMA anomaly detection...")

    if not os.path.exists(INPUT_CSV):
        print(f"[ERROR] Input CSV not found at: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)
    if "window_start" not in df.columns or "tx_count_1min" not in df.columns:
        print(f"[ERROR] Required columns not found. Columns present: {df.columns.tolist()}")
        return

    df["window_start"] = pd.to_datetime(df["window_start"])
    df = df.sort_values("window_start")
    df = apply_ewma_anomaly_detection(df)

    os.makedirs("../report", exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[SUCCESS] EWMA tracking completed. Saved to: {OUTPUT_CSV}")

    alert_for_anomalies(df)

if __name__ == "__main__":
    main()