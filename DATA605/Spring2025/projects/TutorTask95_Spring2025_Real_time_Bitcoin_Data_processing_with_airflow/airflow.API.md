<!-- toc -->

* [Apache Airflow API Tutorial](#apache-airflow-api-tutorial)

  * [Table of Contents](#table-of-contents)
  * [General Guidelines](#general-guidelines)
  * [Overview](#overview)
  * [DAG Definition Walkthrough](#dag-definition-walkthrough)

    * [DAG Basics](#dag-basics)
    * [PythonOperator](#pythonoperator)
    * [Key Parameters](#key-parameters)
  * [Visualizing Workflows](#visualizing-workflows)
  * [Why Use DAGs?](#why-use-dags)

<!-- tocstop -->

# Apache Airflow API Tutorial

This markdown serves as a beginner-friendly guide to understanding the **core API of Apache Airflow**, focusing on native concepts like DAGs and operators. It complements the notebook [`airflow.API.ipynb`](./airflow.API.ipynb), which demonstrates how DAGs are defined programmatically.


## Table of Contents

Use this document to understand:

* How Airflow structures workflows
* The anatomy of a DAG
* Common operator types and parameters


## General Guidelines

* Airflow DAGs are defined in pure Python.
* Every DAG consists of tasks, and each task is an instance of an operator.
* DAGs live inside the `/dags` folder and are automatically discovered by Airflow.
* Scheduling, retries, and dependencies are configured declaratively.


## Overview

A **DAG (Directed Acyclic Graph)** represents a workflow:

* **Directed**: Tasks follow a specific order.
* **Acyclic**: Tasks do not loop back.
* **Graph**: Nodes = tasks, edges = dependencies.

Airflow uses this structure to determine task execution flow, monitor progress, and allow retries.


## DAG Definition Walkthrough

This is a minimal DAG definition for demonstration purposes:

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

def hello():
    print("Hello from Airflow!")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='demo_hello_airflow',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
    description='Sample DAG to illustrate core API',
) as dag:
    hello_task = PythonOperator(
        task_id='say_hello',
        python_callable=hello
    )
```

### DAG Basics

* `dag_id`: Unique name for the DAG
* `schedule_interval`: Controls how often the DAG runs (`@hourly`, `@daily`, etc.)
* `start_date`: When Airflow should begin execution

### PythonOperator

Used to run a Python function. Other common operators include:

* `BashOperator`
* `DummyOperator`
* `BranchPythonOperator`

### Key Parameters

* `task_id`: Unique task name within the DAG
* `python_callable`: The Python function to execute
* `retries`: Number of retry attempts if the task fails
* `retry_delay`: How long to wait before retrying


## Visualizing Workflows

Airflow provides a web-based UI to manage and monitor your DAGs:

* View DAG runs and task statuses
* Trigger DAGs manually
* Inspect logs and dependencies

Start the webserver (default: `localhost:8080`) and login with admin credentials to access these features.


## Why Use DAGs?

DAGs allow you to:

* Represent complex workflows as modular, maintainable Python code
* Automate task scheduling and retries
* Gain visibility through detailed logging and UI

Understanding DAGs and Airflow operators is a prerequisite to building scalable, production-grade data pipelines.
