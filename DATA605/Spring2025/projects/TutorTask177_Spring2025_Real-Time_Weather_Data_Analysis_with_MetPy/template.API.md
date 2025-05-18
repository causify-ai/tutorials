# Real-Time Weather Data Analysis API Documentation

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Core Components](#core-components)
  * [Data Acquisition](#data-acquisition)
  * [MetPy Processing](#metpy-processing)
  * [Visualization](#visualization)
  * [Data Storage](#data-storage)
- [API Reference](#api-reference)
  * [Weather Data Retrieval](#weather-data-retrieval)
  * [Meteorological Calculations](#meteorological-calculations)
  * [Visualization Tools](#visualization-tools)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

## Overview

The Real-Time Weather Data Analysis API provides a comprehensive toolset for retrieving, analyzing, and visualizing meteorological data using MetPy. It enables seamless access to real-time weather information, performs scientific calculations on atmospheric parameters, and generates insightful visualizations for weather analysis and forecasting.

## Installation

```bash
pip install metpy numpy pandas matplotlib requests streamlit python-dotenv
```

## Core Components

### Data Acquisition

The API connects to OpenWeatherMap to retrieve current and historical weather data:

```python
from weather_utils import fetch_weather_data

# Fetch current weather for a location
weather_data = fetch_weather_data("New York", api_key="your_api_key")

# Get historical data
historical = fetch_historical_data("Chicago", days=7, api_key="your_api_key")
```

### MetPy Processing

MetPy functions process raw weather data into meteorological variables:

```python
from metpy.calc import dewpoint_from_relative_humidity
from metpy.units import units

# Convert temperature and calculate dewpoint
temperature = 25 * units.degC
relative_humidity = 65 * units.percent
dewpoint = dewpoint_from_relative_humidity(temperature, relative_humidity)
```

### Visualization

Create professional meteorological visualizations using MetPy's plotting utilities:

```python
from weather_viz import create_skewt_plot

# Generate Skew-T diagram
fig = create_skewt_plot(pressure_levels, temperatures, dewpoints)
```

### Data Storage

Weather data is stored in structured formats for analysis and retrieval:

```python
{
    "location": "Seattle",
    "timestamp": "2025-05-16T14:30:00",
    "data": {
        "temperature": 18.5,
        "relative_humidity": 72,
        "pressure": 1012.4,
        "wind_speed": 5.2,
        "wind_direction": 225
    }
}
```

## API Reference

### Weather Data Retrieval

#### `fetch_weather_data(location: str, api_key: str) -> dict`
- Retrieves current weather conditions from OpenWeatherMap
- Parameters:
  * `location`: City name or coordinates
  * `api_key`: OpenWeatherMap API key
- Returns: Dictionary with current weather data
  ```python
  {
      "timestamp": "2025-05-16T14:30:00",
      "location": "Seattle",
      "temperature": 18.5,
      "humidity": 72,
      "pressure": 1012.4,
      "wind_speed": 5.2,
      "wind_direction": 225
  }
  ```

#### `fetch_historical_data(location: str, days: int, api_key: str) -> list`
- Fetches historical weather data for a location
- Parameters:
  * `location`: City name or coordinates
  * `days`: Number of days of historical data (max 7)
  * `api_key`: OpenWeatherMap API key
- Returns: List of hourly weather data points

#### `fetch_sounding_data(station_id: str, date: str = None) -> dict`
- Retrieves upper air sounding data from NOAA
- Parameters:
  * `station_id`: NOAA weather station identifier
  * `date`: Optional date string in YYYY-MM-DD format (defaults to latest)
- Returns: Dictionary with pressure levels, temperatures, and dewpoints

### Meteorological Calculations

#### `calculate_dewpoint(temperature: float, relative_humidity: float) -> float`
- Calculates dewpoint temperature using MetPy
- Parameters:
  * `temperature`: Air temperature in Celsius
  * `relative_humidity`: Relative humidity as percentage
- Returns: Dewpoint temperature in Celsius

#### `calculate_wind_chill(temperature: float, wind_speed: float) -> float`
- Calculates wind chill factor
- Parameters:
  * `temperature`: Air temperature in Celsius
  * `wind_speed`: Wind speed in meters per second
- Returns: Wind chill temperature in Celsius

#### `calculate_stability_indices(pressure: list, temperature: list, dewpoint: list) -> dict`
- Calculates atmospheric stability indices
- Parameters:
  * `pressure`: List of pressure levels in hPa
  * `temperature`: List of temperatures in Celsius
  * `dewpoint`: List of dewpoint temperatures in Celsius
- Returns: Dictionary with stability indices (CAPE, CIN, LI, etc.)

### Visualization Tools

#### `create_skewt_plot(pressure: list, temperature: list, dewpoint: list) -> matplotlib.figure.Figure`
- Creates a Skew-T log-P diagram for atmospheric profile analysis
- Parameters:
  * `pressure`: List of pressure levels in hPa
  * `temperature`: List of temperatures in Celsius
  * `dewpoint`: List of dewpoint temperatures in Celsius
- Returns: Matplotlib figure with Skew-T plot

#### `create_time_series(timestamps: list, values: list, parameter: str) -> matplotlib.figure.Figure`
- Generates time series plot of weather parameter
- Parameters:
  * `timestamps`: List of datetime objects
  * `values`: List of parameter values
  * `parameter`: Parameter name for labeling (e.g., "Temperature")
- Returns: Matplotlib figure with time series plot

#### `create_weather_map(locations: list, values: list, parameter: str) -> matplotlib.figure.Figure`
- Creates a weather map visualization
- Parameters:
  * `locations`: List of (latitude, longitude) tuples
  * `values`: List of parameter values
  * `parameter`: Parameter being mapped
- Returns: Matplotlib figure with weather map

## Usage Examples

Basic usage example:

```python
from weather_metpy import *
import os
from dotenv import load_dotenv

# Load API key from environment
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Fetch current weather
weather = fetch_weather_data("Boston", API_KEY)

# Calculate meteorological parameters
dewpoint = calculate_dewpoint(weather["temperature"], weather["humidity"])
wind_chill = calculate_wind_chill(weather["temperature"], weather["wind_speed"])

print(f"Current conditions in {weather['location']}:")
print(f"Temperature: {weather['temperature']}°C")
print(f"Dewpoint: {dewpoint}°C")
print(f"Feels like: {wind_chill}°C")
```

Creating a Skew-T diagram:

```python
from weather_metpy import *
import matplotlib.pyplot as plt

# Fetch sounding data
sounding = fetch_sounding_data("72518")  # Boston, MA

# Create Skew-T plot
fig = create_skewt_plot(
    sounding["pressure"],
    sounding["temperature"],
    sounding["dewpoint"]
)

# Calculate stability indices
indices = calculate_stability_indices(
    sounding["pressure"],
    sounding["temperature"],
    sounding["dewpoint"]
)

print(f"CAPE: {indices['cape']} J/kg")
print(f"CIN: {indices['cin']} J/kg")

plt.show()
```

## Best Practices

1. Data Retrieval
   - Cache API responses to minimize requests
   - Implement error handling for API failures
   - Use environment variables for API keys

2. MetPy Usage
   - Always use appropriate units with MetPy calculations
   - Validate input data before processing
   - Handle missing data with appropriate techniques

3. Visualization
   - Use consistent color schemes for meteorological variables
   - Include proper labels and units on all plots
   - Create accessible visualizations with clear contrasts