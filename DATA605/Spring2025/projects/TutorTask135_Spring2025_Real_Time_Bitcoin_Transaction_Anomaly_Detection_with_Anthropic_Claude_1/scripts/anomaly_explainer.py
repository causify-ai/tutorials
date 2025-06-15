import os
import pandas as pd
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Load Claude API key from .env
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# File paths (adjusted to top-level project structure)
INPUT_CSV = "../data/processed/tx_agg_1min.csv"
OUTPUT_CSV = "../report/anomaly_explanations_full.csv"

def build_prompt(tx_data: dict) -> str:
    return f"""
You are a blockchain forensic analyst with expertise in Bitcoin. A financial analyst has provided the following time-window summary of transaction activity:

{tx_data}

You must write a structured report covering:

1. Is this activity statistically unusual compared to Bitcoin’s historical and network-wide norms?
2. What suspicious behavior patterns might this match? (e.g., mixers, dusting attacks, fund dispersion, congestion)
3. What plausible legitimate causes could explain this pattern?
4. Final summary: Should this activity be flagged for further investigation? Why or why not?

Do not say “data is insufficient.” Assume this data is a high-level alert signal. Use your training on known Bitcoin anomalies to interpret the risk.

Structure your answer clearly in sections. Avoid vague disclaimers.
"""

def explain(tx_data: dict) -> str:
    prompt = build_prompt(tx_data)
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    # Handle both list and string responses
    if isinstance(response.content, list) and hasattr(response.content[0], 'text'):
        return response.content[0].text.strip()
    return str(response.content).strip()

def main():
    print("[INFO] Explaining Bitcoin transactions with Claude...")

    try:
        df = pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"[ERROR] Failed to read input file: {e}")
        return

    df["window_start"] = pd.to_datetime(df["window_start"])
    sample = df.sample(2) if len(df) >= 2 else df
    explanations = []

    # Load previously saved explanations
    existing_keys = set()
    if os.path.exists(OUTPUT_CSV):
        existing = pd.read_csv(OUTPUT_CSV)
        existing["window_start"] = pd.to_datetime(existing["window_start"], errors='coerce')
        existing = existing.dropna(subset=["window_start"])
        existing_keys = set(existing["window_start"].astype(str))

    for idx, row in sample.iterrows():
        ts_str = str(row["window_start"])
        if ts_str in existing_keys:
            print(f"[SKIP] Already explained transaction at {ts_str}")
            continue

        print(f"[INFO] Explaining transaction {idx}...")
        tx_data = row.to_dict()
        explanation = explain(tx_data)
        print(f"\n--- Explanation for transaction {idx} ---\n{explanation}\n")

        explanations.append({
            "tx_index": idx,
            "window_start": row["window_start"],
            "window_end": row.get("window_end", ""),
            "tx_count_1min": row.get("tx_count_1min", ""),
            "explanation": explanation
        })

    # Save output
    if explanations:
        os.makedirs("report", exist_ok=True)
        df_new = pd.DataFrame(explanations)
        if os.path.exists(OUTPUT_CSV):
            df_new.to_csv(OUTPUT_CSV, mode="a", header=False, index=False)
        else:
            df_new.to_csv(OUTPUT_CSV, index=False)
        print(f"[INFO] All explanations saved to: {OUTPUT_CSV}")
    else:
        print("[INFO] No new explanations needed.")

if __name__ == "__main__":
    main()