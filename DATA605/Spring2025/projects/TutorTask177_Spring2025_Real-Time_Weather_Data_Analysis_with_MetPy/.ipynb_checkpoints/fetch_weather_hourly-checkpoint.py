import requests
import pandas as pd
from datetime import datetime
import time
import os

API_KEY = "e3019527d4076cd2e0e5ae7088c3c9c7"
CITIES = ["New York", "London", "Tokyo", "Delhi"]
CSV_FILE = "weather_log.csv"

def fetch_weather_data(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch {city}: {response.status_code}")
        return None

def process_weather_data(data):
    if not data:
        return None
    temp_c = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    pressure = data["main"]["pressure"]
    timestamp = datetime.utcfromtimestamp(data["dt"])
    dew_point = temp_c - ((100 - humidity) / 5.0)
    wind_speed_kph = wind_speed * 3.6
    if temp_c <= 10 and wind_speed_kph > 4.8:
        wind_chill = 13.12 + 0.6215 * temp_c - 11.37 * wind_speed_kph**0.16 + 0.3965 * temp_c * wind_speed_kph**0.16
    else:
        wind_chill = temp_c
    return {
        "city": data["name"],
        "datetime": timestamp,
        "temperature_C": temp_c,
        "humidity_percent": humidity,
        "wind_speed_mps": wind_speed,
        "pressure_hPa": pressure,
        "dew_point_C": round(dew_point, 1),
        "wind_chill_C": round(wind_chill, 1),
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"]
    }

def append_to_csv(record, filename=CSV_FILE):
    df_new = pd.DataFrame([record])
    if os.path.exists(filename):
        df = pd.read_csv(filename, parse_dates=["datetime"])
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(filename, index=False)

def main():
    while True:
        print(f"Fetching data at {datetime.utcnow()} UTC...")
        for city in CITIES:
            data = fetch_weather_data(API_KEY, city)
            processed = process_weather_data(data)
            if processed:
                append_to_csv(processed)
                print(f"Saved data for {city} at {processed['datetime']}")
        print("Waiting 1 hour for next fetch...")
        time.sleep(3600)  # Sleep for 1 hour

if __name__ == "__main__":
    main()
