import time
import datetime
import os
import csv
# Import your existing functions (make sure they're in the same folder or properly imported)
from your_weather_module import automate_data_fetching_and_processing

def main():
    api_key = "e3019527d4076cd2e0e5ae7088c3c9c7"   # Replace with your actual API key
    city = "London"                 # Change to any city you want

    print(f"Starting data logger for {city} at {datetime.datetime.now()}")

    while True:
        print(f"Fetching data at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        processed_data = automate_data_fetching_and_processing(api_key, city)
        if processed_data is None:
            print("Failed to fetch data; will retry in 10 minutes.")
        else:
            print("Data logged successfully.")
        
        print("Sleeping for 10 minutes...\n")
        time.sleep(600)  # Wait for 600 seconds (10 minutes)

if __name__ == "__main__":
    main()
