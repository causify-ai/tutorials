"""
Import as:

import tutorial_forecast_as_service.api.services as tfasapse
"""

import io
import logging
import os
from typing import Any, Dict, List

import fastapi
import helpers.hio as hio
import helpers.hpickle as hpickle
import pandas as pd

import tutorial_prophet.src.prophet_model as tpsrprmo

_LOG = logging.getLogger(__name__)

_UPLOAD_DIR = "tmp.forecast_as_service.upload"
_UPLOAD_PATH = os.path.join(_UPLOAD_DIR, "df.pkl")


def handle_upload(file: fastapi.UploadFile) -> Dict[str, str]:
    """
    Read and parse uploaded CSV file, then persist to disk.

    :param file: uploaded file object from FastAPI
    :return: upload confirmation message
    """
    contents = file.file.read()
    df = pd.read_csv(io.BytesIO(contents))
    _LOG.info("Data uploaded with shape: %s", df.shape)
    hio.create_dir(_UPLOAD_DIR, incremental=True)
    hpickle.to_pickle(df, _UPLOAD_PATH)
    return {"message": "Upload successful"}


def handle_forecast() -> Dict[str, List[Dict[str, Any]]]:
    """
    Run Prophet forecast on the latest uploaded data.

    :return: forecast results
    """
    if not os.path.exists(_UPLOAD_PATH):
        raise RuntimeError("No data uploaded. Please POST to /upload_data first.")
    df = hpickle.from_pickle(_UPLOAD_PATH)
    config = {"daily_seasonality": True}
    forecaster = tpsrprmo.ProphetForecastModel(config)
    forecaster.fit(df)
    forecast_df = forecaster.predict(df)
    return {"forecast": forecast_df[["ds", "yhat"]].to_dict(orient="records")}
