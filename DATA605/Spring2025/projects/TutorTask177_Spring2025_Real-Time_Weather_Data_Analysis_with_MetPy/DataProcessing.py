# DataProcessing.py

from metpy.units import units
from metpy.calc import dewpoint_from_relative_humidity

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

def process_weather_data(weather_data: dict) -> dict:
    """
    Process the weather data to compute additional parameters like dew point and wind chill.

    Parameters:
        weather_data (dict): Dictionary containing keys like 'temperature_C', 'humidity_percent',
                             'wind_speed_mps', 'pressure_hPa', etc.

    Returns:
        dict: Augmented weather data with additional calculated parameters.
    """
    temperature_C = weather_data.get("temperature_C")
    humidity_percent = weather_data.get("humidity_percent")
    wind_speed_mps = weather_data.get("wind_speed_mps")
    pressure_hPa = weather_data.get("pressure_hPa")

    return {
        "city": weather_data.get("city"),
        "datetime": weather_data.get("datetime"),
        "temperature_C": temperature_C,
        "humidity_percent": humidity_percent,
        "wind_speed_mps": wind_speed_mps,
        "pressure_hPa": pressure_hPa,
        "dew_point_C": calculate_dewpoint(temperature_C, humidity_percent),
        "wind_chill_C": calculate_wind_chill(temperature_C, wind_speed_mps)
    }
