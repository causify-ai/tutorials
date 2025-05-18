import csv
import os
import datetime
from DataAcquisition import fetch_weather_data
from DataProcessing import process_weather_data

def automate_data_fetching_and_processing(api_key, city, csv_file="weather_log.csv"):
    raw_data = fetch_weather_data(api_key, city)
    if not raw_data:
        return None

    processed = process_weather_data(raw_data)

    # Convert UNIX timestamp to readable datetime
    dt_str = datetime.datetime.fromtimestamp(processed["datetime"]).strftime("%Y-%m-%d %H:%M:%S")

    # Write header if file doesn't exist
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "datetime", "city", "temperature_C", "dew_point_C", 
                "humidity_percent", "wind_speed_mps", "pressure_hPa", "wind_chill_C", "lat", "lon"
            ])
        writer.writerow([
            dt_str, processed["city"], processed["temperature_C"], processed["dew_point_C"],
            processed["humidity_percent"], processed["wind_speed_mps"],
            processed["pressure_hPa"], processed["wind_chill_C"],processed["lat"], processed["lon"]
        ])
    
    print(f"Logged weather data at {dt_str}")
    return processed
