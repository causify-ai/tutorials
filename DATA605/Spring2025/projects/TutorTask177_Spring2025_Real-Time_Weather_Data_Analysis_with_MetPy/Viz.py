import matplotlib.pyplot as plt
from metpy.plots import SkewT, StationPlot, add_metpy_logo
from metpy.units import units
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.dates import DateFormatter
import datetime
from DataProcessing import process_weather_data  # Ensure this module exists

def plot_time_series(weather_data):
    """Plot a time series of Temperature, Dew Point, and Wind Chill."""
    plt.figure(figsize=(10, 5))
    plt.title("Temperature, Dew Point and Wind Chill")

    # Convert datetime from timestamp to readable date
    datetime_values = [datetime.datetime.fromtimestamp(weather_data["datetime"])]

    # Plot Temperature, Dew Point, and Wind Chill
    plt.plot(datetime_values, [weather_data["temperature_C"]], 'ro', label="Temperature (°C)")
    plt.plot(datetime_values, [weather_data["dew_point_C"]], 'go', label="Dew Point (°C)")
    if weather_data["wind_chill_C"]:
        plt.plot(datetime_values, [weather_data["wind_chill_C"]], 'bo', label="Wind Chill (°C)")

    plt.legend()
    plt.grid(True)
    
    # Formatting datetime for better readability
    plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)
    plt.savefig("time_series_plot.png")
    plt.close()

def plot_skewt():
    """Plot a Skew-T diagram."""
    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig)

    # Sample data (replace with real atmospheric data)
    p = np.array([1000, 925, 850, 700, 500]) * units.hPa
    t = np.array([15, 12, 7, -5, -20]) * units.degC
    td = np.array([8, 6, 2, -10, -25]) * units.degC

    skew.plot(p, t, 'r')
    skew.plot(p, td, 'g')
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-30, 30)
    add_metpy_logo(fig, 100, 100)
    plt.savefig("skewt_plot.png")
    plt.close()

def plot_station_plot(weather_data):
    """Create a Station Plot to display basic weather information."""
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([-100, -70, 30, 50])
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.STATES, linestyle=':')

    stationplot = StationPlot(ax, [-77], [39], clip_on=True)
    stationplot.plot_parameter('C', [weather_data["temperature_C"]], fontsize=12)
    stationplot.plot_parameter('SW', [weather_data["dew_point_C"]], fontsize=12)
    stationplot.plot_parameter('N', [weather_data["pressure_hPa"]], fontsize=12)
    stationplot.plot_barb([weather_data["wind_speed_mps"]], [0])
    plt.savefig("station_plot.png")
    plt.close()

def generate_visualizations(weather_data):
    """Generate all visualizations using the processed weather data."""
    # Generate the plots
    plot_time_series(weather_data)
    plot_skewt()
    plot_station_plot(weather_data)

    print("Visualizations generated: Time series, Skew-T, and Station plots.")
