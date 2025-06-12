<!-- toc -->

- [BTC Transformer Prediction API Tutorial](#btc-transformer-prediction-api-tutorial)
  - [General Guidelines](#general-guidelines)
  - [API Overview](#api-overview)
  - [Key Components](#key-components)
    - [Model Architecture](#model-architecture)
    - [Data Preprocessing](#data-preprocessing)
    - [Prediction Pipeline](#prediction-pipeline)
    - [Streamlit UI](#streamlit-ui)
  - [Usage](#usage)
  - [References](#references)

## General Guidelines

- Follow the instructions in `README.md` on writing API tutorials.
- This document explores the real-time Bitcoin prediction API implemented in `btc.API.py`.
- The file should be named `btc.API.md`.

## API Overview

This API uses a Transformer-based PyTorch model to forecast future Bitcoin prices based on minute-level historical data, technical indicators, and market volume.

- Input: Past 30 minutes of BTC/USD data with technical features
- Output: Next 1–30 minutes of predicted BTC prices
- Served via Streamlit dashboard with real-time auto-refresh

## Key Components

### Model Architecture

Implemented in `MultiStepTransformer`:

- Linear input projection
- Multi-layer Transformer encoder (`nn.TransformerEncoder`)
- Linear decoder
- Output: sequence of future price deltas, inverse-scaled to price range

### Data Preprocessing

Handled in `get_latest_btc_data()`:

- Uses CryptoCompare API
- Extracts `Close`, `Volume`
- Computes `log_return`, 5-min MA, and 14-period RSI

### Prediction Pipeline

- Scales features with `StandardScaler`
- Performs inference with Transformer model
- Applies inverse scaling and clipping to stabilize predictions
- Outputs a list of `n` future price estimates

### Streamlit UI

- Forecast horizon slider (1–30 minutes)
- Real-time metric comparison (Actual vs Predicted)
- Altair line chart with historical and forecasted prices
- CSV download for forecast data

## Usage

```bash
streamlit run btc.API.py
```

Make sure the following files exist:

- `utils/saved_models/30step_transformer.pth`
- `utils/saved_models/30step_scaler.pkl`
- `.env` with `CRYPTO_COMPARE_API_KEY`

## References

- Vaswani et al., “Attention is All You Need”, [arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- [PyTorch Transformers](https://pytorch.org/docs/stable/generated/torch.nn.TransformerEncoder.html)
- [CryptoCompare API](https://min-api.cryptocompare.com)
- [Streamlit Docs](https://docs.streamlit.io/)
- [TA-Lib for Python](https://technical-analysis-library-in-python.readthedocs.io/)
