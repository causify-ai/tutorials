"""
Import as: 

import tutorial_forecast_as_service.api.data_utils as tfasadu
"""

import io
import logging
import base64
import typing
import pandas as pd
import requests

import tutorial_forecast_as_service.api.config as tfasaconf 

logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)


def parse_csv_contents(contents: str, filename: str) -> typing.Optional[pd.DataFrame]:
    """
    Parse uploaded CSV file contents.
    
    :param contents: base64 encoded file contents
    :param filename: name of uploaded file
    :return: parsed DataFrame or None if error
    """
    try:
        _, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))        
        _LOG.info(f"Parsed {filename} with shape {df.shape}")
        if 'ds' not in df.columns or 'y' not in df.columns:
            raise ValueError("CSV must contain 'ds' (date) and 'y' (value) columns")
        # Convert ds to datetime if it's not already
        df['ds'] = pd.to_datetime(df['ds'])
        
        return df
        
    except Exception as e:
        _LOG.error(f"Error parsing CSV: {e}")
        return None


def upload_data_to_api(df: pd.DataFrame) -> typing.Dict[str, typing.Any]:
    """
    Upload DataFrame to FastAPI service.
    
    :param df: DataFrame to upload
    :return: API response
    """
    try:
        csv_string = df.to_csv(index=False)        
        # Prepare file and send to API
        _LOG.info(f"Uploading {len(df)} rows to API")
        files = {'file': ('data.csv', csv_string, 'text/csv')}
        response = requests.post(tfasaconf.UPLOAD_ENDPOINT, files=files)
        response.raise_for_status()        
        return {"success": True, "message": response.json().get("message", "Upload successful")}
        
    except requests.exceptions.RequestException as e:
        _LOG.error(f"API upload error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        _LOG.error(f"Upload error: {e}")
        return {"success": False, "error": str(e)}


def get_forecast_from_api() -> typing.Dict[str, typing.Any]:
    """
    Retrieve forecast from FastAPI service.
    
    :return: forecast data or error message
    """
    try:
        # Request forecast data from the API and convert it to a DataFrame
        response = requests.get(tfasaconf.FORECAST_ENDPOINT)
        response.raise_for_status()        
        data = response.json()
        forecast_data = data.get("forecast", [])       
        _LOG.info(f"Received forecast data with {len(forecast_data)} entries")
        # Return empty DataFrame if no forecast data present 
        if not forecast_data:
            return {"success": False, "error": "No forecast data received"}        
        forecast_df = pd.DataFrame(forecast_data)
        forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])        
        return {"success": True, "forecast": forecast_df}   
         
    except requests.exceptions.RequestException as e:
        _LOG.error(f"API forecast error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        _LOG.error(f"Forecast error: {e}")
        return {"success": False, "error": str(e)}