
---
# Prefect API Tutorial

This document demonstrates how to use the **Prefect 2.x native API** to build and orchestrate Python workflows. Prefect is a modern data orchestration framework designed for reliability, observability, and ease of use.

## 🧭 What This Tutorial Covers

- Introduction to Prefect’s core concepts
- Writing reusable tasks and flows
- Passing parameters
- Logging and debugging
- Scheduling flows (briefly)
- References and citations

---

## 🧠 Prerequisites

- Python 3.7+
- `prefect >= 2.0.0`
- Familiarity with basic Python functions

---

## 📦 Setup and Imports

```python
%load_ext autoreload
%autoreload 2
%matplotlib inline

import logging
from typing import List
from time import sleep

import helpers.hdbg as hdbg
import helpers.hprint as hprint

hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)
hprint.config_notebook()
````

---

## 🔧 Core Imports from Prefect

```python
from prefect import flow, task, get_run_logger
```

---

## ⚙️ Creating Tasks

Tasks are basic units of computation in Prefect.

```python
@task
def square(n: int) -> int:
    return n * n
```

Tasks can include logging, retries, caching, and more.

---

## 🔁 Composing Tasks in a Flow

Flows orchestrate one or more tasks.

```python
@flow
def compute_squares(numbers: List[int]) -> List[int]:
    results = []
    for number in numbers:
        results.append(square.submit(number))
    return results
```

Use `.submit()` for concurrent execution.

---

## 🧪 Testing the Flow

```python
if __name__ == "__main__":
    output = compute_squares([2, 4, 6])
    print(output)
```

---

## 📑 Flow Logs

Use `get_run_logger()` for logging inside tasks:

```python
@task
def greet(name: str) -> None:
    logger = get_run_logger()
    logger.info(f"Hello, {name}!")
```

---

## 🧵 Parameterized Flows

Flows can take parameters directly:

```python
@flow
def say_hello(name: str = "Prefect"):
    print(f"Hello, {name}!")
```

---

## 📅 Scheduling Flows (Concept)

You can schedule Prefect flows using the CLI or Prefect Cloud UI.

```python
from datetime import timedelta

if __name__ == "__main__":
    say_hello.serve(
        name="greeting-schedule",
        interval=timedelta(minutes=5)
    )
```

> Note: `.serve()` runs a deployment that polls for schedule.

---

## 🧠 Summary

| Concept    | Decorator          | Purpose                            |
| ---------- | ------------------ | ---------------------------------- |
| Task       | `@task`            | A function Prefect can orchestrate |
| Flow       | `@flow`            | Container of one or more tasks     |
| Parameters | args               | Passed to flows at runtime         |
| Logging    | `get_run_logger()` | In-task logging support            |

---

## 🔗 References and Resources

* 📘 [Prefect Docs](https://docs.prefect.io/)
* 🧪 [Prefect Flows API](https://docs.prefect.io/latest/concepts/flows/)
* 🛠️ [Task Concurrency](https://docs.prefect.io/latest/concepts/tasks/#task-concurrency)
* 💡 [Prefect Orchestration Patterns](https://docs.prefect.io/latest/)




