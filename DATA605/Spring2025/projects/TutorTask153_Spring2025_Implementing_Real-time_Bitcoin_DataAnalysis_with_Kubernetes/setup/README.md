# Bitcoin Data Processing on Kubernetes with PostgreSQL

This project sets up a Kubernetes deployment that fetches Bitcoin price data in real-time and stores it in a PostgreSQL database.

## Prerequisites

- Docker
- Minikube or a Kubernetes cluster
- kubectl configured to work with your cluster

## Setup Instructions

1. Clone this repository:
   ```
   git clone <repository-url>
   cd bitcoin-k8s-project
   ```

2. Run the setup script:
   ```
   chmod +x setup/minikube-setup.sh
   ./setup/minikube-setup.sh
   ```

3. Check that the pods are running:
   ```
   kubectl get pods
   ```

## Accessing the Data

### PostgreSQL Database

To access the PostgreSQL database directly:

```bash
# Get the pod name
POSTGRES_POD=$(kubectl get pods -l app=postgres -o jsonpath="{.items[0].metadata.name}")

# Connect to PostgreSQL
kubectl exec -it $POSTGRES_POD -- psql -U postgres -d bitcoin_data

# Once in psql, you can run queries
bitcoin_data=# SELECT * FROM bitcoin_data ORDER BY timestamp DESC LIMIT 10;
```

### Generated Charts

To access the generated charts:

```bash
# Get the bitcoin-fetcher pod name
FETCHER_POD=$(kubectl get pods -l app=bitcoin-fetcher -o jsonpath="{.items[0].metadata.name}")

# Copy charts to local machine
kubectl cp $FETCHER_POD:/data/charts ./local_charts
```

## Monitoring the Application

To monitor the application logs:

```bash
kubectl logs -f deployment/bitcoin-fetcher
```

## Database Schema

The Bitcoin data is stored in a table with the following schema:

- `id`: Serial primary key
- `timestamp`: The time the data was recorded
- `price_usd`: Bitcoin price in USD
- `market_cap_usd`: Market cap in USD
- `volume_24h_usd`: 24-hour trading volume in USD
- `price_change_24h`: 24-hour price change percentage
