# BigDL Example — End-to-End Bitcoin Price Forecasting  
*DATA605 • Spring 2025 • TutorTask300*

This example walks through a **complete ML workflow** on top of the thin API layer exposed in `bitcoin_api.py` and the utility helpers in `template_utils.py`.  
After ~5 minutes you should have:

1. A local Spark 3 session running inside the course Docker image (`bigdl-bitcoin:latest`).
2. 30 days of intraday BTC-USD prices ingested, cleaned & feature-engineered.
3. An LSTM model trained in **BigDL DLlib** (distributed on Spark) to predict 10 future timesteps.
4. A set of visual diagnostics & error metrics, including:
   - Actual vs. Forecast line plot  
   - Residual histogram  
   - Rolling‐MAPE & RMSE trend  
   - Autocorrelation (ACF) of residuals

---

## 1 · Environment Setup

```bash
# build & enter the container (one-off)
bash docker_build.sh
winpty docker run -it --rm -p 8888:8888 -v "$PWD":/app bigdl-bitcoin:latest bash

# inside the container – start Jupyter (optional)
jupyter lab --ip=0.0.0.0 --no-browser --NotebookApp.token='' --allow-root
```

2 · Notebook Flow (BigDL_example.ipynb)
Step	Cell Label	What Happens	Key Function
A	ETL pipeline	Ingest ➜ Clean ➜ Transform ➜ Persist to ./output/bitcoin/	etl_pipeline()
B	Train LSTM	Builds a Sequential network → trains 5 epochs with Adam	train_rnn_model()
C	Forecast	Autoregressive loop predicting 10 future minutes	predict_future()
D	Visual 1	Line chart – Actual vs. Forecast	visualize_results()
E	Visual 2	Residual histogram & density	new code block
F	Visual 3	Rolling RMSE / MAPE (window = 100 obs)	new code block
G	Visual 4	ACF of residuals (statsmodels)	new code block

3 · Key Results
Metric	Value (run ✱)	Notes
RMSE	≈ $ 1 345	10-step horizon, test window = last 20 %
MAPE	1.32 %	Stable for quiet regimes; spikes during high volatility
R²	0.87	Captures direction but smooths extreme jumps

✱ Numbers shown are indicative; rerun will vary depending on random seed and the latest BTC prices.

4 · Additional Plots
mermaid
Copy
Edit
graph LR
    subgraph Diagnostics
        A[Actual vs Forecast] -->|eye-check| B[Residual Histogram]
        B --> C[Rolling RMSE/MAPE]
        C --> D[Residuals ACF]
    end
All four plots are produced in the second half of the notebook.
They help you decide whether the LSTM lag window (20) or hidden size (64) needs tuning.

5 · Next Steps / Extensions
Hyper-opt via BigDL’s integrated Ray Tune wrapper — grid over hidden_size, time_steps, lr.

Switch to GRU or TCN (BigDL nn.layer.TemporalConvNet) for potentially better long-range memory.

Stream live data every minute using spark.readStream and update predictions in near-real-time.

Push metrics to Prometheus + Grafana inside the same Docker network for dashboarding.

6 · References 📚
BigDL DLlib Docs: https://bigdl.readthedocs.io/en/latest/doc/DLlib/

CoinGecko API: https://www.coingecko.com/en/api

Pandas + Spark toPandas Warning: https://stackoverflow.com/questions/52344044

Course Template Guidelines: DATA605/tutorial_template/*

Maintained by Krishnendra Singh Tomar (UID 121335364)


