# Utility functions for Bitcoin Transaction Anomaly Detection

import subprocess
from pathlib import Path

# Set the directory of the current file (not duplicated)
SCRIPTS_DIR = Path(__file__).parent.resolve()

def run_extract():
    print("[RUN] Running extract_and_upload.py...")
    script = SCRIPTS_DIR / "extract_and_upload.py"
    subprocess.run(["python3", str(script)], check=True)

def run_preprocess():
    print("[RUN] Running preprocess_with_spark.py...")
    script = SCRIPTS_DIR / "preprocess_with_spark.py"
    subprocess.run(["spark-submit", "--packages", "org.apache.hadoop:hadoop-aws:3.3.2", str(script)], check=True)

def run_anomaly_detection():
    print("[RUN] Running track_anomalies.py...")
    script = SCRIPTS_DIR / "track_anomalies.py"
    subprocess.run(["python3", str(script)], check=True)

def run_explanation():
    print("[RUN] Running anomaly_explainer.py...")
    script = SCRIPTS_DIR / "anomaly_explainer.py"
    subprocess.run(["python3", str(script)], check=True)

def run_coordinated_attack_check():
    print("[RUN] Running detect_coordinated_attacks.py...")
    script = SCRIPTS_DIR / "detect_coordinated_attacks.py"
    subprocess.run(["python3", str(script)], check=True)

def run_alert():
    print("[RUN] Running send_alert.py...")
    script = SCRIPTS_DIR / "send_alert.py"
    subprocess.run(["python3", str(script)], check=True)

def run_forecast():
    print("[RUN] Running forecast_with_prophet.py...")
    script = SCRIPTS_DIR / "forecast_with_prophet.py"
    subprocess.run(["python3", str(script)], check=True)