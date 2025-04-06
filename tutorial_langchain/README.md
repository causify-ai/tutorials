<!-- toc -->

- [Project files](#project-files)
- [Setup and Dependencies](#setup-and-dependencies)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)
    + [Environment Setup](#environment-setup)

<!-- tocstop -->

# Project files

- Author: Krishna Pratardan Taduri <kptaduri@umd.edu>
- Date: 2025-03-15

This project contains the following files

- Boilerplate files to get the project run in `//tutorials`
  - `changelog`.txt
  - `conftest`.py
  - `invoke`.yaml
  - `pip_list`.txt
  - `poetry`.lock.out
  - `pytest`.ini
  - `repo_config`.yaml
  - `tasks`.py

- `README`.md: This file
- `langchain`.API.ipynb: a notebook describing the native API of LangChain
- `langchain`.API.md: a description of the native API of LangChain
- `langchain`.API.py: code for using API of LangChain
- `langchain`.example.ipynb: a notebook implementing a project using LangChain
- `langchain`.example.md: a markdown description of the project
- `langchain`.example.py: code for implementing the project

- `dev_scripts_tutorial_langchain` boilerplate files
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
  > cd tutorial_langchain
  ```
- Activate virtual environment:
  ```bash
  > source dev_scripts_tutorial_langchain/thin_client/setenv.sh
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

### Environment Setup

Set the `OPENAI_API_KEY` environment variable for API access:

```python
import os
os.environ["OPENAI_API_KEY"] = "<your_openai_api_key>"
```
