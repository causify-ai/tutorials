# Bitcoin RDS - Real-Time Bitcoin Data Processing using Amazon RDS

This project demonstrates real-time Bitcoin price data processing using Amazon RDS for storage and analysis.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- An Amazon RDS PostgreSQL database instance

## System Architecture

### System Components

```mermaid
graph TD
    A[CoinGecko API] -->|Bitcoin Price Data| B[Python Application]
    B -->|Store Data| C[(Amazon RDS PostgreSQL)]
    B -->|Analyze Data| B
    C -->|Retrieve Data| D[Streamlit Dashboard]
    C -->|Query Data| E[Jupyter Notebooks]
    
    class A,C external
    class B,D,E internal
```

### Data Processing Flow

```mermaid
flowchart LR
    A[Fetch Data\nfrom CoinGecko] --> B[Process &\nValidate Data]
    B --> C{Store Data}
    C -->|Raw Data| D[(raw_bitcoin_prices)]
    C -->|Aggregated Data| E[(hourly_bitcoin_prices)]
    D --> F[Time Series\nAnalysis]
    E --> F
    F --> G[Visualization\n& Dashboard]
```

### Database Relationship

```mermaid
erDiagram
    raw_bitcoin_prices ||--o{ hourly_bitcoin_prices : aggregates
    
    raw_bitcoin_prices {
        serial id PK
        timestamp timestamp
        numeric price_usd
        numeric volume_usd
        numeric market_cap_usd
        timestamp created_at
    }
    
    hourly_bitcoin_prices {
        timestamp timestamp PK
        numeric open_price_usd
        numeric high_price_usd
        numeric low_price_usd
        numeric close_price_usd
        numeric volume_usd
        timestamp created_at
    }
```

## Database Schema

The project uses two primary tables in the PostgreSQL database:

### 1. raw_bitcoin_prices

Stores raw Bitcoin price data fetched from CoinGecko API.

| Column         | Type           | Description                                |
|----------------|----------------|--------------------------------------------|
| id             | SERIAL         | Primary key                                |
| timestamp      | TIMESTAMP      | Time when the price data was recorded      |
| price_usd      | NUMERIC(20,8)  | Bitcoin price in USD                       |
| volume_usd     | NUMERIC(24,2)  | Trading volume in USD                      |
| market_cap_usd | NUMERIC(24,2)  | Market capitalization in USD               |
| created_at     | TIMESTAMP      | Record creation timestamp (auto-generated) |

**Indexes**:
- `idx_raw_bitcoin_prices_timestamp` on the timestamp column for efficient time-based queries

### 2. hourly_bitcoin_prices

Stores aggregated hourly Bitcoin price data derived from raw data.

| Column         | Type           | Description                                |
|----------------|----------------|--------------------------------------------|
| timestamp      | TIMESTAMP      | Hour timestamp (PRIMARY KEY)               |
| open_price_usd | NUMERIC(20,8)  | Opening price for the hour                 |
| high_price_usd | NUMERIC(20,8)  | Highest price during the hour              |
| low_price_usd  | NUMERIC(20,8)  | Lowest price during the hour               |
| close_price_usd| NUMERIC(20,8)  | Closing price for the hour                 |
| volume_usd     | NUMERIC(24,2)  | Average trading volume during the hour     |
| created_at     | TIMESTAMP      | Record creation timestamp (auto-generated) |

**Indexes**:
- Primary key on `timestamp` 
- `idx_hourly_bitcoin_prices_close` on the close_price_usd column

## First-Time Setup

1. **Clone the repository**:
   ```
   git clone repository-url
   cd bitcoin-rds-project  # Navigate to the project directory
   ```

2. **Create `.env` file**:
   Create a `.env` file in the project root, then copy and paste the following content with your own RDS concredentials:
   ```
   RDS_HOST=your-database-host.region.rds.amazonaws.com
   RDS_PORT=5432
   RDS_DATABASE=bitcoin_db
   RDS_USER=your_username
   RDS_PASSWORD=your_password
   ```

3. **Build Docker images**:
   ```
   cd docker_data605_style
   ./docker_build.sh        # Builds the main Docker image
   ./docker_build_streamlit.sh  # Builds the Streamlit Docker image
   ```

## Running the Project

You have several options for running the project:

### Option 1: Run both Jupyter and Streamlit together (recommended)
```
cd docker_data605_style
./docker_start_all.sh
```
Then access:
- Jupyter at http://localhost:8888
- Streamlit at http://localhost:8080

### Option 2: Run Jupyter only
```
cd docker_data605_style
./docker_jupyter.sh
```
Access Jupyter at http://localhost:8888

### Option 3: Run Streamlit only
```
cd docker_data605_style
./docker_streamlit.sh
```
Access Streamlit at http://localhost:8080

## Usage

1. **Jupyter notebooks**:
   - `bitcoin_rds.API.ipynb`: API documentation and examples to describe the native API of RDS and CoinGecko
   - `bitcoin_rds.example.ipynb`: Complete usage example

2. **Streamlit dashboard**:
   - Real-time Bitcoin price visualization
   - Historical data analysis with RSI indicator
   - Database connection and management

## Project Structure

- `bitcoin_rds_utils.py`: Core utilities for Bitcoin data processing and RDS connections
- `bitcoin_dashboard.py`: Streamlit dashboard implementation
- `docker_data605_style/`: Docker configuration files for containerization
- `bitcoin_rds.API.md`: A description of the native API of RDS and CoinGecko
- `bitcoin_rds.example.md`: A markdown description of the project
- `README.md`: This file

## Troubleshooting

- **Database connection issues**: Verify your RDS credentials in the `.env` file
- **Docker build failures**: Ensure Docker is properly installed and running
- **Port conflicts**: If ports 8888 or 8080 are in use, modify the port settings in the Docker scripts
