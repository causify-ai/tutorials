"""
Import as:

import tutorial_forecast_as_service.api.services as tfasapse
"""

import io
import logging
import os

import pandas as pd

import tutorial_prophet.src.prophet_model as tpsrprmo

_LOG = logging.getLogger(__name__)

_UPLOAD_PATH = "tmp/uploaded_df.pkl"


def handle_upload(file) -> dict:
    """
    Read and parse uploaded CSV file, then persist to disk.

    :param file: uploaded file object from FastAPI
    :return: upload confirmation message
    """
    contents = file.file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
        _LOG.info("Data uploaded with shape: %s", df.shape)
        os.makedirs("tmp", exist_ok=True)
        df.to_pickle(_UPLOAD_PATH)
        return {"message": "Upload successful"}
    except Exception as e:
        _LOG.exception("Failed to parse uploaded file")
        raise RuntimeError(f"Invalid CSV format: {str(e)}")


def handle_forecast() -> dict:
    """
    Run Prophet forecast on the latest uploaded data.

    :return: forecast results
    """
    if not os.path.exists(_UPLOAD_PATH):
        raise RuntimeError("No data uploaded. Please POST to /upload_data first.")
    df = pd.read_pickle(_UPLOAD_PATH)
    config = {"daily_seasonality": True}
    forecaster = tpsrprmo.ProphetForecastModel(config)
    forecaster.fit(df)
    forecast_df = forecaster.predict(df)
    return {"forecast": forecast_df[["ds", "yhat"]].to_dict(orient="records")}
