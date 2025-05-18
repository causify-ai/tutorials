#!/usr/bin/env python3
import subprocess
import threading
import time
import os
import signal
import sys
from datetime import datetime

api_process = None
dashboard_process = None

def signal_handler(sig, frame):
    print("\nShutting down services...")
    if api_process:
        api_process.terminate()
    if dashboard_process:
        dashboard_process.terminate()
    sys.exit(0)

def run_api_server():
    global api_process
    print("Starting API server on port 5001...")
    try:
        api_process = subprocess.Popen(
            ["python", "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        while api_process.poll() is None:
            line = api_process.stdout.readline()
            if line:
                print(f"[API] {line.strip()}")
            line = api_process.stderr.readline()
            if line:
                print(f"[API ERROR] {line.strip()}")
    except Exception as e:
        print(f"API server error: {str(e)}")

def run_dashboard():
    global dashboard_process
    print("Starting dashboard on port 5000...")
    try:
        dashboard_process = subprocess.Popen(
            ["python", "simple_dashboard.py", "--no-browser"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        while dashboard_process.poll() is None:
            line = dashboard_process.stdout.readline()
            if line:
                print(f"[DASHBOARD] {line.strip()}")
            line = dashboard_process.stderr.readline()
            if line:
                print(f"[DASHBOARD ERROR] {line.strip()}")
    except Exception as e:
        print(f"Dashboard error: {str(e)}")

def ensure_data_directories():
    for d in ["forecasts", "evaluation", "data", "data/bitcoin"]:
        os.makedirs(d, exist_ok=True)

def check_initial_data():
    data_path = "data/bitcoin/bitcoin_prices.csv"
    if not os.path.exists(data_path):
        print("Initial dataset not found. Fetching historical data...")
        try:
            from tf_bitcoin_utils import fetch_bitcoin_prices
            historical_data = fetch_bitcoin_prices(days=30)
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            historical_data.to_csv(data_path, index=False)
            print(f"Created historical dataset with {len(historical_data)} records")
            return True
        except Exception as e:
            print(f"Error fetching initial data: {str(e)}")
            return False
    return True

def ensure_initial_forecast():
    if not any(f.endswith((".csv", ".png")) for f in os.listdir("forecasts")):
        print("No existing forecasts found. Generating initial forecast...")
        try:
            subprocess.run(["python", "predict.py"], check=True)
            print("Initial forecast generated")
        except Exception as e:
            print(f"Error generating initial forecast: {str(e)}")

def check_model_exists():
    model_dir = "tfx_pipeline_output/bitcoin_price_pipeline/serving_model"
    if not os.path.exists(model_dir):
        print("No trained model found. Running initial pipeline...")
        try:
            subprocess.run(["python", "tf_pipeline.py"], check=True)
            print("Initial pipeline completed")
        except Exception as e:
            print(f"Error running initial pipeline: {str(e)}")

def start_daily_retraining():
    def retrain_loop():
        last_trained_day = None
        while True:
            current_day = datetime.now().date()
            if last_trained_day != current_day:
                print(f"[RETRAINER] New day detected: {current_day}. Triggering retraining...")
                try:
                    subprocess.run(["python", "realtime_update.py"], check=True)
                    print("[RETRAINER] Retraining completed.")
                    last_trained_day = current_day
                except Exception as e:
                    print(f"[RETRAINER] Error during retraining: {e}")
            else:
                print(f"[RETRAINER] Already retrained today ({current_day}). Sleeping...")
            time.sleep(3600)
    thread = threading.Thread(target=retrain_loop, daemon=True)
    thread.start()

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("="*60)
    print(" Bitcoin Price Forecasting System Deployment ")
    print("="*60)

    ensure_data_directories()
    data_ready = check_initial_data()

    if data_ready:
        check_model_exists()
        ensure_initial_forecast()

    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()

    time.sleep(3)

    print("\n" + "="*60)
    print(" Service URLs:")
    print(" Dashboard: http://localhost:5000")
    print(" API Server: http://localhost:5001")
    print("="*60 + "\n")

    start_daily_retraining()
    run_dashboard()

    if api_process and api_process.poll() is None:
        print("Shutting down API server...")
        api_process.terminate()

    print("Deployment completed")

if __name__ == "__main__":
    main()
