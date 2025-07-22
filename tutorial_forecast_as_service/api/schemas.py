"""
Import as:

import tutorial_forecast_as_service.api.schemas as tfasapsc
"""

from typing import Dict, List, Optional

import pydantic


# #############################################################################
# ForecastRequest
# #############################################################################


class ForecastRequest(pydantic.BaseModel):
    """
    Input schema for posting a forecasting request.
    """
    # The input time series data.
    df: List[Dict]
    # Configurations for the forecasting model.
    config: Dict
    # Holiday records used by Prophet.
    holidays: Optional[List[Dict]] = None


# #############################################################################
# ForecastResponse
# #############################################################################


class ForecastResponse(pydantic.BaseModel):
    """
    Output schema for returning forecasted values.
    """
    # Forecasted records.
    forecast: List[Dict]


# #############################################################################
# UploadResponse
# #############################################################################


class UploadResponse(pydantic.BaseModel):
    """
    Output schema for successful file upload.
    """
    # Confirmation message on successful upload.
    message: str
