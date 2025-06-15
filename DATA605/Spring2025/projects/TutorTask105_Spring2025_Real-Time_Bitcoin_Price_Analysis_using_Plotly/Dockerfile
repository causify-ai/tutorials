# ------------------------------------------------------------------------------
# Dockerfile: bitcoin.forecasting.plotly.py
#
# 1. Uses a slim, stable Python image based on Debian Bullseye.
# 2. Installs project dependencies listed in requirements.txt.
# 3. Copies the entire project codebase into the Docker container.
# 4. Launches the BTC price forecasting script with LSTM and Plotly.
#
# References:
# - Kraken API: https://docs.kraken.com/rest/
# - TensorFlow LSTM: https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM
# - Coding Standards: https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
# ------------------------------------------------------------------------------

# Use a stable, minimal Python image
FROM python:3.11-slim-bullseye

# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entire source code
COPY . .

# Run the BTC forecasting script
CMD ["python", "btc_forecast.py"]
