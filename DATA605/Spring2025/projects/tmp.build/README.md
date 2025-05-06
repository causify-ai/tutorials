# Project Files

This tutorial contains the following files:

- Docker Container
    - docker_bash.sh
    - docker_build.sh
    - docker_build.version.log
    - docker_clean.sh
    - Dockerfile
    - requirements.txt
    - (more)
- README.md: This file
- sparkSQL.API.ipynb: Notebook describing the native API of Spark SQL along with a simple example.
- sparkSQL.API.md: Description of the native API of Spark SQL.
- books.csv: Data corresponding to example in Spark SQL API notebook.
- prices.csv: Data corresponding to example in Spark SQL API notebook.
- sparkSQL.example.ipynb: Notebook implementing the project using Spark SQL.
- sparkSQL.example.md: Description of the project using Spark SQL.
- sparkSQL.example.py: Code corresponding to the project.

## 1. Set up Environment

1. Go to the top of the directory
```bash
> cd $GIT_ROOT
```
2. Build the dev thin environment
```bash
> ./helpers_root/dev_scripts_helpers/thin_client/build.py
```
3. Go to the project directory
```bash
> cd TutorTask108_Spring2025_Implementing_Real-Time_Bitcoin_Price_Analysis_with_Spark_SQL
```
4. Activate virtual environment
```bash
> source dev_scripts_tutorial_langchain/thin_client/setenv.sh
```

## 2. Run Docker Container

From the project directory -

1. Build the container:
```bash
> ./docker_build.sh
```
2. Run the container:
```bash
> ./docker_bash.sh
```
3. Launch Jupyter Notebook:
```bash
> /data/run_jupyter.sh
```
4. Go to http://localhost:8888.

5. Under the folder '/data', you will find all the files part of this tutorial.

6. Run the notebooks to follow the examples.


