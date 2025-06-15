# Bitcoin Price Dashboard Web Application

This web application provides a modern JavaScript/HTML-based dashboard for monitoring Bitcoin prices and predictions in real-time. It replaces the previous Streamlit-based dashboard with a more efficient and customizable solution.

## Architecture

The application consists of two main components:

1. **Backend API (Flask)**: Serves the data from CSV files and provides REST API endpoints for the frontend.
2. **Frontend (HTML/JS/CSS)**: A responsive web interface using Plotly.js for interactive charts.

### API Endpoints

- `/api/price-data`: Returns the latest Bitcoin price data
- `/api/prediction-data`: Returns the latest price predictions
- `/api/metrics-data`: Returns the latest prediction metrics and error data

## Features

- Real-time price monitoring with candlestick charts
- Prediction visualization with confidence intervals
- Error metrics tracking and distribution analysis
- Responsive design that works on desktop and mobile devices
- Cold start mode for handling limited data scenarios
- Configurable time windows and refresh intervals

## Running the Application

### Using Docker Compose

The easiest way to run the application is using Docker Compose:

```bash
cd docker_causify_style
docker-compose up -d web-app
```

The dashboard will be available at http://localhost:5000

### Running Locally

To run the application locally:

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend:
   ```bash
   python backend/app.py
   ```

3. Open your browser and navigate to http://localhost:5000

## Configuration

The application is configured through the `config.yaml` file in the `configs` directory. Key configuration options include:

- `refresh_interval`: How often to refresh the data (in seconds)
- `time_window_minutes`: Default time window to display (in minutes)
- `cold_start`: Settings for handling limited data scenarios
- `colors`: Color scheme for the charts

## Development

To modify the frontend:
- Edit the HTML/CSS/JavaScript in the `frontend/index.html` file

To modify the backend:
- Edit the Flask application in `backend/app.py` 