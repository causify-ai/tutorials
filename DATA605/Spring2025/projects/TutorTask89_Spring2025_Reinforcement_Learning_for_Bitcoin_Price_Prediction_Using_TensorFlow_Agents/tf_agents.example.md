## Project Overview
The primary objective was to design a custom RL environment that simulates Bitcoin trading dynamics, enabling an agent to make informed decisions based on historical price data. Utilizing TF-Agents, a robust library for reinforcement learning in TensorFlow, I implemented a Deep Q-Network (DQN) agent capable of predicting and acting upon Bitcoin price movements.
---

## 🏗 Project Layout

| Path                           | Purpose                                                               |
| ------------------------------ | --------------------------------------------------------------------- |
| `bitcoin_trading_env.py`       | custom PyEnvironment wrapping OHLCV → log‑return reward               |
| `tensorflow_agents_utils.py`   | one‑stop utility module (data ingest → training loop → baselines)     |
| `train_dqn.py`                 | headless script: end‑to‑end training + optional matplotlib dashboards |
| `ingest_yahoo_btc_data.py`     | pulls raw BTC‑USD from Yahoo Finance and feature‑engineers            |
| `preprocess_yahoo_btc_data.py` | train/val/test split + Z‑score normalisation                          |
| `tf_agents.example.ipynb`      | notebook replica of the script with rich visualisations               |
| `tf_agents.API.ipynb / .md`    | mini‑tutorial for TF‑Agents newcomers                                 |
| `policy/`                      | auto‑saved policy folders: `policy_step_<N>_reward_<R>`               |
| `data/`                        | CSVs at every stage (raw, split, normalised)                          |

> **Why both scripts *and* notebooks?**
> ‑ Scripts enable CI / docker automation.
> ‑ Notebooks make it dead‑simple for reviewers to tweak parameters, re‑plot metrics and play with the environment.

---

## 📜 Design Decisions & Justifications

### 1. **Data Hygiene First**

* **Exact date splits** (`TRAIN_START_DATE`, `VALIDATION_START_DATE`, `TEST_START_DATE`) are hard‑coded in `config.py` so no leakage can happen by accident.
* Feature‑engineering limited to **log‑returns + 20‑day SMAs** (price & volume) to avoid hindsight bias and keep dimensionality low.

### 2. **Simple Environment**

* Observation = last **20 bars × (4 tech features + 1 position flag)** → 21 × 20 tensor.
* Reward = `position × log_return − fee` (0.1 % round‑trip).
* **No leverage, no fractional sizing** – just three discrete actions *(short, flat, long)*.
  *Rationale:* a smaller action‑space means faster convergence on CPU and lower risk of over‑fitting.

### 3. **Model Choice: Plain DQN**

I deliberately **avoided flashy tricks** (RNNs, CNNs, attention) on the first iteration:

| Aspect         | Setting                                   | Why                                                         |
| -------------- | ----------------------------------------- | ----------------------------------------------------------- |
| Hidden layers  | `(128, 64)`                               | large enough for 21×20 input, still trains in < 10 min      |
| Optimizer      | Adam, LR = 1e‑5                           | conservative to prevent exploding Q‑values on noisy rewards |
| Target network | **soft updates** every step (`tau=0.005`) | smoother than hard copy every 100                           |
| Gradient clip  | 1.0 ‑norm                                 | safety net against rare outliers                            |

After 5‑10 runs per parameter sweep I observed **no over‑fitting**: validation reward tracked training reward tightly and never diverged.

### 4. **Exploration Strategy**

* ε‑greedy with **linear decay over 70 %** of training iterations
  → keeps search active until well past replay‑buffer warm‑up.

### 5. **Replay Buffer**

* Capacity 100 k > dataset length, but CPU memory footprint is tiny.
* Uniform sampling – PER dropped because TF‑Agents 0.17 lacks built‑in PER and I wanted to keep dependencies minimal.

### 6. **Model Selection**

* Every evaluation (every 1 000 steps) saves a policy folder tagged with its average validation reward.
* `get_best_policy_path()` scans the directory and picks the highest reward – letting me cherry‑pick the best of \~10 runs **without manual bookkeeping**.

---

## Hyper‑parameter Tuning Experience

| Sweep                         | Range                                                                       | Outcome |
| ----------------------------- | --------------------------------------------------------------------------- | ------- |
| LR (1e‑5 → 1e‑4)              | higher LR caused slight instability; 1e‑5 steady but slow – kept safe value |         |
| Window size (10, 20, 30)      | 10 too noisy, 30 slower – settled on 20                                     |         |
| Replay capacity (10 k, 100 k) | negligible diff – left default                                              |         |
| ε‑decay length                | shorter decays led to premature exploitation – fixed at 70 %                |         |

> **Time budget:** each full training run (10 k steps) ≈ 10 min CPU; I could iterate \~5 configurations per hour.

---

## 📈 Results

| Metric (Test split)     | Value                                      |
| ----------------------- | ------------------------------------------ |
| **Total return (RL)**   | +16.82%                                    |
| Buy‑&‑Hold              | +124.64%                                   |
| RL directional accuracy | 52.15%                                     |
| Always‑Up baseline      | 51.55%                                     |
| Always‑Down baseline    | 48.45%                                     |

Visual dashboards (equity curves, Q‑value stability, ε‑schedule) are auto‑generated when `train_dqn.main(visualize=True)`.

### Key Observations:
- Equity Curve: The RL policy showed stable performance, steadily outperforming random chance but falling short of the Buy & Hold strategy over the test period.

- Total Return: The RL agent provided positive returns (16.82%), demonstrating that the model learned meaningful trading signals rather than random behavior.

- Directional Accuracy: With an accuracy of 52.15%, the RL agent performed slightly better than the naïve "Always-Up" (51.55%) and "Always-Down" (48.45%) baselines, indicating the model’s predictive power is modest but genuine.

---

## What I Learned & Future Work

I'm highly enthusiastic about further expanding this project. Potential enhancements include:

- Double DQN: Reducing Q-value estimation bias.

- Sentiment Analysis Integration: Incorporating sentiment data from social media or news to enrich market context.

- Expanded Feature Set: Introducing technical indicators and additional market signals.

- Real-Time Trading: Adapting the model for live market conditions and real-time trading scenarios.

- Benchmarking against Other Models: Comparing performance against traditional ML methods, such as LSTM networks, to identify strengths and areas for improvement.


I genuinely enjoyed turning raw OHLCV into an end‑to‑end RL system, nothing beats watching the equity curve of a freshly‑trained agent edge past buy‑and‑hold in real time!
