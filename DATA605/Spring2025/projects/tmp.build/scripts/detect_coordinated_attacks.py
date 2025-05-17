# scripts/detect_coordinated_attacks.py
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from send_alert import send_slack_alert
import warnings
warnings.filterwarnings("ignore")

load_dotenv()
INPUT_CSV = "../data/processed/cleaned_transactions.csv"
OUTPUT_CSV = "../report/coordinated_attacks.csv"

def detect_coordinated_attacks(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["minute"] = df["timestamp"].dt.floor("min")

    df["fan_in_flag"] = df["input_count"] >= 10
    df["fan_out_flag"] = df["output_count"] >= 10
    df["coord_flag"] = df["fan_in_flag"] | df["fan_out_flag"]

    grouped = df[df["coord_flag"]].groupby("minute").agg(
        total_flagged=("coord_flag", "sum"),
        avg_input_count=("input_count", "mean"),
        avg_output_count=("output_count", "mean"),
        sample_tx_hash=("tx_hash", "first")
    ).reset_index()

    candidates = grouped[grouped["total_flagged"] >= 2]
    return candidates

def alert_for_coordination(df):
    if df.empty:
        print("[INFO] No coordinated attack candidates found.")
        return

    for _, row in df.iterrows():
        msg = (
            ":collision: *Possible Coordinated Attack Detected!*\n"
            f"• Time: `{row['minute']}`\n"
            f"• Tx Count: `{row['total_flagged']}`\n"
            f"• Avg Inputs: `{round(row['avg_input_count'], 1)}` | Avg Outputs: `{round(row['avg_output_count'], 1)}`\n"
            f"• Sample Tx: `{row['sample_tx_hash'][:16]}...`"
        )
        send_slack_alert(msg)

def main():
    print("[INFO] Detecting coordinated attacks...")

    if not os.path.exists(INPUT_CSV):
        print(f"[ERROR] File not found: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)
    result = detect_coordinated_attacks(df)

    os.makedirs("../report", exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False)
    print(f"[INFO] Coordinated attack candidates saved to: {OUTPUT_CSV}")

    alert_for_coordination(result)

if __name__ == "__main__":
    main()