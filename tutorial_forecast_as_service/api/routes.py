"""
Import as:

import tutorial_forecast_as_service.api.routes as tfasapro
"""

import logging

import fastapi

import tutorial_forecast_as_service.api.schemas as tfasapsc
import tutorial_forecast_as_service.api.services as tfasapse

router = fastapi.APIRouter()
_LOG = logging.getLogger(__name__)


@router.post("/upload_data", response_model=tfasapsc.UploadResponse)
def upload_data(
    file: fastapi.UploadFile = fastapi.File(...),
) -> tfasapsc.UploadResponse:
    """
    Handle CSV file upload and store parsed DataFrame in memory.

    :param file: uploaded CSV file
    :return: response message with upload status
    """
    try:
        return tfasapse.handle_upload(file)
    except Exception as e:
        _LOG.exception("Upload failed")
        raise fastapi.HTTPException(status_code=400, detail=str(e))


@router.get("/forecast", response_model=tfasapsc.ForecastResponse)
def forecast() -> tfasapsc.ForecastResponse:
    """
    Generate a forecast using the latest uploaded data.

    :return: forecast response with predicted values
    """
    try:
        return tfasapse.handle_forecast()
    except Exception as e:
        _LOG.exception("Forecasting failed")
        raise fastapi.HTTPException(status_code=400, detail=str(e))
