import requests
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
from dowhy import CausalModel 



DATA_PATH = "data/raw_bitcoin.csv"


    
    
def fetch_historical_prices(days=30):
    
   
    print(f"[INFO] Fetching last {days} days of Bitcoin data...")
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.text}")

    prices = response.json()["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/raw_bitcoin.csv", index=False)
    print(f"[INFO] Saved historical data to data/raw_bitcoin.csv")


def fetch_live_price():
   
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch live price: {response.text}")

    price = response.json()["bitcoin"]["usd"]
    timestamp = datetime.utcnow()
    return {"timestamp": timestamp, "price": price}


def append_live_price_to_csv():
    
    live_data = fetch_live_price()
    print(f"[INFO] Fetched live price: {live_data}")

    # Load existing data
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    else:
        df = pd.DataFrame(columns=["timestamp", "price"])

    # Append if new
    if live_data["timestamp"] not in df["timestamp"].values:
        df = pd.concat([df, pd.DataFrame([live_data])], ignore_index=True)
        df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")
        df.to_csv(DATA_PATH, index=False)
        print(f"[INFO] Appended live price to {DATA_PATH}")
    else:
        print(f"[INFO] Live price with timestamp {live_data['timestamp']} already exists.")


def load_bitcoin_data():
   
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, parse_dates=["timestamp"]).sort_values("timestamp")
    else:
        raise FileNotFoundError(f"{DATA_PATH} not found. Please run fetch_historical_prices() first.")

       
    from dowhy import CausalModel
    
def inject_multiple_dummy_events(df, event_times):
    if "timestamp" not in df.columns:
        raise ValueError("DataFrame must include a 'timestamp' column.")

    df = df.copy()
    df["event"] = df["timestamp"].apply(lambda t: 1 if pd.to_datetime(t) in [pd.to_datetime(e) for e in event_times] else 0)
    print(f"[INFO] Injected {len(event_times)} dummy event(s) at: {event_times}")
    return df

def run_causal_analysis(df):
    """
    Perform causal inference using DoWhy without graph string.
    Uses common causes instead of DOT graph to bypass pygraphviz.
    """
    if "price" not in df.columns or "event" not in df.columns:
        raise ValueError("DataFrame must include 'price' and 'event' columns.")

    # Add rolling std as confounder if not present
    if "confounder" not in df.columns:
        df["confounder"] = df["price"].shift(1).fillna(method="bfill")
        print("[INFO] Using lagged price as confounder.")

    print("[INFO] Defining CausalModel (no graph)...")
    model = CausalModel(
        data=df,
        treatment="event",
        outcome="price",
        common_causes=["confounder"]
    )

    print("[INFO] Identifying estimand...")
    identified_estimand = model.identify_effect()

    print("[INFO] Estimating effect using linear regression...")
    estimate = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.linear_regression"
    )

    print(f"\n[RESULT] Estimated Treatment Effect: {estimate.value}")

    print("\n[INFO] Running placebo refutation test...")
    refute1 = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="placebo_treatment_refuter"
    )

    print("[INFO] Running data subset refutation test...")
    refute2 = model.refute_estimate(
        identified_estimand,
        estimate,
        method_name="data_subset_refuter"
    )

    print("\n[INFO] Refutation Test 1 Result (Placebo):", refute1)
    print("[INFO] Refutation Test 2 Result (Subset):", refute2)

    return estimate, refute1, refute2

def run_causal_with_estimators(df):
    """
    Runs DoWhy causal estimation using multiple supported estimators.
    Returns a list of estimator names and their estimated effects.
    """
    if "price" not in df.columns or "event" not in df.columns:
        raise ValueError("DataFrame must include 'price' and 'event' columns.")
    
    if "confounder" not in df.columns:
        df["confounder"] = df["price"].shift(1).fillna(method="bfill")
        print("[INFO] Added lagged price as default confounder.")

    estimators = [
        "backdoor.linear_regression",
        "backdoor.propensity_score_matching"
    ]

    model = CausalModel(
        data=df,
        treatment="event",
        outcome="price",
        common_causes=["confounder"]
    )

    identified_estimand = model.identify_effect()

    results = []
    for method in estimators:
        try:
            estimate = model.estimate_effect(identified_estimand, method_name=method)
            results.append({
                "estimator": method,
                "effect": estimate.value
            })
        except Exception as e:
            print(f"[ERROR] {method} failed: {e}")
            results.append({
                "estimator": method,
                "effect": None
            })
    
    return results



def compare_confounder_strategies(df, event_time):
    """
    Compares treatment effects using different confounder strategies:
    - Lagged Price
    - Rolling Volatility (Std Dev)
    - Price Momentum (Pct Change)
    
    Returns a list of results with confounder type and estimated effect.
    """
    confounder_strategies = {
        "lagged_price": lambda d: d["price"].shift(1).fillna(method="bfill"),
        "rolling_volatility": lambda d: d["price"].rolling(window=5).std().fillna(0),
        "momentum": lambda d: d["price"].pct_change().fillna(0)
    }

    results = []

    for name, func in confounder_strategies.items():
        temp_df = df.copy()
        temp_df["event"] = 0
        temp_df.loc[temp_df["timestamp"] == event_time, "event"] = 1
        temp_df["confounder"] = func(temp_df)

        try:
            estimate, _, _ = run_causal_analysis(temp_df)
            results.append({
                "confounder": name,
                "estimated_effect": estimate.value
            })
        except Exception as e:
            print(f"[ERROR] {name} failed: {e}")
            results.append({
                "confounder": name,
                "estimated_effect": None
            })

    return results




import matplotlib.pyplot as plt

def plot_price_series(df):
   
    if "timestamp" not in df.columns or "price" not in df.columns:
        raise ValueError("DataFrame must have 'timestamp' and 'price' columns.")

    plt.figure(figsize=(12, 5))
    plt.plot(df["timestamp"], df["price"], label="Bitcoin Price", color='blue')

    if "event" in df.columns and df["event"].sum() > 0:
        event_times = df[df["event"] == 1]["timestamp"]
        for i, ev in enumerate(event_times):
            plt.axvline(x=ev, color='red', linestyle='--', alpha=0.7,
                        label="Event" if i == 0 else "")

    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.title("Bitcoin Price Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    
def plot_event_impact(df):
    """
    Plots Bitcoin price with a red vertical line marking the event timestamp.
    """
    if "event" not in df.columns or df["event"].sum() == 0:
        print("[WARN] No event column found or no event marked.")
        return

    event_time = df[df["event"] == 1]["timestamp"].values[0]

    plt.figure(figsize=(12, 5))
    plt.plot(df["timestamp"], df["price"], label="Bitcoin Price", color="blue")
    plt.axvline(x=event_time, color="red", linestyle="--", label="Simulated Event")

    plt.title("Bitcoin Price with Simulated Event")
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
def plot_multiple_events(df):
    """
    Plots all event timestamps as vertical red lines on the price timeline.
    """
    if "event" not in df.columns or df["event"].sum() == 0:
        print("[WARN] No events found in 'event' column.")
        return

    plt.figure(figsize=(12, 5))
    plt.plot(df["timestamp"], df["price"], label="Bitcoin Price", color='blue')

    event_times = df[df["event"] == 1]["timestamp"]
    for ev in event_times:
        plt.axvline(x=ev, color='red', linestyle='--', alpha=0.7)

    plt.title("Bitcoin Price with Multiple Events")
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    
def compute_lagged_confounder(df):
    """
    Uses previous timestamp's price as confounder (lagged price).
    """
    df = df.copy()
    df["confounder"] = df["price"].shift(1).fillna(method="bfill")
    print("[INFO] Confounder (lagged price) added.")
    return df
def run_full_event_analysis(df, event_times):
    """
    Runs full causal analysis for each event timestamp:
    - Injects event
    - Computes lagged confounder
    - Runs DoWhy estimation and refutation

    Returns:
    - A pandas DataFrame with: event_time, estimated effect, placebo p-value, subset p-value
    """
    results = []

    for i, event_time in enumerate(event_times):
        temp_df = df.copy()
        temp_df["event"] = 0
        temp_df.loc[temp_df["timestamp"] == event_time, "event"] = 1

        temp_df = compute_lagged_confounder(temp_df)

        try:
            estimate, ref1, ref2 = run_causal_analysis(temp_df)
            results.append({
                "Event #": i + 1,
                "Event Time": event_time,
                "Estimated Effect": estimate.value,
                "Placebo P-Value": ref1.refutation_result.get("p_value", None),
                "Subset P-Value": ref2.refutation_result.get("p_value", None)
            })
        except Exception as e:
            print(f"[ERROR] Failed at event {event_time}: {e}")
            results.append({
                "Event #": i + 1,
                "Event Time": event_time,
                "Estimated Effect": None,
                "Placebo P-Value": None,
                "Subset P-Value": None
            })

    return pd.DataFrame(results)





   






