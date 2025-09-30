<!-- toc -->

- [Project files](#project-files)
- [Setup and Dependencies](#setup-and-dependencies)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)
    + [Environment Setup](#environment-setup)

<!-- tocstop -->

# Project files

- Author: Krishna Pratardan Taduri <kptaduri@umd.edu> and Indrayudd Roy Chowdhury <indro@umd.edu>
- Date: 2025-09-05

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
- `hllm.example.ipynb`: a notebook implementing example use-cases using `hllm.py`
- `hllm.example.md`: a description of using `hllm.py`
- `hllm.example.py`: code with example use-cases using `hllm.py`
- `openai.example.ipynb`: a notebook implementing example use-cases using the native API of OpenAI
- `openai.example.md`: a description of using the native API of OpenAI
- `openai.example.py`: code using the native API of OpenAI


- `dev_scripts_tutorial_openai` boilerplate files
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
  > cd tutorial_openai
  ```
- Activate virtual environment:
  ```bash
  > source dev_scripts_tutorial_openai/thin_client/setenv.sh
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

### Environment Setup

Set the `OPENAI_API_KEY` environment variable for API access:

```python
import os
os.environ["OPENAI_API_KEY"] = "<your_openai_api_key>"
```
