"""
Import as:

import tutorial_forecast_as_service.frontend.data_utils as tfasfdaut
"""

import base64
import io
import logging
from typing import Any, Dict

import pandas as pd
import requests

import tutorial_forecast_as_service.frontend.config as tfasfrco

_LOG = logging.getLogger(__name__)


def parse_csv_contents(contents: str, filename: str) -> pd.DataFrame:
    """
    Parse uploaded CSV file contents.

    :param contents: file contents
    :param filename: name of uploaded file
    :return: parsed data
    """
    try:
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        _LOG.info("Parsed %s with shape %s", filename, df.shape)
        if "ds" not in df.columns or "y" not in df.columns:
            raise ValueError(
                "CSV must contain 'ds' (date) and 'y' (value) columns"
            )
        df["ds"] = pd.to_datetime(df["ds"])
        return df
    except Exception as e:
        raise ValueError(f"Failed to parse uploaded file: {e}") from e


def upload_data_to_api(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Upload DataFrame to FastAPI service.

    :param df: data to upload
    :return: API response
    """
    try:
        csv_string = df.to_csv(index=False)
        # Prepare requests.
        files = {"file": ("data.csv", csv_string, "text/csv")}
        _LOG.info("Uploading %d rows to API", len(df))
        # Get API request.
        response = requests.post(tfasfrco.UPLOAD_ENDPOINT, files=files, timeout=5)
        response.raise_for_status()
        # Parse response.
        response_data = response.json()
        return {
            "success": True,
            "message": response_data.get("message", "Upload successful"),
        }
    # Handle errors.
    except requests.exceptions.RequestException as e:
        _LOG.error("API upload error: %s", e)
        return {"success": False, "error": str(e)}
    except (ValueError, TypeError, UnicodeDecodeError) as e:
        _LOG.error("Upload error: %s", e)
        return {"success": False, "error": str(e)}


def get_forecast_from_api() -> Dict[str, Any]:
    """
    Retrieve forecast from FastAPI service.

    :return: forecast data or error message
    """
    try:
        response = requests.get(tfasfrco.FORECAST_ENDPOINT, timeout=5)
        response.raise_for_status()
        # Parse response.
        data = response.json()
        forecast_data = data.get("forecast", [])
        _LOG.info("Received forecast data with %d entries", len(forecast_data))
        if not forecast_data:
            return {"success": False, "error": "No forecast data received"}
        # Convert forecast records into DataFrame.
        forecast_df = pd.DataFrame(forecast_data)
        forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])
        return {"success": True, "forecast": forecast_df}
    # Handle errors.
    except requests.exceptions.RequestException as e:
        _LOG.error("API forecast error: %s", e)
        return {"success": False, "error": str(e)}
    except (ValueError, TypeError, UnicodeDecodeError) as e:
        _LOG.error("Upload error: %s", e)
        return {"success": False, "error": str(e)}
