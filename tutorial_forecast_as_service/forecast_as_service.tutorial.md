# Tutorial Guide: Forecast-As-A-Service

<!-- toc -->

- [Introduction](#introduction)
- [What You'Ll Build](#what-youll-build)
- [Before You Begin](#before-you-begin)
- [Using the Script](#using-the-script)

<!-- tocstop -->

## Introduction

- This tutorial walks you through how to run the Forecast‑as‑a‑Service project
  using Docker Compose
  - A two-container system for forecasting time series data
  - Provides an interactive Dash frontend and FastAPI backend
  - Supports uploading time series data and returning Prophet-based forecasts

## What You'll Build

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

- Step 5: Open the app in your browser
  - Access the forecast app UI at:
    [http://localhost:8050](http://localhost:8050) or
    [http://0.0.0.0:8050](http://0.0.0.0:8050)

  <img src="figs/forecast/image1.png" width="1000"/>
  - Access the FastAPI docs at:
    [http://localhost:8000/docs](http://localhost:8000/docs) or
    [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)

- Step 6: Upload your CSV file
  - Use the drag-and-drop file upload box at the top of the dashboard
  - The file must contain: a `ds` column (date), and a `y` column (value)

  <img src="figs/forecast/image2.png" width="1000"/>

- Step 7: Click generate forecast
  - After upload, press the `Generate Forecast` button

  <img src="figs/forecast/image3.png" width="1000"/>

- Step 8: View forecast results
  - The app will show:
    - A line chart of predicted values
    - A summary of min/max/mean and time range

  <img src="figs/forecast/image4.png" width="1000"/>

- Step 9: Stop the service
  - In the same terminal, press `CTRL+C` once to stop the containers
