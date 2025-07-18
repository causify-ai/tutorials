"""
Import as:

import tutorial_forecast_as_service.frontend.config as tfasfrco
"""

# FastAPI service configuration.
API_BASE_URL = "http://forecast_api:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload_data"
FORECAST_ENDPOINT = f"{API_BASE_URL}/forecast"

# App configuration.
APP_TITLE = "Forecast as a Service"
APP_PORT = 8050
DEBUG_MODE = True

# Styling.
UPLOAD_STYLE = {
    "width": "100%",
    "height": "60px",
    "lineHeight": "60px",
    "borderWidth": "1px",
    "borderStyle": "dashed",
    "borderRadius": "5px",
    "textAlign": "center",
    "margin": "10px",
}

MAIN_STYLE = {"margin": "20px", "fontFamily": "Arial, sans-serif"}

BUTTON_STYLE = {"marginBottom": "20px"}

SECTION_STYLE = {"marginBottom": "30px"}

HEADER_STYLE = {"textAlign": "center", "marginBottom": "30px"}

TABLE_STYLE = {"width": "100%", "marginTop": "10px"}

SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
