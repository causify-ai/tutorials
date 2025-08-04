# Forecast as a Service

<!-- toc -->

- [Overview](#overview)
- [Directory Layout](#directory-layout)

<!-- tocstop -->

## Overview

- This project implements a modular Forecast-as-a-Service system
- It includes:
  - A backend API for receiving forecast requests and returning predictions
  - A frontend interface for visualizing forecasts and interacting with users

## Directory Layout

- `api/`: contains the backend forecast API
  - `api/main.py`: FastAPI app definition and router registration
  - `api/routes.py`: defines API endpoints and their handlers
  - `api/schemas.py`: defines request and response schemas using Pydantic
    - `ForecastRequest`: schema for input data
    - `ForecastResponse`: schema for forecast results
  - `api/services.py`: core forecasting logic

- `frontend/`: contains the user-facing interface
  - `frontend/app.py`: Dash app initialization and execution
  - `frontend/layout.py`: defines the structure of the UI
  - `frontend/callbacks.py`: implements interactivity via Dash callbacks
  - `frontend/config.py`: contains configuration variables (e.g., API endpoint
    URL)
  - `frontend/ui_components.py`: contains reusable UI components
  - `frontend/data_utils.py`: helper functions for data parsing and formatting
