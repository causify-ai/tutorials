# Real-Time Bitcoin Price Analysis using Django ORM

This project demonstrates a real-time Bitcoin price tracker and analyzer using Django ORM, Jupyter, and Docker.

---

## 📦 Project Structure

* `django_orm_utils.py`: Wrapper functions to fetch, store, and analyze Bitcoin prices
* `django_orm.API.ipynb`: Shows how to use the API functions
* `django_orm.API.md`: Markdown describing the CoinGecko API and software layer
* `django_orm.example.ipynb`: Full application demo — charting, volatility, peaks
* `django_orm.example.md`: Explanation of the end-to-end app structure
* `Dockerfile`, `docker_*.sh`: Build and run environment setup

---

## 🐳 Running the Project with Docker

### 1. Build Docker Image

```bash
./docker_build.sh
```

### 2. Option A: Launch Jupyter

```bash
./docker_jupyter.sh
```

Then go to:
`http://localhost:8888`

### 3. Option B: Launch Django Web App

```bash
./docker_bash.sh
```

Inside the container:

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Then go to:
`http://localhost:8000`

---

## 📊 Features

* Fetches live Bitcoin prices via CoinGecko API
* Stores price history using Django ORM in SQLite
* Analyzes price trends: average, volatility, peak detection
* Interactive Plotly chart on the frontend
* Clean utility module and Dockerized workflow

---

## 🔧 Requirements

Everything is included in Docker:

* Python 3.9
* Django
* Jupyter Notebook
* Requests, NumPy, SciPy, Plotly

---

## 🧠 Learning Objectives

* Use Django ORM for time-series data storage
* Containerize ML/AI workflows with Docker
* Perform basic statistical analysis with Python
* Visualize financial data using Plotly

---

## 📝 Author

Mukul Gupta
University of Maryland — DATA605 (Spring 2025)
