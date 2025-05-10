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
#
# This notebook is a tutorial on how to use Tensorflow for time series data.

# %%
# Install required libs on the fly.
# Tensorflow needs to be downloaded from pip as poetry relies on the package metadata to resolve packages, 
# tensorflow does not consistently contain the required metadata. https://github.com/python-poetry/poetry/issues/8764
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install tensorflow)"
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install tensorflow-probability)"
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install tf-keras)"

# %%
# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# %%
import logging
import collections
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas.plotting as pdp
import seaborn as sns
import scipy.stats as stats
import sklearn.metrics as metrics
import tensorflow as tf
import tf_keras
import tensorflow_probability as tfp


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
        # params for random walk,
        "seasonal_drift_scale" : 0.5,
        # List of holidays and their impact.
        "holidays_dates": ['2020-12-25', '2021-12-25', '2022-12-25', "2023-12-25", "2024-12-25"],
        "holidays_impact" : 0.25,
        # Autoregression params.
        "ar_order": 1,
        "phi": 0.7,
        # Noise std.
        "seed": 42,
        "observational_noise_sigma": 2.0,
    },
    "model": {
        "num_seasons": 7,
        "num_steps_per_season":1,
        "learning_rate": 0.1,
        "num_steps": 200,
    },
}
print(config)

# %% [markdown]
# # Generate data

# %%
np.random.seed(config["data"]["seed"])
# Generate date range.
dates = pd.date_range(start=config["train_start_date"], end=config["test_end_date"], freq='D')
time = np.arange(len(dates))
# Define linear trend.
y_trend = config["data"]["slope"] * time + config["data"]["intercept"]
# Define the seasonality factor.
seasonality_factor = 7
# Generate seasonal effects with drift
for t in range(seasonality_factor, len(dates), seasonality_factor):
    y_trend[t] = y_trend[t - seasonality_factor] + np.random.normal(0, config["data"]["seasonal_drift_scale"])
# # Generate seasonal effects with drift
# seasonal_effects = np.zeros(len(dates))
# for t in range(seasonality_factor, len(dates), seasonality_factor):
#     seasonal_effects[t] = seasonal_effects[t - seasonality_factor] + np.random.normal(
#         0, config["data"]["seasonal_drift_scale"]
#     )
# Define holidays impact.
holiday_effect = np.zeros(len(dates))
holiday_effect[np.isin(dates.date, pd.to_datetime(config["data"]["holidays_dates"]).date)] = config["data"]["holidays_impact"]
# Define white noise.
noise = np.random.normal(loc=0, scale=config["data"]["observational_noise_sigma"], size=len(time))
# Add autoregressive behavior.
y = np.zeros(len(time))
y[0] = y_trend[0] + holiday_effect[0] + noise[0] 
for i in range(1, len(time)):
    y[i] = config["data"]["phi"] * y[i-1] + y_trend[i] + holiday_effect[i] + noise[i]
df = pd.DataFrame({"ds": dates, "y": y})
# Add lagged value of the target as a feature.
df["y.lag1"] = df["y"].shift(1)
# The first row is NaN -> drop it.
df = df.dropna()
_LOG.info(hpanda.df_to_str(df, log_level=logging.INFO))

# %%
df.set_index("ds")["y"].plot(title="Original data", ylabel="Target variable", xlabel="Time")

# %% [markdown]
# ## Plotting Helpers

# %%
# It is used to register date converters with Matplotlib. 
# This ensures that Matplotlib can properly handle and plot date-related data.
pdp.register_matplotlib_converters()
sns.set_context("notebook", font_scale=1.)
sns.set_style("whitegrid")
# %config InlineBackend.figure_format = 'retina'

# %%
def plot_forecast(
    x: np.ndarray,
    y: np.ndarray,
    forecast_mean: np.ndarray,
    forecast_scale: np.ndarray,
    forecast_samples: np.ndarray,
    title: str,
    x_locator: Optional[plt.Locator] = None,
    x_formatter: Optional[plt.Formatter] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot a forecast distribution against the 'true' time series.

    :param x: The time points for the entire dataset.
    :param y: The ground truth values for the time series.
    :param forecast_mean: The mean values of the forecasted distribution.
    :param forecast_scale: The scale (standard deviation) of the forecasted distribution.
    :param forecast_samples: Samples drawn from the forecasted distribution.
    :param title: The title of the plot.
    :param x_locator: Optional locator for the x-axis (e.g., for dates).
    :param x_formatter: Optional formatter for the x-axis labels.
    :return: A tuple containing the figure and axes objects of the plot.
    """
    colors = sns.color_palette()
    c1, c2 = colors[0], colors[1]
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1)
    #
    num_steps = len(y)
    num_steps_forecast = forecast_mean.shape[-1]
    num_steps_train = num_steps - num_steps_forecast
    #
    ax.plot(x, y, lw=2, color=c1, label="ground truth")
    forecast_steps = x[num_steps_train : num_steps_train + num_steps_forecast]
    ax.plot(forecast_steps, forecast_samples.T, lw=1, color=c2, alpha=0.1)
    ax.plot(
        forecast_steps,
        forecast_mean,
        lw=2,
        ls="--",
        color=c2,
        label="forecast",
    )
    ax.fill_between(
        # x-axis values (e.g., time steps or forecast points).
        forecast_steps,
        # Lower boundary of the confidence interval.
        forecast_mean - 2 * forecast_scale,
        # Upper boundary of the confidence interval.
        forecast_mean + 2 * forecast_scale, 
        color=c2,
        alpha=0.2,
    )
    ymin, ymax = (
        min(np.min(forecast_samples), np.min(y)),
        max(np.max(forecast_samples), np.max(y)),
    )
    yrange = ymax - ymin
    ax.set_ylim([ymin - yrange * 0.1, ymax + yrange * 0.1])
    ax.set_title("{}".format(title))
    ax.legend()
    if x_locator is not None:
        ax.xaxis.set_major_locator(x_locator)
        ax.xaxis.set_major_formatter(x_formatter)
        fig.autofmt_xdate()
    return fig, ax



# %%
def plot_components(
    dates: np.ndarray,
    component_means_dict: Dict[str, np.ndarray],
    component_stddevs_dict: Dict[str, np.ndarray],
    *,
    x_locator: Optional[plt.Locator] = None,
    x_formatter: Optional[plt.Formatter] = None,
) -> Tuple[plt.Figure, Dict[str, plt.Axes]]:
    """
    Plot the contributions of posterior components in a single figure.

    :param dates: Array of dates corresponding to the time series.
    :param component_means_dict: Dictionary where keys are component names 
        and values are arrays of mean contributions of each component.
    :param component_stddevs_dict: Dictionary where keys are component names 
        and values are arrays of standard deviations of each component.
    :param x_locator: Optional locator for the x-axis (e.g., for dates).
    :param x_formatter: Optional formatter for the x-axis labels.
    :return: A tuple containing the figure and an ordered dictionary of axes objects, 
        keyed by component names.
    """
    colors = sns.color_palette()
    c1, c2 = colors[0], colors[1]
    #
    axes_dict = collections.OrderedDict()
    num_components = len(component_means_dict)
    fig = plt.figure(figsize=(12, 2.5 * num_components))
    #
    for i, component_name in enumerate(component_means_dict.keys()):
        component_mean = component_means_dict[component_name]
        component_stddev = component_stddevs_dict[component_name]
        #
        ax = fig.add_subplot(num_components, 1, 1 + i)
        ax.plot(dates, component_mean, lw=2)
        ax.fill_between(
            dates,
            component_mean - 2 * component_stddev,
            component_mean + 2 * component_stddev,
            color=c2,
            alpha=0.5,
        )
        ax.set_title(component_name)
        if x_locator is not None:
            ax.xaxis.set_major_locator(x_locator)
            ax.xaxis.set_major_formatter(x_formatter)
        axes_dict[component_name] = ax
    #
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig, axes_dict



# %% [markdown]
# ## Tran and Test Split

# %%
start_date_filter = df["ds"] >= config["train_start_date"]
end_date_filter = df["ds"] <= config["train_end_date"]
df_train = df[start_date_filter & end_date_filter].reset_index(drop=True)
_LOG.info(hpanda.df_to_str(df_train, log_level=logging.INFO))

# %%
start_date_filter = df["ds"] >= config["test_start_date"]
end_date_filter = df["ds"] <= config["test_end_date"]
df_test = df[start_date_filter & end_date_filter].reset_index(drop=True)
_LOG.info(hpanda.df_to_str(df_test, log_level=logging.INFO))


# %% [markdown]
# ## Model and Fitting

# %%
def build_model(observed_time_series: np.ndarray, holiday_features: np.ndarray) -> tfp.sts.Sum:
    """
    Build a Structural Time Series (STS) model for forecasting.

    The model includes the following components:
    - A local linear trend to capture long-term changes.
    - A seasonal component to account for day-of-week effects.
    - An autoregressive component to model temporal dependencies.

    :param observed_time_series: The observed time series data as a NumPy array.
    :return: An STS model combining trend, seasonal, and autoregressive components.
    """
    trend = tfp.sts.LocalLinearTrend(observed_time_series=observed_time_series)
    day_of_week_effect = tfp.sts.Seasonal(
        num_seasons=config["model"]["num_seasons"],
        num_steps_per_season=config["model"]["num_steps_per_season"],
        observed_time_series=observed_time_series,
        name="day_of_week_effect",
    )
    autoregressive = tfp.sts.Autoregressive(
        order=1,
        observed_time_series=observed_time_series,
        name="autoregressive",
    )
    # Using example of holiday indicators https://www.tensorflow.org/probability/api_docs/python/tfp/sts/LinearRegression
    # TODO(Sonaal) : Adding holiday_effect in model is throwing some error during forecast. 
    holiday_effect = tfp.sts.LinearRegression(
         design_matrix=holiday_features,
         name='holiday_effect'
    )
    
    # Combine components into a single model
    model = tfp.sts.Sum(
        [trend, day_of_week_effect, autoregressive, holiday_effect],
        observed_time_series=observed_time_series,
    )
    return model
     


# %%
# Generate a date range for the entire period.
all_dates = pd.date_range(start=config["train_start_date"], end=config["test_end_date"])
# Extract holiday dates from the configuration.
holiday_dates = pd.to_datetime(config["data"]["holidays_dates"])
holiday_features = np.isin(all_dates, holiday_dates).astype(float)
holiday_indicators = np.zeros((len(all_dates), len(holiday_dates)))
# For each date we create a one hot vector.
for i, holiday in enumerate(holiday_dates):
    holiday_indicators[:, i] = (all_dates == holiday).astype(int)
_LOG.info("holdiay features = %s, shape = %s", holiday_indicators, holiday_indicators.shape)

# %%
model = build_model(df_train["y"].to_numpy(), holiday_indicators)

# %% [markdown]
# ## Background
#
# This code is part of a **Variational Inference** (VI) process used to approximate the posterior distribution of a Bayesian model. In this case, TensorFlow Probability (TFP) is used to build a **surrogate posterior** and optimize it to approximate the true posterior distribution of a model. The idea behind variational inference is to turn the problem of calculating intractable posteriors into a tractable optimization problem. This is done by approximating the true posterior with a simpler distribution (the surrogate posterior) and then optimizing it to be as close as possible to the true posterior.
#
# #### Key Concepts and When to Use
#
# - **Bayesian Inference**: In Bayesian inference, we aim to calculate the posterior distribution of the model parameters given the data. This can be computationally expensive or intractable for complex models.
# - **Variational Inference (VI)**: VI is a method to approximate the posterior distribution by optimizing a surrogate distribution (which is easier to compute). It does this by minimizing the **Evidence Lower Bound (ELBO)**, which is a measure of how close the surrogate posterior is to the true posterior.
#   
# **Optimizing the Variational Loss Function (ELBO):**
#
# ```python
# elbo_loss_curve = tfp.vi.fit_surrogate_posterior(
#     target_log_prob_fn=model.joint_distribution(
#         observed_time_series=df_train["y"].to_numpy()).log_prob,
#     surrogate_posterior=variational_posteriors,
#     optimizer=tf_keras.optimizers.Adam(learning_rate=config["model"]["learning_rate"]),
#     num_steps=num_variational_steps,
#     jit_compile=True)
# ```
#
# - **Purpose**: This performs the optimization of the variational posterior by minimizing the **ELBO loss**.
# - **How it works**: 
#   - `target_log_prob_fn`: This is the log-probability of the model’s joint distribution, evaluated on the observed data.
#   - `surrogate_posterior`: This is the surrogate posterior distribution (`qs`), which we aim to optimize.
#   - `optimizer`: The optimizer used to minimize the ELBO loss. Here, Adam is used with a learning rate specified in the config.
#   - `num_steps`: The number of optimization steps, controlled by `num_variational_steps`.
#   - `jit_compile`: This enables JIT (Just-In-Time) compilation to speed up the optimization process using TensorFlow's XLA (Accelerated Linear Algebra).
# - **When to use**: This is the core part of variational inference, used when we want to approximate the posterior distribution in a computationally efficient way. It’s helpful for models where traditional sampling-based approaches (e.g., MCMC) are too slow or impractical.
#
# ### Model Parameters
#
# The model consists of various components, and the parameters pertain to these components. Let’s go over some typical model parameters in a **Structural Time Series** (STS) model and their role:
#
# 1. **Trend Parameters**:
#    - These represent the long-term movements in the time series.
#    - Common parameters:
#      - **Level**: The current level of the time series.
#      - **Slope**: The rate of change of the level over time.
#
# 2. **Seasonal Components**:
#    - These capture periodic patterns, such as weekly or yearly cycles.
#    
#    
# 3. **Autoregressive Parameters**:
#    - These capture dependencies between time steps.
#    - Common parameters:
#      - **Order**: The number of past time steps considered in the autoregressive process (e.g., AR(1) for one-step lag).
#      - **Coefficient**: The weight of the past time step in predicting the current value.
#
# 4. **Noise Parameters**:
#    - These represent the random fluctuations or errors in the data.
#    - Common parameters:
#      - **Observation Noise Scale**: The variance of the observation noise.
#    

# %%
# Build the variational surrogate posteriors `qs`.
variational_posteriors = tfp.sts.build_factored_surrogate_posterior(
    model=model)

# %%
# Allow external control of optimization to reduce test runtimes.
num_variational_steps = config["model"]["num_steps"]

# Build and optimize the variational loss function.
elbo_loss_curve = tfp.vi.fit_surrogate_posterior(
    target_log_prob_fn=model.joint_distribution(
        observed_time_series=df_train["y"].to_numpy()).log_prob,
    surrogate_posterior=variational_posteriors,
    optimizer=tf_keras.optimizers.Adam(learning_rate=config["model"]["learning_rate"]),
    num_steps=num_variational_steps,
    jit_compile=True)
plt.plot(elbo_loss_curve, label="ELBO Loss Curve")
plt.xlabel("Optimization Steps")
plt.ylabel("ELBO Loss")
plt.title("Variational Optimization Progress")
plt.legend()
plt.grid(True)
plt.show()

# Draw samples from the variational posterior.
q_samples_ = variational_posteriors.sample(50)

# %% [markdown]
# ### Explanation of Parameters and Outputs:
#
# #### 1. **`LocalLinearTrend/_level_scale` and `LocalLinearTrend/_slope_scale`**
#    - **Definition**: These represent the variability (or uncertainty) in the level and slope of the local linear trend in the time series. 
#      - **Level scale** (`_level_scale`): Refers to the variability or noise in the level of the trend component in the Local Linear Trend model. 
#      - **Slope scale** (`_slope_scale`): Reflects variability in the rate of change (or slope) of the trend.
# #### 2. **`day_of_week_effect/_drift_scale`**
#    - **Definition**: Represents the variability in the day-of-week effects (e.g., systematic variations in the time series that recur weekly). 
#    - **Seasonality Model**: Unlike Prophet, which models seasonality using Fourier terms (sine and cosine functions), this implementation likely uses a simpler drift-based approach. 
#      
# #### 3. **`autoregressive/_level_scale`**
#    - **Definition**: Represents the noise scale or variability at the level of the autoregressive (AR) process. 
#    - **Autoregressive Model**: This parameter reflects how much the AR process deviates from the expected trajectory defined by its coefficients.
#      - Higher values of `_level_scale` indicate a noisier AR process, whereas lower values suggest that the process closely follows the AR coefficients.
#

# %%
_LOG.info("Inferred parameters:")
for param in model.parameters:
  _LOG.info("%s: %s +- %s", param.name,
                              np.mean(q_samples_[param.name], axis=0),
                              np.std(q_samples_[param.name], axis=0))

# %%
#TODO(Sonaal): We can't directly compare `_slope_scale` with slope as `_slope_scale` is basically slope noise.
# Can we find a way to model actual data parameters.

# %%
# TODO(Sonaal): The true seasonal_drift_scale is not in 95% confidence internval. Need to investigate why is that.
_LOG.info("True Sesonality drift  = %s, Predicted Seasonality drift =%s", config["data"]["seasonal_drift_scale"], np.mean(q_samples_["day_of_week_effect/_drift_scale"]))

# %%
# Build a dict mapping components to distributions over
# their contribution to the observed signal.
component_dists = tfp.sts.decompose_by_component(
    model,
    observed_time_series=df_train["y"].to_numpy(),
    parameter_samples=q_samples_)

# %%
component_means_, component_stddevs_ = (
    {k.name: c.mean() for k, c in component_dists.items()},
    {k.name: c.stddev() for k, c in component_dists.items()})

# %%
_ = plot_components(df_train["ds"], component_means_, component_stddevs_,
                    x_locator=None, x_formatter=None)

# %%
# Forecast the prediction.
forecast_dist = tfp.sts.forecast(
    model=model,
    observed_time_series=df_train["y"].to_numpy(),
    parameter_samples=q_samples_,
    num_steps_forecast=len(df_test))


# %%
num_samples=10
(
    forecast_mean,
    forecast_scale,
    forecast_samples
) = (
    forecast_dist.mean().numpy()[..., 0],
    forecast_dist.stddev().numpy()[..., 0],
    forecast_dist.sample(num_samples).numpy()[..., 0]
    )

# %%
fig, ax = plot_forecast(df_test["ds"], df_test["y"].to_numpy(),
                        forecast_mean,
                        forecast_scale,
                        forecast_samples,
                        title="Forecast Plot",
                        x_locator=None, x_formatter=None)
fig.tight_layout()

# %%
# Calculate residuals
residuals = df_test["y"].to_numpy() - forecast_mean
plt.figure(figsize=(10, 6))
plt.plot(df_test["ds"], residuals, label="Residuals", color="blue")
plt.axhline(0, color="red", linestyle="--", label="Zero Line")
plt.title("Residuals Over Time")
plt.xlabel("Date")
plt.ylabel("Residuals")
plt.legend()
plt.grid(True)
plt.show()

# Q-Q Plot for Residuals
plt.figure(figsize=(10, 5))
stats.probplot(residuals, dist="norm", plot=plt)
plt.title("Q-Q Plot of Residuals")
plt.show()

# %% [markdown]
# ## Performance Metric

# %%
mae = metrics.mean_absolute_error(df_test["y"].to_numpy(), forecast_mean)
_LOG.info("Mean Absolute Error (MAE): %s", mae)
mse = metrics.mean_squared_error(df_test["y"].to_numpy(), forecast_mean)
_LOG.info("Mean Squared Error (MSE): %s", mse)

# %%
