# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
try:
    import arviz as az
    import pymc as pm
except ModuleNotFound:
    # !sudo /bin/bash -c "(source /venv/bin/activate; pip install pymc)"
    # !sudo /bin/bash -c "(source /venv/bin/activate; pip install arviz)"
    # #!pip install arviz
    # #!pip install pymc3
    pass

# %%
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install graphviz)"

# %%
import numpy as np

print("numpy version=", np.__version__)
import pymc as pm

print("pymc3 version=", pm.__version__)
import arviz as az

print("arviz version=", az.__version__)
import graphviz

print("graphviz version=", graphviz.__version__)

# %%
from IPython.display import HTML, display

# Control the size of the notebook.
display(HTML("<style>.container { width:80% !important; }</style>"))

# %% [markdown]
# https://python.arviz.org/en/latest/index.html
#
# - ArviZ is a package for exploratory analysis of Bayesian models.
# - It is backend agnostic (e.g., PyStan, PyMC, raw `numpy` arrays)

# %% [markdown]
# # Getting Started
#
# https://python.arviz.org/en/latest/getting_started/index.html#

# %% [markdown]
# ## ArviZ quickstart
#
# https://python.arviz.org/en/latest/getting_started/Introduction.html

# %%
# Plot a distribution with some info about HDI.
vals = np.random.randn(100_000)
print(vals)
az.plot_posterior(vals)

# %%
# A 2d array is interpreted as "chain x draws" by `arviz`.
# 10 chains, 50 draws.
size = (10, 50)
# print(np.random.randn(*size))

# %%
size = (10, 50)
# A dict is interpreted as multiple random vars, each with different "chains x draws".
data = {
    "normal": np.random.randn(*size),
    "gumbel": np.random.gumbel(size=size),
    "student t": np.random.standard_t(df=6, size=size),
    "exponential": np.random.exponential(size=size),
}
az.plot_forest(data)
# So there are 4 RVs, each with 10 realizations, each with 50 samples.

# %%
az.plot_posterior(data["normal"][0])
az.plot_posterior(data["normal"][1])

# %%
# data["normal"] is a 10 chains x 50 samples, but when plotting all the data is concat.
az.plot_posterior(data["normal"])

# %%

# %% [markdown]
# ## InferenceData
#
# From https://python.arviz.org/en/latest/getting_started/Introduction.html#convert-to-inferencedata
#
# The object returned by most PyMC sampling methods is `arviz.InferenceData`.

# %%
# 8 school examples
# - there are 8 schools (each with a name)
# -

J = 8
# Observations.
# - Mean (unknown).
y = np.array([28.0, 8.0, -3.0, 7.0, -1.0, 1.0, 18.0, 12.0])
# - Std dev (is known).
sigma = np.array([15.0, 10.0, 16.0, 11.0, 9.0, 11.0, 10.0, 18.0])

schools = np.array(
    [
        "Choate",
        "Deerfield",
        "Phillips Andover",
        "Phillips Exeter",
        "Hotchkiss",
        "Lawrenceville",
        "St. Paul's",
        "Mt. Hermon",
    ]
)

# with pm.Model() as centered_eight:
#    # 8 normal RVs for the mean.
#    mu = pm.Normal("mu", mu=0, sigma=5)
#    tau = pm.HalfCauchy("tau", beta=5)
#    theta = pm.Normal("theta", mu=mu, sigma=tau, shape=J)
#    # The observed data has:
#    # - random means and
#    # - known std dev.
#    obs = pm.Normal("obs", mu=theta, sigma=sigma, observed=y)
#    # This pattern is useful in PyMC3.
#    #prior = pm.sample_prior_predictive()
#    # Sample the posterior.
#    centered_eight_trace = pm.sample(
#        # Return data as arviz.InferenceData instead of MultiTrace.
#        return_inferencedata=False)
#    posterior_predictive = pm.sample_posterior_predictive(centered_eight_trace)

# %%
# pm.model_to_graphviz(centered_eight)

# %% [markdown]
# - Most ArviZ functions accept `trace` objects.
# - It can be converted into `InferenceData`

# %%
# print(type(centered_eight))
# print(centered_eight)

# print(type(centered_eight_trace))
# print(centered_eight_trace)

# %%
with pm.Model(coords={"school": schools}) as centered_eight:
    mu = pm.Normal("mu", mu=0, sigma=5)
    tau = pm.HalfCauchy("tau", beta=5)
    theta = pm.Normal("theta", mu=mu, sigma=tau, dims="school")
    pm.Normal("obs", mu=theta, sigma=sigma, observed=y, dims="school")

    # This pattern can be useful in PyMC
    idata = pm.sample_prior_predictive()
    idata.extend(pm.sample())
    pm.sample_posterior_predictive(idata, extend_inferencedata=True)

# %%
idata

# %%
az.plot_autocorr(centered_eight_trace)

# %%
# Build the inference data from PyMC3 run.
data = az.from_pymc(
    trace=centered_eight_trace,
    prior=prior,
    posterior_predictive=posterior_predictive,
    model=centered_eight,
    coords={"school": schools},
    dims={"theta": ["school"], "obs": ["school"]},
)
data

# %% [markdown]
# ## Intro do xarray, InferenceData
#
# From https://python.arviz.org/en/latest/getting_started/XarrayforArviZ.html

# %% [markdown]
# Bayesian inference generates numerous datasets:
# - Prior / posterior distribution for vars
# - Observed data
# - Prior / posterior predictive distribution
# - Trace data for each of the above
# - Sample statistics for each inference run
#
# Data from probabilistic programming is high-dimensional
# - Use `xarray` to store high-dimensional data with human readable dimensions and coordinates

# %%
print(az.list_datasets())

# %%
# From Bayesian Data Analysis, section 5.5 (Gelman et al. 2013):

# A study was performed for the Educational Testing Service to analyze the effects of special coaching
# programs for SAT-V (Scholastic Aptitude Test-Verbal) in each of eight high schools. The outcome variable
# in each study was the score on a special administration of the SAT-V, a standardized multiple choice test
# administered by the Educational Testing Service and used to help colleges make admissions decisions; the
# scores can vary between 200 and 800, with mean about 500 and standard deviation about 100. The SAT
# examinations are designed to be resistant to short-term efforts directed specifically toward improving
# performance on the test; instead they are designed to reflect knowledge acquired and abilities developed
# over many years of education. Nevertheless, each of the eight schools in this study considered its short-term
# coaching program to be very successful at increasing SAT scores. Also, there was no prior reason to believe
# that any of the eight programs was more effective than any other or that some were more similar in effect to
# each other than to any other.

# %%
data = az.load_arviz_data("centered_eight")
data

# %% [markdown]
# - There are 3 variables and 4 chains

# %%
observed_data = data.observed_data
observed_data

# %% [markdown]
# - `xarray.Dataset` (and `InferenceData`) store data in memory
# - NetCDF is a standard for serializing data

# %% [markdown]
# ## Creating InferenceData
#
# From https://python.arviz.org/en/latest/getting_started/CreatingInferenceData.html

# %%
size = 100
data = np.random.randn(size)
dataset = az.convert_to_inference_data(data)
dataset

# %% [markdown]
# ## Working with InferenceData
#
# From https://python.arviz.org/en/latest/getting_started/WorkingWithInferenceData.html

# %% [markdown]
# # User guide

# %% [markdown]
# ## Data structures
#
# ### InferenceData schema
# https://python.arviz.org/en/latest/schema/schema.html#schema

# %%

# %%
