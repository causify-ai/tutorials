<!-- toc -->

- [Project files](#project-files)
- [Setup and Dependencies](#setup-and-dependencies)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)
    + [Environment Setup](#environment-setup)

<!-- tocstop -->

# Project files

- Author: Prahar Modi
- Date: 09 Apr, 2025

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
- `github.API.ipynb`: a notebook describing the native API of GitHub
- `github.API.md`: a description of the native API of GitHub
- `github.API.py`: code for using API of GitHub
- `github.example.ipynb`: a notebook implementing a project using GitHub
- `github.example.md`: a markdown description of the project
- `github.example.py`: code for implementing the project

- `dev_scripts_tutorial_github` boilerplate files
- `devops` mostly boilerplate files
  - `devops/docker_build/pyproject.toml`: contains the dependency of the package
    in Poetry format

# Setup and Dependencies

## Building and Running the Docker Container

- Go to the top of the repo
  ```
  > cd $GIT_ROOT/tutorial_github_causify_style
  ```
- Build the thin environment
  ```bash
  > ./dev_scripts_tutorial_github/thin_client/setenv.sh
  ```
- Activate virtual environment:
  ```bash
  > source dev_scripts_tutorial_github/thin_client/setenv.sh
  ```
- Build Docker Image:
  ```bash
  > i docker_build_local_image --version 1.0.0
  ```
- Run Container:
  ```bash
  > i docker_bash --skip-pull --stage local --version 1.0.0
  ```
- Launch Jupyter Notebook:
  ```bash
  > i docker_jupyter --skip-pull --stage local --version 1.0.0 -d
  ```