# DataProcessing.py

from metpy.units import units
from metpy.calc import dewpoint_from_relative_humidity
import pandas as pd

def process_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize weather data.

    Parameters:
        raw_data (pd.DataFrame): The raw data with weather metrics.

    Returns:
        pd.DataFrame: Cleaned and processed weather data.
    """
    if raw_data is None or raw_data.empty:
        return pd.DataFrame()  # Return empty DataFrame safely

    # Ensure datetime is in datetime format
    raw_data["datetime"] = pd.to_datetime(raw_data["datetime"])

    # Sort by datetime (optional but useful)
    raw_data = raw_data.sort_values(by="datetime")

    # Fill or drop missing values (customize as needed)
    raw_data = raw_data.dropna()

    return raw_data


def calculate_dewpoint(temperature_celsius: float, relative_humidity_percent: float) -> float:
    """
    Calculate the dew point from temperature and relative humidity.

    Parameters:
        temperature_celsius (float): Temperature in degrees Celsius.
        relative_humidity_percent (float): Relative humidity as a percentage (0-100).

    Returns:
        float: Dew point in degrees Celsius, rounded to one decimal place.
    """
    temperature = temperature_celsius * units.degC
    relative_humidity = (relative_humidity_percent / 100.0) * units.dimensionless
    dew_point = dewpoint_from_relative_humidity(temperature, relative_humidity)
    return round(dew_point.to('degC').magnitude, 1)

def calculate_wind_chill(temperature_celsius: float, wind_speed_mps: float) -> float:
    """
    Calculate the wind chill based on temperature and wind speed using the standard formula.

    Parameters:
        temperature_celsius (float): Temperature in degrees Celsius.
        wind_speed_mps (float): Wind speed in meters per second.

    Returns:
        float: Wind chill in degrees Celsius.
    """
    wind_speed_kph = wind_speed_mps * 3.6
    wind_chill = (
        13.12 + 0.6215 * temperature_celsius
        - 11.37 * wind_speed_kph**0.16
        + 0.3965 * temperature_celsius * wind_speed_kph**0.16
    )
    return round(wind_chill, 1)

def process_weather_data(raw_data):
    temp_c = raw_data["main"]["temp"]
    humidity = raw_data["main"]["humidity"]
    wind_speed = raw_data["wind"]["speed"]
    pressure = raw_data["main"]["pressure"]
    dew_point = calculate_dew_point(temp_c, humidity)
    wind_chill = calculate_wind_chill(temp_c, wind_speed)
    
    return {
        "city": raw_data["name"],
        "datetime": raw_data["dt"],
        "temperature_C": temp_c,
        "humidity_percent": humidity,
        "wind_speed_mps": wind_speed,
        "pressure_hPa": pressure,
        "dew_point_C": dew_point,
        "wind_chill_C": wind_chill,
        "lat": raw_data["coord"]["lat"],   # ADD THIS
        "lon": raw_data["coord"]["lon"]    # ADD THIS
    }
