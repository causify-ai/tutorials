
# Real-Time Bitcoin Transaction Anomaly Detection with Anthropic Claude

## Table of Contents
1. [Author](#author)
2. [Overview](#overview)
3. [Project Structure](#project-structure)
4. [How to Run the Project](#how-to-run-the-project)
5. [Documentation Links](#documentation-links)
6. [Final Notes and Disclaimers](#final-notes-and-disclaimers)

---

## Author
**Anvesh Chitturi**  
Email: achittu1@umd.edu

---

## Overview

This tutorial demonstrates how to build an explainable, real-time anomaly detection pipeline for Bitcoin transactions using Anthropic Claude, PySpark, and other open-source tools. It provides a complete walkthrough from data extraction to anomaly explanation, forecasting, and alerting.

The tutorial includes both:
- A **tool-focused API notebook** explaining how to use Anthropic Claude.
- A **project-based example notebook** implementing the Bitcoin anomaly detection pipeline.

---

## Project Structure

| File / Folder | Description |
|---------------|-------------|
| `scripts/` | Contains modular Python scripts used in the pipeline. Each handles one component of the project. |
| `BitcoinTxAnomaly_utils.py` | Wrapper functions to run all scripts cleanly from notebooks. |
| `notebooks/Anthropic.API.ipynb` | Tutorial-style notebook explaining how to use Claude API. |
| `notebooks/BitcoinTxAnomaly.example.ipynb` | End-to-end executable notebook of the anomaly detection project. |
| `dashboards/dashboard_app.py` | Dash dashboard to visualize outputs. |
| `data/raw/` | Contains extracted raw JSON data from the Blockchair API. |
| `data/processed/` | Contains cleaned and aggregated transaction CSVs. |
| `report/` | Final results like Claude explanations, EWMA anomalies, forecasts, and Slack alerts. |
| `Anthropic.API.md` | Markdown guide on Anthropic Claude API usage. |
| `BitcoinTxAnomaly.example.md` | Markdown walkthrough of the Bitcoin anomaly detection project. |

---

## How to Run the Project

We use Docker to ensure consistent environment setup.

### Step 1: Build the Docker container

```bash
./docker_build.sh
```

### Step 2: Run the container interactively

```bash
./run_docker.sh
```

### Step 3: Inside the container, navigate to the notebook folder

```bash
cd notebooks/
jupyter notebook
```

Then open and run `BitcoinTxAnomaly.example.ipynb` and `Anthropic.API.ipynb`.

---

## Python Dependencies

All required Python libraries are listed in the `requirements.txt` file. These include:

- `pyspark` – for large-scale transaction preprocessing
- `anthropic` – Claude API client for explainable anomaly detection
- `prophet` – for time-series forecasting
- `dash`, `plotly` – for dashboard visualization
- `slack-sdk` – for alert integration
- `python-dotenv`, `requests`, `tqdm`, `pandas`, `numpy`, etc.

If you're running outside Docker, install them manually via:

```bash
pip install -r requirements.txt
```


These are automatically installed during Docker container build using:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
```

---


## Slack Alerts Integration

This project supports real-time alerts via Slack.

To enable it:
1. Go to [Slack API: Incoming Webhooks](https://api.slack.com/messaging/webhooks)
2. Create a new webhook URL for a channel in your Slack workspace
3. Copy the webhook URL into your `.env` file as:

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

Alerts will be sent when anomalies are detected or coordinated attacks are flagged.

---


## Documentation Links

- [Anthropic Claude API Tutorial – `Anthropic.API.md`](./Anthropic.API.md)
- [Project Example Walkthrough – `BitcoinTxAnomaly.example.md`](./BitcoinTxAnomaly.example.md)

---

## Final Notes and Disclaimers

- **Anthropic Claude** usage requires account creation and API key setup.
- This tutorial was developed using **free-tier limits** for all tools except Anthropic Claude.
- The `Claude` API is **not free beyond trial usage** – personal payment was made to access model responses during project development.
- AWS EMR was not used in this implementation to avoid cloud costs and ensure local reproducibility.

---