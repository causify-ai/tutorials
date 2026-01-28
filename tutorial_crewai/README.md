<!-- toc -->

- [Setup and Dependencies](#setup-and-dependencies)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)

<!-- tocstop -->

# Setup and Dependencies

## Building and Running the Docker Container

- Go to the top of the repo
  ```bash
  > cd $GIT_ROOT/tutorial_crewai
  ```
- Build the thin environment
  ```bash
  > ./dev_scripts_tutorial_crewai/thin_client/setenv.sh
  ```
- Activate virtual environment:
  ```bash
  > source dev_scripts_tutorial_crewai/thin_client/setenv.sh
  ```
- Build Docker Image:
  ```bash
  > i docker_build_local_image --version 1.1.0
  ```
- Run Container:
  ```bash
  > i docker_bash --skip-pull --stage local --version 1.1.0
  ```
- Launch Jupyter Notebook:
  ```bash
  > i docker_jupyter --skip-pull --stage local --version 1.1.0 -d
  ```