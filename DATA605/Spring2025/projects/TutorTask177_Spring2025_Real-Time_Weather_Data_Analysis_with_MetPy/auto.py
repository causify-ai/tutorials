# auto.py

import time
from datetime import datetime
from DataAcquisition import fetch_weather_data
from DataProcessing import process_weather_data
from Viz import generate_visualizations

API_KEY = "your_openweathermap_api_key"  # Replace with your actual API key
CITY = "London"  # Default city
FETCH_INTERVAL = 3600  # Time interval for fetching data (in seconds, 3600s = 1 hour)

def automate_data_fetching_and_processing():
    """Automate data fetching, processing, and visualization generation every hour."""
    while True:
        print(f"Fetching data at {datetime.now()}")
        
        # Step 1: Fetch weather data
        weather_data = fetch_weather_data(API_KEY, CITY)
        
        if weather_data:
            # Step 2: Process the weather data
            print("Processing data...")
            processed_data = process_weather_data(weather_data)

            # Step 3: Generate visualizations
            print("Generating visualizations...")
            generate_visualizations()
        
        # Wait for the next cycle
        print(f"Waiting for {FETCH_INTERVAL / 60} minutes...")
        time.sleep(FETCH_INTERVAL)

if __name__ == "__main__":
    automate_data_fetching_and_processing()
