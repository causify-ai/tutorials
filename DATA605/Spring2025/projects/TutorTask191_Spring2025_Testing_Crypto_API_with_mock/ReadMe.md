# Real-Time Bitcoin Causal Analysis with DoWhy

This project demonstrates a real-time cryptocurrency price alert system using the Bitcoin price fetched from the CoinGecko API. We then apply basic threshold-based logic to trigger alerts and validate functionality using `unittest.mock`.

## Components

- `DoWhy_API.py`: Contains functions to fetch the BTC price, check thresholds, send alerts, and combine them with `fetch_and_alert`.
- `test_mock.py`: Unit tests for `fetch_and_alert`, using mocked API responses via `unittest.mock`.
- `Mock.API.ipynb`: A notebook demonstrating how to call and use the functions in `DoWhy_API.py`.
- `Mock.example.ipynb`: A notebook simulating realistic example usage with mocked price scenarios.

## Goal

To practice mocking external APIs and writing unit tests for real-time applications without relying on live data.
