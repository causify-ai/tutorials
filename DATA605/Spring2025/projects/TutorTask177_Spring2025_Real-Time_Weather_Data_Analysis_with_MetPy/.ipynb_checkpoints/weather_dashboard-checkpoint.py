import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import os

# Weather data file
csv_file = "weather_log.csv"
skewt_image_path = "skewt_latest.png"

# Load weather data
def load_weather_data():
    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
        df["datetime"] = pd.to_datetime(df["datetime"])
        # Dummy lat/lon if not present (you can modify this to fetch actual values)
        city_coords = {
            "London": (51.5074, -0.1278),
            "New York": (40.7128, -74.0060),
            "Tokyo": (35.6895, 139.6917),
            "Paris": (48.8566, 2.3522),
        }
        df["lat"] = df["city"].map(lambda x: city_coords.get(x, (0, 0))[0])
        df["lon"] = df["city"].map(lambda x: city_coords.get(x, (0, 0))[1])
        return df
    return pd.DataFrame()

# Dash app setup
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Weather Dashboard"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("🌦 Weather Dashboard with Map and Skew-T"), width=12)
    ], className="my-3"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {"label": "Temperature (°C)", "value": "temperature_C"},
                    {"label": "Humidity (%)", "value": "humidity_percent"},
                    {"label": "Wind Speed (m/s)", "value": "wind_speed_mps"},
                    {"label": "Pressure (hPa)", "value": "pressure_hPa"},
                    {"label": "Wind Chill (°C)", "value": "wind_chill_C"},
                ],
                value="temperature_C",
                clearable=False
            )
        ], width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='weather-time-series'), width=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='weather-map'), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Latest Skew-T Plot"),
            html.Img(id="skewt-image", src="/skewt_latest.png", style={"width": "100%", "maxHeight": "500px"})
        ], width=12)
    ]),

    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0)  # refresh every 5 min
], fluid=True)

# Callbacks
@app.callback(
    Output('weather-time-series', 'figure'),
    Output('weather-map', 'figure'),
    Output('skewt-image', 'src'),
    Input('metric-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(selected_metric, _):
    df = load_weather_data()

    if df.empty:
        return px.line(title="No data"), px.scatter_mapbox(), "/skewt_latest.png"

    fig_line = px.line(
        df, x="datetime", y=selected_metric, color="city",
        title=f"{selected_metric.replace('_', ' ').title()} Over Time"
    )
    fig_line.update_traces(mode="lines+markers")

    # Get last record per city for the map
    df_map = df.sort_values("datetime").groupby("city").tail(1)
    fig_map = px.scatter_mapbox(
        df_map, lat="lat", lon="lon", size=selected_metric, color=selected_metric,
        hover_name="city", zoom=1, mapbox_style="carto-positron",
        title=f"Latest {selected_metric.replace('_', ' ').title()} by Location"
    )

    # Skew-T image path
    skewt_src = f"/{skewt_image_path}" if os.path.exists(skewt_image_path) else ""

    return fig_line, fig_map, skewt_src

# Enable serving static images (e.g., skewt_latest.png)
from flask import send_from_directory

@app.server.route("/skewt_latest.png")
def skewt_image():
    return send_from_directory(".", "skewt_latest.png")

if __name__ == "__main__":
    app.run(debug=True)
