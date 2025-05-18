# stablebaseline3.example.md

## 🧠 Project Summary

This notebook presents an end-to-end reinforcement learning (RL) application for forecasting Bitcoin price trends using real-time and historical data.

We use Stable-Baselines3’s PPO (Proximal Policy Optimization) algorithm and a custom trading environment built with Gymnasium. The model is trained on a 30-day hourly time series of Bitcoin prices and evaluated for profitability and action strategy.

---

## Workflow Overview

### 1. Data Loading
The dataset `bitcoin_historical.csv` is generated using the CoinGecko API and contains 30 days of hourly BTC prices.

### 2. Environment Setup
We use a custom `BitcoinTradingEnv` environment from `stablebaseline3_utils.py` that:
- Models buy/sell/hold trading decisions
- Rewards profit made after a sell
- Tracks portfolio value and profit

### 3. RL Model Training
We train a PPO agent using:
- `MlpPolicy`
- `total_timesteps=10000`

Training shows improving `ep_rew_mean` with time, indicating learning.

### 4. Evaluation
- The agent is evaluated in a fresh environment
- Cumulative profit is tracked and visualized
- Buy/Sell actions are plotted over price trend

---

## Observations

- PPO effectively learns a basic trading pattern within limited timesteps
- Model rewards spike when profitable sell actions occur
- Agent tends to hold when uncertain (no penalty for inactivity)

---

## Limitations & Improvements

### Current limitations:
- No transaction fees
- No technical indicators (e.g., RSI, MA)
- Single-agent and single-asset focus

### Possible improvements:
- Add time-based penalties
- Use additional features like moving averages, volume
- Compare PPO vs DQN

---

## Files Produced
- `ppo_bitcoin_trading.zip`: Trained PPO model
- `bitcoin_historical.csv`: Normalized price dataset
- `stablebaseline3_utils.py`: Utility functions and environment
- `stablebaseline3.example.ipynb`: Model training and evaluation

---

## Conclusion

This project demonstrates how to apply reinforcement learning to a real-world financial problem using open-source tools. It combines real-time data access, a custom trading simulation, and powerful learning algorithms — providing a solid foundation for future crypto trading bots.
