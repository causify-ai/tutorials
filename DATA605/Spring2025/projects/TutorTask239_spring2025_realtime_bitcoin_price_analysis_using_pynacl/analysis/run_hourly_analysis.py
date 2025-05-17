import time
import subprocess
import sys
from datetime import datetime

def run_analysis():
    print(f"\n[{datetime.now()}] Starting analysis...")
    try:
        result = subprocess.run(
            ["python3", "-m", "analysis.time_series_analysis"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[{datetime.now()}] ✅ Analysis completed successfully")
        else:
            print(f"[{datetime.now()}] ❌ Analysis failed with error:")
            print(result.stderr)
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error running analysis: {e}")

if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting hourly analysis service...")
    print("Make sure main.py is running to collect data!")
    
    while True:
        try:
            run_analysis()
            print(f"[{datetime.now()}] Waiting 1 hour until next analysis...")
            time.sleep(3600)  # Sleep for 3600 seconds = 1 hour
        except KeyboardInterrupt:
            print("\n[{datetime.now()}] Analysis service stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Unexpected error: {e}")
            print("Retrying in 5 minutes...")
            time.sleep(300)  # Wait 5 minutes before retrying
