# Real-Time Bitcoin Price Trend Analysis using Stable-Baselines3

This project applies reinforcement learning (RL) using Stable-Baselines3 to predict and act on Bitcoin price movements. By training an agent on real-time and historical data, it simulates an automated crypto trader making buy/sell/hold decisions.

---

## Project Highlights

- Live BTC data from CoinGecko API
- Custom Gymnasium environment for trading simulation
- PPO model training with Stable-Baselines3
- End-to-end RL pipeline with analytics, visualizations, and predictions

---

## Tech Stack

| Tool | Role |
|------|------|
| Stable-Baselines3 | Reinforcement learning algorithms |
| Gymnasium | Custom RL environment design |
| CoinGecko API | Fetch live and historical BTC prices |
| Pandas / NumPy / Matplotlib | Data manipulation and visualization |
| Jupyter Notebooks | Development and experimentation |

---


## File Structure

- `stablebaseline3_utils.py`  
  Contains reusable utility functions and the custom Gymnasium environment for trading simulation.

- `stablebaseline3.API.ipynb`  
  Demonstrates how to use the raw CoinGecko API and the wrapper functions for fetching live and historical Bitcoin prices. Also includes normalization and plotting.

- `stablebaseline3.API.md`  
  Documents the native API, wrapper layer, and explains the rationale behind each utility function.

- `stablebaseline3.example.ipynb`  
  Full end-to-end training and evaluation notebook. Includes PPO training, performance evaluation, action logging, visualizations, and a simulated prediction step.

- `stablebaseline3.example.md`  
  Project narrative with design choices, model observations, challenges, and future enhancement opportunities.

- `bitcoin_historical.csv`  
  30-day hourly BTC price dataset, normalized and used for training and evaluation.

- `ppo_bitcoin_trading.zip`  
  Saved PPO model trained on historical BTC data using Stable-Baselines3.

- `README.md`  
  Project summary, installation guide, file structure, and execution instructions.
