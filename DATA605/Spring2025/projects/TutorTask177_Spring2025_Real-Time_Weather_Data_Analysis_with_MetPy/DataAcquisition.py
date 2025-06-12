# DataAcquisition.py

import requests

def fetch_weather_data(api_key, city):
    """Fetch real-time weather data from OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_data = {
            "city": data["name"],
            "temperature_C": data["main"]["temp"],
            "humidity_percent": data["main"]["humidity"],
            "wind_speed_mps": data["wind"]["speed"],
            "pressure_hPa": data["main"]["pressure"],
            "datetime": data["dt"]
        }
        return weather_data
    else:
        print(f"Failed to retrieve data. Error code: {response.status_code}")
        return None
