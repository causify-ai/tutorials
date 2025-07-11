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

    Attributes:
      - df: the input time series data
      - config: configurations for the forecasting model
      - holidays: holiday records used by Prophet
    """
    df: List[Dict]
    config: Dict
    holidays: Optional[List[Dict]] = None


# #############################################################################
# ForecastResponse
# #############################################################################


class ForecastResponse(pydantic.BaseModel):
    """
    Output schema for returning forecasted values.

    Attributes:
      - forecast: forecasted records
    """
    forecast: List[Dict]


# #############################################################################
# UploadResponse
# #############################################################################


class UploadResponse(pydantic.BaseModel):
    """
    Output schema for successful file upload.

    Attributes:
      - message: confirmation message on successful upload
    """
    message: str
