<!-- toc -->

- [Project files](#project-files)
- [Setup and Dependencies](#setup-and-dependencies)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)
    + [Environment Setup](#environment-setup)

<!-- tocstop -->


This project contains the following files

- Boilerplate files to get the project run in `//tutorials`
  - `changelog.txt`
  - `conftest.py`
  - `invoke.yaml`
  - `pip_list.txt`
  - `poetry.lock.out`
  - `pytest.ini`
  - `repo_config.yaml`
  - `tasks.py`

- `README.md`: This file
- `tutorial_prophet.ipynb`: a notebook implementing a project using Prophet
- `tutorial_prophet.py`: Python version of the Jupyter notebook
- `prophet_model.py`: code implementing the native packages of Prophet

- `dev_scripts_tutorial_prophet` boilerplate files
- `devops` mostly boilerplate files
  - `devops/docker_build/pyproject.toml`: contains the dependency of the package
    in Poetry format

# Setup and Dependencies

## Building and Running the Docker Container

- Go to the top of the repo
  ```
  > cd $GIT_ROOT
  ```
- Build the thin environment
  ```bash
  > ./helpers_root/dev_scripts_helpers/thin_client/build.py
  ```
- Go to the project dir
  ```
  > cd tutorial_prophet
  ```
- Activate virtual environment:
  ```bash
  > source dev_scripts_tutorial_prophet/thin_client/setenv.sh
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

