
<!-- toc -->

•⁠  ⁠[Project Description](#project-description)  
  * [Table of Contents](#table-of-contents)  
    + [Hierarchy](#hierarchy)  
  * [General Guidelines](#general-guidelines)

<!-- tocstop -->

# Real-time Bitcoin Price Analysis Using PyMC3

•⁠  ⁠E.g., Building a probabilistic forecasting system to predict Bitcoin price trends using ⁠ PyMC3 ⁠ via both Gaussian Random Walk and Bayesian ARIMA models

## Table of Contents

### Hierarchy

Headings should follow this structure:
- # Title
- ## Section
- ### Subsection

## General Guidelines

•⁠  ⁠Follow the format in [README](/DATA605/DATA605_Spring2025/README.md).  
•⁠  ⁠Explain how PyMC3's native API was used.  
•⁠  ⁠Describe the data, modeling architecture, inference technique, and results.  
•⁠  ⁠Name this file: `pymc3.example.md`

---

## Project Overview

This notebook demonstrates real-time Bitcoin price forecasting using **two Bayesian time series models** built with PyMC3:

1. **Gaussian Random Walk (GRW)** model  
2. **Bayesian ARIMA (AR(1))** model  

Each model is evaluated for its ability to learn the latent structure of the time series and generate credible probabilistic forecasts.

---

## Tools and Architecture

- **PyMC3** (`pymc`) – for model specification and inference  
- **Pandas** – to manage and preprocess price data  
- **Seaborn / Matplotlib** – for visualization  
- **ArviZ** – for posterior summaries and diagnostic plots  
- **TQDM** and **Logging** – for clean, interactive logging

---

## Dataset

- Bitcoin prices are ingested and stored as a time series.
- Data is centered or differenced where required to meet model assumptions.
- Used as input to both GRW and AR(1) models.

---

## Model 1: Gaussian Random Walk (GRW)

### Description

- Models the price as a latent random walk trend with observation noise.
- Suitable for capturing smooth, non-stationary underlying patterns.

### PyMC3 Structure

```python
with pm.Model() as state_space_model:
    sigma_rw = pm.HalfNormal("sigma_rw", sigma=50)
    trend = pm.GaussianRandomWalk("trend", sigma=sigma_rw, shape=len(y))
    sigma_obs = pm.HalfNormal("sigma_obs", sigma=50)
    y_obs = pm.Normal("y_obs", mu=trend, sigma=sigma_obs, observed=y)
    trace_ss = pm.sample(1000, tune=1000, target_accept=0.95)
```

### Forecasting

- Posterior predictive simulations for `n_forecast` steps
- Forecasts visualized with credible intervals

---

## Model 2: Bayesian ARIMA (AR(1))

### Description

- Implements a simple AR(1) model using priors over `phi` (autoregressive coefficient)
- Each price depends linearly on the previous one + Gaussian noise
- Enables short-term forecasting with quantified uncertainty

### PyMC3 Structure

```python
with pm.Model() as ar1_model:
    phi = pm.Normal("phi", mu=0, sigma=1)
    sigma = pm.HalfNormal("sigma", sigma=50)
    y0 = pm.Normal("y0", mu=0, sigma=50)
    y_obs = [y0]
    for t in range(1, len(y_centered)):
        mu = phi * y_obs[t - 1]
        y_t = pm.Normal(f"y_{t}", mu=mu, sigma=sigma, observed=y_centered[t])
        y_obs.append(y_t)
    trace_ar1 = pm.sample(1000, tune=1000, target_accept=0.95)
```

### Forecasting

- Forecast future values using sampled `phi` and `sigma`
- 95% HDI intervals plotted alongside predictions

---

## Comparison and Insights

| Model              | Strengths                          | Limitations                         |
|-------------------|------------------------------------|-------------------------------------|
| Gaussian RW       | Captures latent trends smoothly    | Lacks autoregressive structure      |
| Bayesian AR(1)    | Captures short-term dependencies   | May underperform on trending data   |

Both models provide credible intervals and full posterior samples, making them suitable for risk-aware decision-making.

---

## Key Learnings

- Bayesian time series models offer interpretable, uncertainty-aware forecasts
- PyMC3 enables flexible construction of both state-space and autoregressive models
- Forecasting financial time series benefits from combining multiple Bayesian approaches

---

## References

- [PyMC Documentation](https://www.pymc.io/projects/docs/en/stable/)
- [Bayesian ARIMA Example](https://github.com/fonnesbeck/Bayesians-in-action)
- [ArviZ](https://www.arviz.org/)
- [Charles Copley Blog](https://charlescopley.medium.com/conducting-time-series-bayesian-analysis-using-pymc-22269aeb208b)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)
