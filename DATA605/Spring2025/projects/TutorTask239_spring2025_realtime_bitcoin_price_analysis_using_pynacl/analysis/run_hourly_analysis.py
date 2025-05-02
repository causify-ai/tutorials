import time
import subprocess

def run_analysis():
    print("Running analysis...")
    subprocess.call(["python3", "-m", "analysis.time_series_analysis"])
    print("Analysis complete. Waiting 1 hour...")

if __name__ == "__main__":
    while True:
        run_analysis()
        time.sleep(3600)  # Sleep for 3600 seconds = 1 hour
