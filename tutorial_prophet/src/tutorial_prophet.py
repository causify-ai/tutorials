# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Description

# %% [markdown]
# The notebook shows how to perform time series prediction using the Prophet model developed by Facebook.
#
# References:
# - White paper: `https://peerj.com/preprints/3190.pdf`
# - Official docs: `https://facebook.github.io/prophet/docs/quick_start.html`

# %% [markdown]
# # Imports

# %%
# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# %%
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import prophet as prh
import prophet.diagnostics as diagnostics
import plotly.graph_objects as go
import prophet.plot as plo
import prophet.utilities as prhu

import sklearn.metrics as metrics
import scipy.stats as stats

import helpers.hprint as hprint
import helpers.hdbg as hdbg
import helpers.hpandas as hpanda

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

hprint.config_notebook()

# %% [markdown]
# # Config

# %%
config = {
    # Train/test split.
    "train_start_date": "2020-01-01",
    "train_end_date": "2023-12-31",
    "test_start_date": "2024-01-01",
    "test_end_date": "2024-12-31",
    "data": {
        # Linear trend params.
        "slope": 0.005,
        "intercept": 15,
        # Fourier term params for seasonality component.
        "weekly_amp_sin": 5.0,
        "weekly_amp_cos": 2.5,
        # List of holidays and their impact.
        "holidays_dates": ['2020-12-25', '2021-12-25', '2022-12-25', "2023-12-25", "2024-12-25"],
        "holidays_impact": 2.5,
        # Autoregression params.
        "ar_order": 1,
        "phi": 0.7,
        # Noise std.
        "seed": 42,
        "noise_sigma": 2.0,
    },
    "model": {
        # Defines trend shape.
        "growth":"linear", 
        "yearly_seasonality":False, 
        # Integer defines Fourier order.
        "weekly_seasonality":1, 
        "daily_seasonality":False, 
        "n_changepoints":0, 
        # Prophet internally scales the target variable.
        "scaling":"minmax", 
        # Confidence iterval width.
        "interval_width":0.95,
        # Number of MCMC samples; If `mcmc_samples = 0`, the model produces just a point estimate  of each
        # parameter instead of the full distribution.
        "mcmc_samples":300,
        # Set lower prior scale to narrow the confidence interval.
        "holidays_prior_scale":0.1,
    },
}
print(config)

# %% [markdown]
# # Generate data

# %%
# Generate date range.
dates = pd.date_range(start=config["train_start_date"], end=config["test_end_date"], freq='D')
time = np.arange(len(dates))
# Define linear trend.
y_trend = config["data"]["slope"] * time + config["data"]["intercept"]
# Define the seasonality factor.
p_weekly = 7
y_weekly_seasonality = config["data"]["weekly_amp_sin"] * np.sin(2 * np.pi * time / p_weekly) + config["data"]["weekly_amp_cos"] * np.cos(2 * np.pi * time / p_weekly)
# Define holidays impact.
holiday_effect = np.zeros(len(dates))
holiday_effect[np.isin(dates.date, pd.to_datetime(config["data"]["holidays_dates"]).date)] = config["data"]["holidays_impact"]
# Define white noise.
np.random.seed(config["data"]["seed"])
noise = np.random.normal(loc=0, scale=config["data"]["noise_sigma"], size=len(time))
# Add autoregressive behavior.
y = np.zeros(len(time))
y[0] = y_trend[0] + y_weekly_seasonality[0] + holiday_effect[0] + noise[0]
for i in range(1, len(time)):
    y[i] = config["data"]["phi"] * y[i-1] + y_trend[i] + y_weekly_seasonality[i] + holiday_effect[i] + noise[i]
# Columns "ds" for timestamp and "y" for target variable is necessary in prophet. https://facebook.github.io/prophet/docs/quick_start.html
df = pd.DataFrame({"ds": dates, "y": y})
# Add lagged value of the target as a feature.
df["y.lag1"] = df["y"].shift(1)
# The first row for the lagged feature is NaN; we have to remove it because the model cannot handle NaNs
df = df.dropna()
_LOG.info(hpanda.df_to_str(df, log_level=logging.INFO))

# %%
df.set_index("ds")["y"].plot(title="Original data", ylabel="Target variable", xlabel="Time")

# %% [markdown]
# # Fit the model

# %%
start_date_filter = df["ds"] >= config["train_start_date"]
end_date_filter = df["ds"] <= config["train_end_date"]
df_train = df[start_date_filter & end_date_filter]
_LOG.info(hpanda.df_to_str(df_train, log_level=logging.INFO))

# %% [markdown]
# In Prophet, holidays can be customized to account for their effects on time series data.
# Each holiday is defined as a specific date or set of recurring dates. 
# Additionally, you can extend the influence of a holiday to a range of days using 
# the `lower_window` and `upper_window` parameters:
#
#  - `lower_window`: Specifies how many days before the holiday the effect starts.
#  - `upper_window`: Specifies how many days after the holiday the effect ends.
#
# For example:
#  - To include Christmas Eve as part of the Christmas holiday effect, set 
#    `lower_window=-1` and `upper_window=0`.
#  - To include Black Friday in addition to Thanksgiving, set 
#    `lower_window=0` and `upper_window=1`.
#
# Additionally, you can customize the strength of the holiday effect for each holiday 
# using the `prior_scale` parameter. This allows finer control over the regularization 
# of each holiday's effect, balancing flexibility and overfitting.
#
#

# %%
# Construct a Dataframe with holidays.
holidays_df = pd.DataFrame({
    'holiday': ['Christmas 2020', 'Christmas 2021', 'Christmas 2022', "Christmas 2023", "Christmas 2024"],
    'ds': pd.to_datetime(config["data"]["holidays_dates"]),
    'lower_window': 0, 
    'upper_window': 0,   
})
_LOG.info(hpanda.df_to_str(holidays_df, log_level=logging.INFO))

# %%
model = prh.Prophet(**config["model"], holidays=holidays_df)
# Explicitly add the lagged feature as an external regressor.
model.add_regressor('y.lag1')
model.fit(df_train)

# %% [markdown]
# Dimensionality:
# - k (Mx1 array): M posterior samples of the initial slope
# - m (Mx1 array): The initial intercept
# - delta (MxN array): The slope change at each of N changepoints
# - beta (MxK matrix): Coefficients for K seasonality features
# - sigma_obs (Mx1 array): Noise level
# - M=1 (meaning that only the point estimate is available) if MAP estimation, i.e. `mcmc_samples=0` 
#
# The number M (posterior samples) depends on:
# - `mcmc_samples` provided by the user
# - number of chains and the model internal mechanics that the user does not control
#    - E.g., Prophet might be discarding some samples (e.g., through thinning) to reduce autocorrelation between the samples or to improve convergence

# %% [markdown]
# Scaling:
# - Prophet perofrorms scaling internally, i.e. time is mapped to be on [0, 1] and Y is scaled by model.y_scale
# - Where `y_scale` is controlled by the user and can be `absmax` or `minmax` scaling 
# - TODO(Grisha): consider rescaling coefficients in order to compare them to the ground truth

# %%
_LOG.info("Model Scale: %s, Model Min: %s", model.y_scale, model.y_min)

# %%
estimated_intercept = model.params["m"]
pd.Series(estimated_intercept).plot(kind="hist")
_LOG.info("Shape of the intercept = %s", estimated_intercept.shape)
_LOG.info("Intercept point estimate = %s", estimated_intercept.mean())

# %%
estimated_slope = model.params["k"]
pd.Series(estimated_slope).plot(kind="hist")
_LOG.info("Shape of the slope = %s", estimated_slope.shape)
_LOG.info("Slope point estimate = %s", estimated_slope.mean())

# %% [markdown]
# Estimated value of the autoregression coefficient is close to the ground truth.

# %%
# Use `regressor_coefficients()` to extract external regressors' coefficient. Unlike the other coeficients these
# already takes into account the internal scaling, thus can be directly compared to the original coefficients.
regressor_coefficients = prhu.regressor_coefficients(model)
_LOG.info(hpanda.df_to_str(regressor_coefficients, log_level=logging.INFO))
_LOG.info("True value of the autoregression coefficient = %s", config["data"]["phi"])

# %% [markdown]
# Description:
# - `weekly_delim_1` is the coefficient for the sine term
# - `weekly_delim_2` is the coefficient for the cosine term
# - in general the number of the Fourier coefficients is 2xN (i.e. 1 for the sine and 1 for the cosine), where N is Fourier order (i.e. 1 in our case)
# - then we have 5 coefficients for 5 holidays
# - and finally coefficients for the lagged feature
# - each coefficient is a vector of length M (number of posterior samples)
#
# Once the params are extracted:
# - one can easily obtain a point estimate by averaging the values within a column
# - compute confidence intervals using `np.quatile()`
# - study the entire parameter's distribution

# %%
# Use this table to identify coefficients' indices in the regressors' matrix.
col_names = model.make_all_seasonality_features(df_train)[0].columns 
coefficients_df = pd.DataFrame(model.params["beta"], columns = col_names)
_LOG.info(hpanda.df_to_str(coefficients_df, log_level=logging.INFO))

# %% [markdown]
# # Predict

# %%
start_date_filter = df["ds"] >= config["test_start_date"]
end_date_filter = df["ds"] <= config["test_end_date"]
df_test = df[start_date_filter & end_date_filter].reset_index(drop=True)
_LOG.info(hpanda.df_to_str(df_test, log_level=logging.INFO))

# %%
# Predict on the entire data and then analyze the tran and test split seperately to gain more insights.
forecast = model.predict(df)
forecast = forecast.merge(df, how="inner", on=["ds"])
forecast["residual"] = forecast["y"] - forecast["yhat"]
_LOG.info(hpanda.df_to_str(forecast, log_level=logging.INFO))

# %% [markdown]
# # Analyze the results

# %%
ins_forecast = forecast[forecast["ds"]<=config["train_end_date"]]
ins_forecast.tail(5)

# %%
ins_forecast["residual"].plot()

# %%
stats.probplot(ins_forecast["residual"], dist="norm", plot=plt)
plt.title("Q-Q Plot: Train set residuals")
plt.show()

# %% [markdown]
# Residuals are normal distributed, hence the modle is working fine.

# %%
plt.plot(ins_forecast["ds"], ins_forecast["yhat"], label="Point Estimate", ls='--', c='#0072B2')
plt.plot(ins_forecast["ds"], ins_forecast["y"], label="Observed data", color="blue")

# Plot confidence/prediction intervals
plt.fill_between(
    ins_forecast["ds"],
    ins_forecast["yhat_lower"],
    ins_forecast["yhat_upper"],
    color="blue",
    alpha=0.2,
    label="Confidence Interval",
)
plt.title("Observed vs predicted data, train set")

# %% [markdown]
# ### `Prophet.plot()`
#
# The `Prophet.plot()` function is used to visualize the forecast generated by the Prophet model. It provides a comprehensive view of the predicted trend and uncertainty intervals over the forecast horizon.
#
# **Key Features:**
# 1. **Forecast Line**: Displays the predicted values (`yhat`), representing the central forecast.
# 2. **Uncertainty Intervals**:
#    - Shaded regions represent the uncertainty intervals (`yhat_lower` and `yhat_upper`), capturing the range within which the forecast is expected to fall.
#    - By default, this represents a 95% confidence interval.
# 3. **Historical Data**:
#    - Overlaid as points to show how the forecast aligns with the actual data.

# %%
model.plot(ins_forecast, include_legend=True)

# %% [markdown]
# ### `Prophet.plot_components()`
#
# The `Prophet.plot_components()` function provides a breakdown of the individual components contributing to the forecast. This helps understand **why** the forecast behaves as it does.
#
# **Components Visualized:**
# 1. **Trend**:
#    - Displays the underlying trend in the data, excluding seasonality and holidays.
#    - Useful for identifying long-term growth or decline patterns.
# 2. **Seasonality**:
#    - Shows recurring patterns (e.g., daily, weekly, yearly seasonality) identified from the data.
#    - If multiple seasonalities are specified, they are plotted separately.
# 3. **Holidays (if applicable)**:
#    - Visualizes the effect of specified holidays on the forecast.
#    - Helps identify spikes or dips caused by holidays.

# %%
fig2 = model.plot_components(ins_forecast)

# %%
oos_forecast = forecast[forecast["ds"]>=config["test_start_date"]]
oos_forecast.tail(5)

# %%
model.plot(oos_forecast)

# %%
model.plot_components(oos_forecast)

# %% [markdown]
# ### Prophet.plot_plotly()
# The Prophet.plot_plotly() function provides an interactive visualization of the forecast using the Plotly library. This is an alternative to Prophet.plot(), which uses Matplotlib for static plots.
#
# With plot_plotly(), you can dynamically explore the forecast, zoom in/out, hover over data points to see values, and pan through the graph, making it especially useful for presentations or exploring large datasets.

# %%
# Create Prophet's interactive plot
fig = plo.plot_plotly(model, forecast)

# Add ground truth (actual values)
fig.add_trace(
    go.Scatter(
        x=df_test['ds'],
        y=df_test['y'],
        mode='markers',
        name='Ground Truth',
        marker=dict(color='red', size=5)
    )
)

# Update layout
fig.update_layout(
    title="Forecast vs Ground Truth",
    xaxis_title="Date",
    yaxis_title="Values",
    legend=dict(orientation="h", y=-0.2),
)

# Show the plot
fig.show()


# %% [markdown]
# # Performance metrics
#
# Prophet provides performance metric calculation only on the cross validation data. To test the performance of prophet model on test split we will be using sklearn metrics.

# %%
# Calculate metrics
mae = metrics.mean_absolute_error(oos_forecast['y'], oos_forecast['yhat'])
rmse = metrics.mean_squared_error(oos_forecast['y'], oos_forecast['yhat'])
mape = (abs(oos_forecast['y'] - oos_forecast['yhat']) / oos_forecast['y']).mean() * 100

_LOG.info("MAE=%s, RMSE=%s, MAPE=%s", mae, rmse, mape)

# %% [markdown]
# # Cross Validation
#
# `cross_validation` method does not take in the dataset as input so the cross validation is done on the data used in `model.fit()`
#
# - Sliding Window Approach:
#
# The historical dataset is split into multiple training and testing sets using a sliding window approach.
# Each training set ends at a specific cutoff date, and the model is tested on the subsequent data.
#
# - Parameters:
#
#     - initial: The size of the initial training period (e.g., 3 years).
#     - horizon: The forecast horizon for which predictions are made (e.g., 30 days).
#     - period: The spacing between cutoff dates (e.g., 90 days).
# This setup generates overlapping training and testing periods, simulating how the model performs when trained on different subsets of the data.
#
# Prophet's cross_validation function adheres to the rolling approach. Each fold contains:
#
# - A training set determined by the initial parameter (e.g., the first 3 years of data).
# - A validation set that starts right after the training set and spans the horizon period (e.g., 90 days into the future).
# - The window is shifted forward by the period parameter (e.g., every 180 days), creating new training and validation splits.

# %%
df_cv = diagnostics.cross_validation(
    model=model,
    # Use 2 years as initial training period.
    initial='730 days',
    # Move rolling window every 180 days.
    period='180 days',     
    horizon='365 days'
)


# %%
df_perf = diagnostics.performance_metrics(df_cv)
_LOG.info(hpanda.df_to_str(df_perf, log_level=logging.INFO))

# %%
df_cv.head()

# %%
# Plot Mean Absolute Percentage Error (MAPE)
fig = plo.plot_cross_validation_metric(df_cv, metric='mape')

# %%
