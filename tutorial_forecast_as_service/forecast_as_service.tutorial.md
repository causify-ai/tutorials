# Tutorial Guide: Forecast-As-A-Service

<!-- toc -->

- [Tutorial Guide: Forecast-As-A-Service](#tutorial-guide-forecast-as-a-service)
  * [Introduction](#introduction)
  * [What You'Ll Build](#what-youll-build)
  * [Before You Begin](#before-you-begin)
  * [Using the Script](#using-the-script)

<!-- tocstop -->

## Introduction

- This tutorial walks you through how to run the Forecast‑as‑a‑Service project
  using Docker Compose
  - A two-container system for forecasting time series data
  - Provides an interactive Dash frontend and FastAPI backend
  - Supports uploading time series data and returning Prophet-based forecasts

## What You'Ll Build

- A Dockerized FastAPI backend that runs forecasting using Prophet
- A Dash frontend where users can upload CSV files
- A visualized forecast plot shown on the dashboard

## Before You Begin

- Docker and Docker Compose installed and running
- Local clone of the `tutorial_forecast_as_service` repo
- Linux/macOS terminal
- Ensure ports `8000` (API) and `8050` (UI) are available

## Using the Script

- Step 1: Navigate to the project directory

```bash
> cd $GIT_ROOT/tutorial_forecast_as_service
```

- Step 2: Set up thin environment

```bash
> ./tutorial_forecast_as_service/thin_client/setenv.sh
```

- Step 3: Activate the virtual environment

```bash
> source dev_scripts_tutorial_forecast_as_service/thin_client/setenv.sh
```

- Step 4: Build the Docker image

```bash
> i docker_build_local_image --version 1.0.0
```

- Step 5: Launch the forecast web service

```bash
> ./devops/docker_run/run_docker_forecast.sh 1.0.0
```

- Step 5: Once running
  - Access the forecast app UI at:
    [http://localhost:8050](http://localhost:8050) or
    [http://0.0.0.0:8050](http://0.0.0.0:8050)
  - Access the FastAPI docs at:
    [http://localhost:8000/docs](http://localhost:8000/docs) or
    [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)
