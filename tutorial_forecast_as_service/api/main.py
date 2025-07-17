"""
Import as:

import tutorial_forecast_as_service.api.main as tfasapma
"""

import logging

import fastapi
import helpers.hdbg as hdbg

import tutorial_forecast_as_service.api.routes as tfasapro

hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)

app = fastapi.FastAPI(title="Forecast as a Service")
app.include_router(tfasapro.router)
