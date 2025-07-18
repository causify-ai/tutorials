<!-- toc -->

- [Setup and Dependencies](#setup-and-dependencies)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)

<!-- tocstop -->

# Setup and Dependencies

## Building and Running the Docker Container

- Go to the top of the repo
  ```bash
  > cd $GIT_ROOT/tutorial_forecast_as_service
  ```
- Build the thin environment
  ```bash
  > ./tutorial_forecast_as_service/thin_client/setenv.sh
  ```
- Activate virtual environment:
  ```bash
  > source dev_scripts_tutorial_forecast_as_service/thin_client/setenv.sh
  ```
- Build Docker Image:
  ```bash
  > i docker_build_local_image --version 1.0.0
  ```
- Launch forecast web service:
  ```bash
  > ./devops/docker_run/run_docker_forecast.sh 1.0.0
  ```
- Once running:
  - Access the forecast app UI at:
    [http://localhost:8050](http://localhost:8050) or
    [http://0.0.0.0:8050](http://0.0.0.0:8050)
  - Access the FastAPI docs (backend) at:
    [http://localhost:8000/docs](http://localhost:8000/docs) or
    [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)
- Run Container:
  ```bash
  > i docker_bash --skip-pull --stage local --version 1.0.0
  ```
- Launch Jupyter Notebook:
  ```bash
  > i docker_jupyter --skip-pull --stage local --version 1.0.0 -d
  ```
