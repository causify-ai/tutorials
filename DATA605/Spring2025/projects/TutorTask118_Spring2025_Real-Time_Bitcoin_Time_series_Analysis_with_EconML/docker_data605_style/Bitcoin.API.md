# Bitcoin Causal Inference API Documentation

## Overview

This file documents the API developed in `bitcoin_utils.py`, which supports causal inference over Bitcoin time series data using Microsoft’s EconML.

## Modules & Functions

### 1. `prepare_dataset()`
- Merges price and trend signals.
- Computes percent price change.
- Scales input features.
- Returns a clean DataFrame.

### 2. `train_dml_model(df)`
- Trains a LinearDML estimator.
- Returns causal effects and the fitted model.

### 3. `train_dr_model(df)`
- Uses a DRLearner for doubly robust estimation.
- Returns treatment effect estimates.

### 4. `train_cf_model(df)`
- CausalForestDML for non-parametric estimation.
- Best for heterogeneous treatment effects.

### 5. `plot_effects(df, effect)`
- Visualizes the causal effect over time.

### 6. `plot_comparison(df, effect1, effect2)`
- Plots side-by-side estimates (e.g., LinearDML vs DRLearner).

## Design Notes

- Modular functions allow easy reuse across notebooks.
- All learners follow EconML-compatible structure.
- Uses `RandomForestRegressor` and `LassoCV` by default for robustness.

## Usage Example

```python
from bitcoin_utils import prepare_dataset, train_dml_model, plot_effects

df = prepare_dataset()
effect, model = train_dml_model(df)
plot_effects(df, effect)

