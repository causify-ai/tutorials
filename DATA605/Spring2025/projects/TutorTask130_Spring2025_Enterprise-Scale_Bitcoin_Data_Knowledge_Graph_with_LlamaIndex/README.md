<!-- toc -->

- [Project files](#project-files)
- [Setup and Dependencies](#setup-and-dependencies)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)
    + [Environment Setup](#environment-setup)

<!-- tocstop -->

# Project files

- Author: Harshavardhan C. Patil <hcpatil@umd.edu>
- Date: 2025-05-17

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
- `llamaindex.API.ipynb`: a notebook describing the native API of llamaindex
- `llamaindex.API.md`: a description of the native API of llamaindex
- `llamaindex.API.py`: code for using API of llamaindex
- `llamaindex.example.ipynb`: a notebook implementing a project using llamaindex
- `llamaindex.example.md`: a markdown description of the project
- `llamaindex.example.py`: code for implementing the project

- `dev_scripts_tutorial_llamaindex` boilerplate files
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
  ./helpers_root/dev_scripts_helpers/thin_client/build.py
  ```
- Go to the project dir
  ```
  cd ~DATA605/Spring2025/projects/TutorTask130_Spring2025_Enterprise-Scale_Bitcoin_Data_Knowledge_Graph_with_LlamaIndex/tutorial_llamaindex
  ```
- Activate virtual environment:
  ```bash
  source dev_scripts_tutorial_llamaindex/thin_client/setenv.sh
  ```
- Build Docker Image:
  ```bash
  i docker_build_local_image --version 1.0.0
  ```
- Run Container:
  ```bash
  i docker_bash --skip-pull --stage local --version 1.0.0
  ```
- Launch Jupyter Notebook:
  ```bash
  i docker_jupyter --skip-pull --stage local --version 1.0.0 -d
  ```

### Environment Setup
Generate and set the API Key env variables in devops/env/default.env <br>
FRED_API_KEY -> https://fred.stlouisfed.org/docs/api/api_key.html <br>
BTC_PUBLIC_TOKEN -> https://www.allnodes.com/ <br>
OPENAI_API_KEY -> https://platform.openai.com/api-keys <br>
