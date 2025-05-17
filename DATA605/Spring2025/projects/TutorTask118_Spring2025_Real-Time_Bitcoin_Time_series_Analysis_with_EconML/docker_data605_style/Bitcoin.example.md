# Bitcoin Time Series Causal Analysis – Example Use Case

## Objective

This notebook demonstrates a practical example of using the custom API built in `Bitcoin.API.ipynb` and `bitcoin_utils.py` to estimate the causal impact of a trend signal on Bitcoin price movements using multiple EconML models.

---

## Dataset & Preparation

- Real-time Bitcoin price data was retrieved from the CoinGecko API.
- Trend features were engineered using rolling averages and normalized using `StandardScaler`.
- Price changes were computed as percentage returns.

---

## Models Applied

Three causal estimation models were tested:

1. **LinearDML** – Combines outcome and treatment models using LassoCV and RandomForest.
2. **DRLearner** – Doubly robust estimator for more stable inference under model misspecification.
3. **CausalForestDML** – Flexible non-parametric causal forest for heterogeneous treatment effects.

All models used:
- Outcome model: `RandomForestRegressor(n_estimators=100)`
- Treatment model: `LassoCV(cv=5)`

---

## Results

- **Estimated causal effects** were visualized across time.
- A clear divergence was observed between models, with DRLearner being more volatile.
- Final plots compared LinearDML and DRLearner, showing overlapping trends with differing confidence bands.

---

## Interpretation

- Trend signals had a **positive average causal effect** on returns, especially during market volatility.
- **LinearDML** provided smoother and more interpretable causal trends.
- **DRLearner** captured abrupt regime changes but introduced variance.
- Use of multiple models gives a broader picture of causal dynamics in financial time series.

---

## Project Structure Used

bitcoin_utils.py # Contains all model wrappers and data functions
Bitcoin.API.ipynb # Demonstrates API usage for dataset preparation and model execution
Bitcoin.example.ipynb # Applies models and visualizes outcomes with plots
Bitcoin.example.md # This file – explains methodology and outcome



