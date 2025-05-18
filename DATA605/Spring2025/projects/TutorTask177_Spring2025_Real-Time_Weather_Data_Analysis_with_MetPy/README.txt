Real-Time Weather Data Analysis with MetPy
==========================================

Overview
--------
This project introduces students to MetPy, an open-source Python library tailored for meteorological data analysis and visualization. Participants will set up a real-time data processing pipeline to fetch, analyze, and visualize live weather data, gaining hands-on experience with MetPy's capabilities.

Objective
---------
Develop a real-time weather data analysis system that:
- Fetches live meteorological data from public APIs.
- Performs essential analyses using MetPy.
- Visualizes the results through interactive dashboards.
- Automates data fetching and visualization at regular intervals.

Technologies Used
-----------------
- MetPy: Meteorological data analysis and visualization.
- Streamlit: Interactive web application framework.
- OpenWeatherMap API: Source for real-time weather data.
- Docker: Containerization for easy deployment.

Installation
------------
1. Clone the Repository:
   git clone https://github.com/yourusername/weather-dashboard.git
   cd weather-dashboard

2. Set Up Environment Variables:
   Create a `.env` file in the root directory and add your OpenWeatherMap API key:
   API_KEY=your_openweathermap_api_key

3. Build and Run with Docker:
   Ensure Docker is installed on your system. Then, build and run the Docker container:
   docker build -t weather-dashboard .
   docker run -p 8501:8501 weather-dashboard

   Access the application at http://localhost:8501

Usage
-----
- Fetch Latest Data: Click the "Fetch Latest Data" button to retrieve current weather data for predefined cities.
- Select City: Use the dropdown to select a city and view its weather metrics.
- Visualizations:
  - Temperature Over Time: Line chart displaying temperature trends.
  - Humidity Over Time: Line chart displaying humidity trends.
  - Skew-T Diagram: Visual representation of atmospheric profiles.
- Auto-Refresh: Enable auto-refresh to update data at regular intervals.

Project Structure
-----------------
weather-dashboard/
├── Dockerfile
├── requirements.txt
├── weather_log.csv
├── your_script.py
└── README.txt

Resources
---------
- MetPy Documentation: https://unidata.github.io/MetPy/
- OpenWeatherMap API Documentation: https://openweathermap.org/api
- Streamlit Documentation: https://docs.streamlit.io/
- Docker Documentation: https://docs.docker.com/

License
-------
This project is licensed under the MIT License. See the LICENSE file for details.
