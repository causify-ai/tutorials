# Real-Time Weather Data Analysis with MetPy

// ... existing code ...

### Visualization

The project includes an interactive Streamlit dashboard with the following features:

1. **Real-Time Weather Monitoring**
   ```python
   st.subheader("⏱️ Current Weather Conditions")
   if st.button("📥 Fetch Current Weather"):
       current = fetch_weather_data(selected_city, API_KEY)
       st.success(f"Current Temperature in {current['location']}: {current['temperature']}°C")
   ```

2. **Historical Weather Analysis**
   - 7-day hourly weather chart
   - Interactive date range selection
   - Temperature trend visualization
   ```python
   fig1, ax1 = plt.subplots(figsize=(12, 4))
   ax1.plot(df.index, df['temperature'], marker='o', markersize=2, color='crimson')
   ax1.set_title(f"Temperature in {selected_city} (Last 7 Days)")
   ```

3. **Meteorological Parameters**
   - Temperature
   - Humidity
   - Pressure
   - Wind speed and direction
   ```python
   col1, col2 = st.columns(2)
   with col1:
       st.metric("Temperature", f"{current['temperature']}°C", f"{temp_change}°C")
       st.metric("Pressure", f"{current['pressure']} hPa", f"{pressure_change} hPa")
   with col2:
       st.metric("Humidity", f"{current['humidity']}%", f"{humidity_change}%")
       st.metric("Wind Speed", f"{current['wind_speed']} m/s", f"{wind_change} m/s")
   ```

4. **Advanced Meteorological Analysis**
   - Dew Point Calculation
   - Heat Index
   - Wind Chill Factor
   ```python
   # Calculate derived values
   dewpoint = calculate_dewpoint(current['temperature'], current['humidity'])
   heat_index = calculate_heat_index(current['temperature'], current['humidity'])
   wind_chill = calculate_wind_chill(current['temperature'], current['wind_speed'])
   
   st.subheader("Derived Meteorological Parameters")
   st.info(f"Dew Point: {dewpoint:.1f}°C")
   st.info(f"Heat Index (Feels Like): {heat_index:.1f}°C")
   st.info(f"Wind Chill: {wind_chill:.1f}°C")
   ```

5. **Upper Air Analysis**
   - Skew-T Log-P Diagrams
   - Atmospheric stability indices
   - Vertical profile visualization
   ```python
   sounding = fetch_sounding_data(station_id)
   
   # Calculate stability indices
   indices = calculate_stability_indices(
       sounding['pressure'],
       sounding['temperature'],
       sounding['dewpoint']
   )
   
   # Create Skew-T plot
   fig_skewt = create_skewt_plot(
       sounding['pressure'],
       sounding['temperature'],
       sounding['dewpoint']
   )
   
   st.pyplot(fig_skewt)
   st.metric("CAPE", f"{indices['cape']:.0f} J/kg")
   st.metric("CIN", f"{indices['cin']:.0f} J/kg")
   st.metric("LI", f"{indices['lifted_index']:.1f}")
   ```

6. **Weather Maps**
   - Surface temperature map
   - Precipitation overlay
   - Pressure systems visualization
   ```python
   # Create weather map
   map_data = fetch_regional_data(region="northeast")
   locations = [(loc['lat'], loc['lon']) for loc in map_data]
   temperatures = [loc['temperature'] for loc in map_data]
   
   fig_map = create_weather_map(locations, temperatures, "Temperature (°C)")
   st.pyplot(fig_map)
   ```

7. **Data Export**
   - Download weather data as CSV
   - Automated data refresh
   ```python
   csv_data = df.reset_index().to_csv(index=False).encode("utf-8")
   st.download_button(
       label="📥 Download Weather Data CSV",
       data=csv_data,
       file_name=f"{selected_city}_weather_data.csv",
       mime="text/csv"
   )
   ```

// ... existing code ...

## Results and Visualization

The project provides a comprehensive suite of meteorological visualization and analysis tools:

1. **Interactive Weather Dashboards**
   - Real-time condition updates
   - Historical weather trends
   - Derived parameter calculations

2. **Atmospheric Analysis**
   - Temperature and humidity profiles
   - Pressure trend analysis
   - Wind pattern visualization
   - Stability assessment

3. **Forecasting Tools**
   - Short-term weather predictions
   - Trend analysis
   - Diurnal patterns

4. **Educational Features**
   - Interactive Skew-T diagram explanation
   - Meteorological parameter relationships
   - Weather system visualization

The system successfully demonstrates:
- Real-time weather monitoring
- Advanced meteorological analysis
- Upper air data interpretation
- Data visualization best practices
- Interactive educational components
- Meteorological parameter calculation

Through this implementation, students gain hands-on experience with MetPy's capabilities for weather data analysis while developing practical skills in meteorological visualization and interpretation. The Streamlit interface provides an accessible way to interact with complex atmospheric data and understand weather patterns through both surface and upper-air analysis.