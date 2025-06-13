# Real-Time Bitcoin Data Processing using cuDF

This project demonstrates GPU-accelerated data processing and analysis of Bitcoin price data using cuDF, a GPU DataFrame library from the RAPIDS AI ecosystem.

## Project Overview

This project implements a real-time data processing pipeline for Bitcoin price data that leverages GPU computing to perform fast data manipulation and analysis. Key features include:

- Real-time data ingestion from CoinGecko API
- GPU-accelerated data processing with cuDF
- Time series analysis to compute technical indicators like moving averages, volatility, and RSI
- Interactive visualization of Bitcoin price trends and technical indicators
- Performance comparison between CPU (pandas) and GPU (cuDF) processing
- 30-day Bitcoin price forecasting with confidence intervals

## Requirements

- Python 3.8+
- NVIDIA GPU with CUDA support (for GPU acceleration)
- Docker (optional, for containerized execution)
- CoinGecko API key (optional, for higher rate limits)

## Installation

### Option 1: Local Installation

=======
1. Clone the repository:
```bash
git clone https://github.com/causify-ai/tutorials/tree/TutorTask154_Spring2025_Real-Time_Bitcoin_Data_Processing_using_cuDF/DATA605/Spring2025/projects/TutorTask154_Spring2025_Real-Time_Bitcoin_Data_Processing_using_cuDF
cd TutorTask154_Spring2025_Real-Time_Bitcoin_Data_Processing_using_cuDF
```

2. Create a conda environment with RAPIDS:
```bash
conda create -n bitcoin-cudf -c rapidsai -c conda-forge -c nvidia \
    rapids=24.04 python=3.10 cuda-version=12.0
```

3. Activate the environment:
```bash
conda activate bitcoin-cudf
```

4. Install additional dependencies:
```bash
pip install -r requirements.txt
```

5. Configure API key (optional):
   - Create a `.env` file in the root directory
   - Add your CoinGecko API key: `COINGECKO_API_KEY=your_api_key_here`

### Option 2: Using Docker (Recommended for Compatibility)

## API Key Setup

This project uses the CoinGecko API for fetching Bitcoin price data. While the API can be used without an API key, using one provides higher rate limits.

### Getting a CoinGecko API Key

1. Go to [CoinGecko](https://www.coingecko.com/)
2. Create a free account
3. Navigate to your dashboard and select "API Keys"
4. Create a new API key

### Setting Up Your API Key

1. Create a `.env` file in the root directory of the project
2. Add your API key in the following format:
```
COINGECKO_API_KEY=your_api_key_here
```

Build and run the Docker container:

1. docker build -t cudf-bitcoin-data-processing .
2. docker run --gpus all -p 8888:8888 --env-file .env cudf-bitcoin-data-processing 

## Project Structure

- `utils/`: Python source code
  - `cudf_utils.py`: Utility functions for Bitcoin data processing with cuDF
  - `bitcoin_realtime_processor.py`: Script for processing historical and real-time data
  - `bitcoin_realtime_demo.py`: User-friendly interactive demo script
- `notebook/`: Jupyter notebooks for interactive analysis
  - `cudf.API.ipynb`: Documentation and examples of cuDF API usage
  - `cudf.API.md`: Comprehensive markdown documentation of the cuDF API
  - `cudf.example.ipynb`: End-to-end Bitcoin data processing example notebook
  - `cudf.example.md`: Markdown documentation for the example notebook
  - `performance_comparison.ipynb`: Comparative analysis of cuDF vs pandas performance
  - `performance_comparison.md`: Markdown documentation of performance benchmarking methodology
- Docker configuration files:
  - `Dockerfile`: Container definition
  - `docker_build.sh`: Script to build the Docker image
  - `docker_bash.sh`: Script to run an interactive bash shell in the container
  - `docker_exec.sh`: Script to execute commands in the container
  - `docker_clean.sh`: Script to clean up Docker resources
  - `docker_push.sh`: Script to push the Docker image to a registry
- Configuration files:
  - `requirements.txt`: Python package dependencies
  - `.env`: Environment variables including API keys (you need to create this)
  - `.gitignore`: Git ignore patterns
  - `run_jupyter.sh`: Script to launch Jupyter notebook server
  - `install_jupyter_extensions.sh`: Script to install Jupyter extensions

## Usage

### Running the Interactive Demo

The easiest way to get started is to run the interactive demo script:

```bash
python utils/bitcoin_realtime_demo.py
```

This will guide you through the process of:
1. Choosing between historical, real-time, or combined analysis
2. Setting parameters for data collection
3. Visualizing the results
4. Saving the data to CSV files

### Running the Jupyter Notebooks

For performance comparison between cuDF and pandas:
```bash
jupyter notebook notebook/performance_comparison.ipynb
```

For cuDF API documentation and examples:
```bash
jupyter notebook notebook/cudf.API.ipynb
```

### Using the Command-Line Processor

For more advanced usage, you can use the command-line processor:

```bash
# Historical analysis (1 year of data)
python utils/bitcoin_realtime_processor.py --mode historical --days 365

# Real-time analysis (30 points with 5 second intervals)
python utils/bitcoin_realtime_processor.py --mode realtime --interval 5 --points 30

# Combined analysis
python utils/bitcoin_realtime_processor.py --mode both --days 365 --interval 5 --points 10

# Save output to a specific file
python utils/bitcoin_realtime_processor.py --mode both --output my_bitcoin_data.csv

# Run without plotting (for headless environments)
python utils/bitcoin_realtime_processor.py --mode historical --no-plot
```

## Technical Indicators

This project calculates the following technical indicators for Bitcoin price data:

1. **Simple Moving Averages (SMA)**: Calculates average prices over different time windows to identify trends
2. **Volatility**: Standard deviation of price over a rolling window
3. **Rate of Change (ROC)**: Percentage change in price over different periods
4. **Relative Strength Index (RSI)**: Momentum oscillator that measures the speed and change of price movements

## Price Forecasting

The project includes functionality to forecast Bitcoin prices for the next 30 days:

1. **Machine Learning Approach**: Uses historical data to train a model that predicts future prices
2. **Feature Engineering**: Leverages technical indicators like moving averages and volatility as predictive features
3. **Confidence Intervals**: Provides 95% confidence bounds for the forecasted prices
4. **Visual Presentation**: Plots the forecast alongside historical data for easy interpretation

## Performance Benefits of cuDF

The GPU-accelerated cuDF library provides significant performance improvements compared to CPU-based pandas for large datasets:

- **Data Loading**: 2-5x faster loading of large CSV/Parquet files
- **Aggregations**: 10-100x faster group-by operations
- **Filtering**: 5-20x faster complex filtering operations
- **Technical Indicators**: 3-10x faster calculation of rolling statistics

## Docker Support

This project includes Docker configuration for easy deployment:

1. Build the Docker image:
```bash
./docker_build.sh
```

2. Run the container with GPU support:
```bash
./docker_bash.sh
```

3. For other Docker operations:
```bash
# Execute a command in the container
./docker_exec.sh <command>

# Clean up Docker resources
./docker_clean.sh

# Push the Docker image to a registry
./docker_push.sh
```

## License

This project is released under the MIT License.

## Acknowledgments

- RAPIDS cuDF: https://docs.rapids.ai/api/cudf/stable/
- CoinGecko API: https://www.coingecko.com/en/api/documentation
>>>>>>> 14e5b93d1 (completed)
