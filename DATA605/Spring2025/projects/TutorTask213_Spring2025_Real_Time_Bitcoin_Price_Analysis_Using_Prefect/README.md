

---
# ⚙️ Real-time Bitcoin Price ETL with Prefect

> **Course**: DATA605 – Spring 2025  
> **Project Title**: Real-time Bitcoin Price ETL with Prefect  
> **Student**: Sahithi Vankayala  
> **Difficulty**: 3

---

## 🚀 Objective

This project demonstrates how to use **Prefect 2.0** to orchestrate a real-time ETL pipeline that fetches live Bitcoin price data from the **CoinGecko API**, stores it in a **PostgreSQL database (Docker)**, generates visualizations, and triggers email alerts on significant price changes.

The flow is scheduled to run **every 5 minutes** using **Prefect’s deployment API**.

---

## 🛠 Tech Stack

| Component       | Description |
|----------------|-------------|
| **Prefect**     | Workflow orchestration & scheduling |
| **CoinGecko API** | Real-time Bitcoin price feed |
| **PostgreSQL**  | Relational database (Docker container) |
| **SQLAlchemy**  | ORM to store price data |
| **Matplotlib**  | Visualization of price trends |
| **Email (via Gmail + App Password)**     | Alerts |
| **Docker**      | Running PostgreSQL container |
| **Python (.env)** | Securing credentials |

---

### 📊 Architecture Diagram

```
                   +-------------------------+
                   |     CoinGecko API       |
                   +------------+------------+
                                |
                      Fetches Bitcoin price
                                |
                   +------------v------------+
                   |      Prefect ETL Flow   |
                   |-------------------------|
                   | 1. Fetch & validate data|
                   | 2. Save to PostgreSQL   |
                   | 3. Visualize trend      |
                   | 4. Detect price changes |
                   | 5. Send email alerts    |
                   +------------+------------+
                                |
        +-----------------------+------------------------+
        |                                                |
+-------v--------+                             +---------v---------+
| PostgreSQL DB  |                             |  Email Alerts     |
| (Dockerized)   |                             |  via SMTP (Gmail) |
+----------------+                             +-------------------+
```

---

### 📂 Project Structure

```
605_Project/
│
├── prefect_main.py           # 🔁 The main Prefect flow script
│                             #    - Defines tasks and the ETL flow
│                             #    - Schedules every 5 minutes
│                             #    - Handles fetching, saving, alerting, and visualizing
│
├── plot_price_trend.py       # 📊 Separate script to plot Bitcoin price trend (manual)
│                             #    - Connects to PostgreSQL
│                             #    - Plots last 20 entries using matplotlib
│
├── .env                      # 🔐 Environment variables (DO NOT push to GitHub)
│                             #    - POSTGRES_URL
│                             #    - ALERT_EMAIL (Gmail address)
│                             #    - EMAIL_APP_PASSWORD (Gmail app password)
│
├── requirements.txt          # 📦 Python dependencies for the project
│
├── Dockerfile (optional)     # 🐳 Dockerfile to run everything in a containerized environment
│                             #    - Not required unless deploying fully containerized
│
├── README.md                 # 📘 Project documentation (architecture, setup, usage)
│
└── prefect/
    └── prefect.db            # 📁 Prefect server metadata (if you're using local server)

```

---

## 🛠️ How It Works

### ✅ ETL Flow Tasks
### 1. Fetch Real-Time Data

   * Query CoinGecko's API every 5 minutes for the latest Bitcoin price.

### 2. Validate Data

   * Ensure data includes a valid numeric price.

### 3. Save to PostgreSQL

   * Append timestamped price data to a PostgreSQL table.

### 4. Create Prefect Artifacts

   * Automatically generate markdown and image artifacts for each run.

### 5. Visualize Trends

   * Fetch last 20 entries and render a line chart of Bitcoin prices.

### 6. Alert on Spike/Drop

   * Detect >5% price change and trigger email alerts using Gmail App Passwords.


## ⚡ How to Run

### 1. 🚢 Start PostgreSQL in Docker

```bash
docker run --name bitcoin-postgres \
  -e POSTGRES_USER=sahithivankayala \
  -e POSTGRES_PASSWORD=sahithi2024 \
  -e POSTGRES_DB=bitcoin_etl \
  -p 5432:5432 -d postgres
````

---

### 2. 🔐 Setup `.env` File

Create a `.env` file:

```env
POSTGRES_URL=postgresql://sahithivankayala:sahithi2024@localhost:5432/bitcoin_etl
ALERT_EMAIL=sahithiv@umd.edu
EMAIL_APP_PASSWORD=hcysipwlwlgtuxpv 
```

---

### 3. ✅ Install Requirements

```bash
pip install -r requirements.txt
```

---

### 4. 🌐 Start Prefect Server and Worker

```bash
prefect server start
# in new terminal
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
prefect worker start --pool default-agent-pool
```

---

### 5. ▶️ Run the Flow

```bash
python prefect_main.py
```

This will:

* Schedule the flow every 5 minutes
* Automatically fetch Bitcoin prices
* Store them in PostgreSQL
* Create markdown + image artifacts
* Send email alerts for spikes/drops

---

## 🧪 Sample Visualization Output

Run the following to see latest 20 data points as a line graph:

```bash
python plot_price_trend.py
```

---

## 📬 Email Alert Behavior

* If price increases or decreases by **more than 5%**, an email alert is triggered.
* Alerts are sent using Gmail SMTP and app-specific passwords.

---

## ✅ Outputs

* ✅ Bitcoin price log (Markdown artifact)
* ✅ Price trend chart (Artifact with base64 image)
* ✅ PostgreSQL `prices` table (Docker)
* ✅ Email notifications on significant changes
* ✅ Scheduled execution every 5 minutes


---
## 📚 Learn More

* [Prefect Docs](https://docs.prefect.io/)
* [CoinGecko API](https://www.coingecko.com/en/api)
* [Docker Hub: Postgres](https://hub.docker.com/_/postgres)
* [SQLAlchemy](https://www.sqlalchemy.org/)


