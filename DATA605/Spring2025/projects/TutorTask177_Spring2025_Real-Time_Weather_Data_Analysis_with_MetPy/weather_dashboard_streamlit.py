import streamlit as st
import requests
import pandas as pd
import datetime
import time
import matplotlib.pyplot as plt
import numpy as np
from metpy.plots import SkewT
from metpy.units import units
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# --- CONFIG ---
API_KEY = "e3019527d4076cd2e0e5ae7088c3c9c7"  # Replace with your actual API key
CITIES = ["New York", "London", "Tokyo", "Delhi"]
CSV_FILE = "weather_log.csv"
REFRESH_INTERVAL = 3600  # seconds (1 hour)

# --- FETCH WEATHER DATA ---
def fetch_weather_data(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return {
            "city": city,
            "datetime": datetime.datetime.utcfromtimestamp(data["dt"]),
            "temperature_C": data["main"]["temp"],
            "pressure_hPa": data["main"]["pressure"],
            "humidity_percent": data["main"]["humidity"],
            "wind_speed_mps": data["wind"]["speed"],
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"]
        }
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data for {city}: {e}")
        return None

# --- LOAD DATA ---
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(CSV_FILE, parse_dates=["datetime"])
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# --- SAVE DATA ---
def save_data(data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# --- PLOT SKEW-T DIAGRAM ---
def plot_skewt():
    fig = plt.figure(figsize=(6, 6))
    skew = SkewT(fig)

    # Sample data for demonstration
    pressure = np.linspace(1000, 100, 50) * units.hPa
    temperature = (15 - 0.0065 * (1000 - pressure.magnitude)) * units.degC
    dewpoint = (temperature.magnitude - 5) * units.degC

    skew.plot(pressure, temperature, 'r')
    skew.plot(pressure, dewpoint, 'g')
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-40, 40)
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()
    st.pyplot(fig)

# --- MAIN APP ---
def main():
    st.title("Live Weather Dashboard 🌤️")

    # Auto-refresh every hour
    st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="auto_refresh")

    # Fetch and save new data
    if st.button("Fetch Latest Data"):
        for city in CITIES:
            data = fetch_weather_data(API_KEY, city)
            if data:
                save_data(data)
        st.success("Data fetched and saved successfully.")

    df = load_data()
    if df.empty:
        st.warning("No data available. Please fetch data first.")
        st.stop()

    # City selection
    city = st.selectbox("Select city", df["city"].unique())
    city_data = df[df["city"] == city].sort_values("datetime")

    # Show latest metrics
    latest = city_data.iloc[-1]
    st.subheader(f"Latest Weather Metrics for {city}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperature (°C)", latest["temperature_C"])
    col2.metric("Humidity (%)", latest["humidity_percent"])
    col3.metric("Wind Speed (m/s)", latest["wind_speed_mps"])
    col4.metric("Pressure (hPa)", latest["pressure_hPa"])

    # Time-series plots
    st.subheader("Temperature Over Time")
    st.line_chart(city_data.set_index("datetime")["temperature_C"])

    st.subheader("Humidity Over Time")
    st.line_chart(city_data.set_index("datetime")["humidity_percent"])

    # Skew-T diagram
    st.subheader("Skew-T Diagram (Sample Data)")
    plot_skewt()

    # Interactive Map with Weather Stations
    st.subheader("Weather Stations Map")
    m = folium.Map(location=[20, 0], zoom_start=2)
    for city in CITIES:
        data = fetch_weather_data(API_KEY, city)
        if data:
            lat = data["lat"]
            lon = data["lon"]
            popup_text = f"{city}: {data['temperature_C']}°C, {data['humidity_percent']}% humidity"
            folium.Marker([lat, lon], popup=popup_text).add_to(m)
    st_folium(m, width=700)

    # Historical Data Comparison
    st.subheader("Historical Data Comparison")
    start_date = st.date_input("Start Date", value=datetime.date.today() - datetime.timedelta(days=7))
    end_date = st.date_input("End Date", value=datetime.date.today())
    mask = (df['datetime'].dt.date >= start_date) & (df['datetime'].dt.date <= end_date)
    filtered_data = df.loc[mask]
    for city in CITIES:
        city_hist_data = filtered_data[filtered_data['city'] == city]
        st.line_chart(city_hist_data.set_index('datetime')['temperature_C'], height=200)

    # Customizable Alerts and Notifications
    st.subheader("Custom Alerts")
    temp_threshold = st.slider("Temperature Alert Threshold (°C)", min_value=-30, max_value=50, value=35)
    wind_threshold = st.slider("Wind Speed Alert Threshold (m/s)", min_value=0, max_value=30, value=15)
    for city in CITIES:
        city_data = df[df['city'] == city]
        if not city_data.empty:
            latest = city_data.iloc[-1]
            if latest["temperature_C"] > temp_threshold:
                st.warning(f"⚠️ High temperature alert for {city}: {latest['temperature_C']}°C")
            if latest["wind_speed_mps"] > wind_threshold:
                st.warning(f"💨 High wind speed alert for {city}: {latest['wind_speed_mps']} m/s")

    # Downloadable Reports
    st.subheader("Download Weather Data")
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    csv_data = convert_df_to_csv(df)
    st.download_button(
        label="Download Weather Data as CSV",
        data=csv_data,
        file_name='weather_data.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
