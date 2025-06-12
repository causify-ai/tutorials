# Tutorial on Spark SQL

Author: Neha Dutt

---

# Project Files

---

This tutorial contains the following files:

- `Docker Container`
    - docker_bash.sh
    - docker_build.sh
    - docker_build.version.log
    - docker_clean.sh
    - Dockerfile
    - requirements.txt
    - ...Additional files
- `README.md`: This file which contains information on how to start the Docker container.
- `sparkSQL_API.ipynb`: Notebook describing the native API of Spark SQL along with a simple example and basic SQL queries.
- `sparkSQL_API.md`: Description of the native API of Spark SQL.
- `books.csv`: Data corresponding to example in Spark SQL API notebook.
- `prices.csv`: Data corresponding to example in Spark SQL API notebook.
- `sparkSQL_example.ipynb`: Notebook implementing the project on Bitcoin prices using Spark SQL.
- `sparkSQL_example.md`: Description of the project on Bitcoin prices using Spark SQL.
- `sparkSQL.utils`: Class and functions to load data from API endpoint corresponding to sparkSQL_example.ipynb.

---


## Instructions

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

5. Under the folder '/data', you will find all the files that are required for this tutorial.

6. Read the markdown files and run the notebooks to follow the examples.
