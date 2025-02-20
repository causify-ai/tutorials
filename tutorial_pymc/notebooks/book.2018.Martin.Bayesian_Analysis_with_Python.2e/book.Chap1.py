# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Imports

# %% [markdown]
# ### Install packages.

# %%
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim)"
# !jupyter labextension enable

# %%
# # From https://pypi.org/project/jupyter-black/
# # https://github.com/n8henrie/jupyter-black
# # !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-black)"
# import black
# import jupyter_black

# jupyter_black.load(
#     lab=False,
#     line_length=79,
#     verbosity="DEBUG",
#     target_version=black.TargetVersion.PY310,
# )

# # #%load_ext jupyter_black

# %%
try:
    import preliz as pz
except ModuleNotFoundError:
    # !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet preliz)"
    pass

# %% [markdown]
# ### Print module signature.

# %%
import utils

utils.notebook_signature()

# %% [markdown]
# ### Import modules

# %%
# %load_ext autoreload
# %autoreload 2

import logging

import arviz as az
import pymc as pm
import numpy as np
import seaborn as sns
import scipy.stats as stats
import matplotlib.pyplot as plt
import preliz as pz

# %% [markdown]
# ### Style notebook.

# %%
plt.rcParams['figure.figsize'] = [8, 3]

# %% [markdown]
# ### Refs
#
# https://github.com/aloctavodia/BAP3/blob/main/code/Chp_01.ipynb
# https://github.com/jhrcook/bayesian-analysis-with-python_e2/tree/master/data
# https://github.com/aloctavodia/BAP
#
# /Users/saggese/src/github/bayesian-analysis-with-python_e2
#
# cp ~/src/github/bayesian-analysis-with-python_e2/data/tips.csv ~/src/git_gp1/code/book.2018.Martin.Bayesian_Analysis_with_Python.2e/

# %% [markdown] heading_collapsed=true
# # Chap1: Thinking probabilistically

# %% [markdown]
# ## Gaussian

# %% hidden=true
np.random.seed(42)

# Create a Normal Gaussian.
mu = 0.0
sigma = 1.0
X = stats.norm(mu, sigma)

# Print 3 realizations.
x = X.rvs(3)
print(x)

# %% hidden=true run_control={"marked": true}
# - Plot Gaussian PDF for different values of the params.

mu_params = [-1, 0, 1]
sd_params = [0.5, 1, 1.5]
x = np.linspace(-7, 7, 200)
# Create a 3x3 plot.
_, ax = plt.subplots(len(mu_params),
                     len(sd_params),
                     sharex=True,
                     sharey=True,
                     figsize=(9, 7),
                     # Fit plots into the figure cleanly.
                     constrained_layout=True)
                     #constrained_layout=False)
for i in range(3):
    for j in range(3):
        mu = mu_params[i]
        sd = sd_params[j]
        # Evaluate the PDF in several points.
        y = stats.norm(mu, sd).pdf(x)
        # Plot the PDF.
        ax[i, j].plot(x, y)
        # Add the legend.
        ax[i, j].plot([], label="mu={:3.2f}\nsigma={:3.2f}".format(mu, sd), alpha=0)
        ax[i, j].legend(loc=1)
ax[2, 1].set_xlabel('x')
ax[1, 0].set_ylabel('p(x)', rotation=0, labelpad=20)
#ax[1, 0].set_yticks([])

# %%
params = {
    #"kind": "cdf",
    "kind": "pdf",
    "pointinterval": False,
    "interval": "hdi",   # Highest density interval.
    #"interval": "eti",  # Equal tailed interval.
    "xy_lim": "auto"
}

pz.Normal(mu=0, sigma=1).plot_interactive(**params)

# %%
# Generate some samples.
pdf = pz.Normal(mu=0, sigma=1)
pdf.rvs(10)

# %%
# #?plt.hist

# %%
#n = 100
#n = 1000
n = 100_000_000
plt.hist(pdf.rvs(1000), density=True)
pdf.plot_pdf();

# %% [markdown]
# ## Binomial

# %%
help(pz.Binomial.plot_interactive)

# %%
params = {
    #"kind": "cdf",
    "kind": "pdf",
    "pointinterval": False,
    "interval": "hdi",   # Highest density interval.
    #"interval": "eti",  # Equal tailed interval.
    "xy_lim": "auto"
}

# Probability of k successes on N trial flipping a coin with p success
pz.Binomial(p=0.5, n=5).plot_interactive(**params)

# %% [markdown]
# ## Beta
#
# - Continuous prob distribution defined in [0, 1]
# - It is useful to model probability or proportion
#     - E.g., the probability of success in a Bernoulli trial
#
# - alpha represents "success" parameter
# - beta represents "failure" parameter
#     - When alpha is larger than beta the distribution skews toward 1, indicating a higher probability of success
#     - When alpha = beta the distribution is symmetric and centered around 0.5

# %%
params = {
    #"kind": "cdf",
    "kind": "pdf",
    "pointinterval": False,
    "interval": "hdi",   # Highest density interval.
    #"interval": "eti",  # Equal tailed interval.
    "xy_lim": "auto"
}

alpha = 3.0
beta = 1.0

pz.Beta(alpha=alpha, beta=beta).plot_interactive(**params)

# %%
np.random.seed(123)

trials = 4
# Unknown value.
theta_real = 0.35

# Generate some values.
data = stats.bernoulli.rvs(p=theta_real, size=trials)
print(data)

# %%
params1 = [0.8, 1.0, 2.0, 4.0]
params2 = [0.8, 1.0, 2.0, 4.0]
x = np.linspace(0, 1, 200)
# Create a plot.
_, ax = plt.subplots(len(params1),
                     len(params2),
                     sharex=True,
                     sharey=True,
                     figsize=(9, 7),
                     # Fit plots into the figure cleanly.
                     constrained_layout=True)
                     #constrained_layout=False)
for i in range(len(params1)):
    for j in range(len(params2)):
        param1 = params1[i]
        param2 = params2[j]
        # Evaluate the PDF in several points.
        y = stats.beta(a=param1, b=param2).pdf(x)
        # Plot the PDF.
        ax[i, j].plot(x, y)
        # Add the legend.
        ax[i, j].plot([], label="a={:3.2f}\nb={:3.2f}".format(param1, param2), alpha=0)
        ax[i, j].legend(loc=1)
ax[2, 1].set_xlabel('x')
ax[1, 0].set_ylabel('p(x)', rotation=0, labelpad=20);
#ax[1, 0].set_yticks([])

# %% [markdown]
# ### Beta in function of mean and concentration.

# %%
#help(stats.beta)

# %%
params = {
    #"kind": "cdf",
    "kind": "pdf",
    "pointinterval": False,
    "interval": "hdi",   # Highest density interval.
    #"interval": "eti",  # Equal tailed interval.
    "xy_lim": "auto"
}

mu = 1.0
nu = 0.1
alpha = mu * nu
beta = (1.0 - mu) * nu
print(alpha, beta)

# x = np.linspace(0, 1, 200)
# y = stats.beta(a=alpha, b=beta).pdf(x)
# # Plot the PDF.
# plt.plot(x, y);

pz.Beta(mu=0.5, nu=0.5).plot_interactive(**params)

# %% [markdown]
# ## BetaBinomial
#
# - Discrete RV
# - Represent the probability of success in a series of Bernoulli trials
# - The Binomial models the number of successes in a fixed number of trials $n$
# - The probability of success $p$ is not fixed but follows a Beta distribution

# %%
pz.BetaBinomial(alpha=10, beta=10, n=6).plot_interactive()

# %%
# Generate some samples.
pz.BetaBinomial(alpha=10, beta=10, n=60).rvs(100)

# %%
# Generate samples.
plt.hist(pz.BetaBinomial(alpha=2, beta=5, n=5).rvs(1000))
pz.BetaBinomial(alpha=2, beta=5, n=5).plot_pdf();

# %% [markdown]
# ## BetaScaled

# %%
help(pz.BetaScaled.__init__)

# %%
pz.BetaScaled(alpha=2.0, beta=1.0, lower=-5, upper=5).plot_interactive(**params)

# %% [markdown]
# ## SkewNormal

# %%
help(pz.SkewNormal.__init__)

# %%
# Alpha controls the skewness.
pz.SkewNormal(mu=0, sigma=1.0, alpha=1.0).plot_interactive(**params)

# %% [markdown]
# ## StudentT

# %%
help(pz.StudentT.__init__)

# %%
pz.StudentT(mu=0, sigma=1, nu=3.0).plot_interactive(**params)

# %% [markdown]
# ## Half normal

# %%
help(pz.HalfNormal.__init__)

# %%
pz.HalfNormal(sigma=1.0).plot_interactive(**params)

# %% [markdown]
# ## Exponential

# %%
help(pz.Exponential.__init__)

# %%
pz.Exponential(beta=1.0).plot_interactive(**params)

# %% [markdown]
# ## Gamma

# %%
#help(pz.Gamma)
help(pz.Gamma.__init__)

# Represents the sum of alpha exponentially distributed random variables,
# each of which has rate beta.

# %% [markdown]
# - Model the time until an event occurs a certain number of times, assuming that the event follows a Poisson
#   process (where events occur independently at a constant average rate). 

# %%
pz.Gamma(alpha=1.0, beta=1.0).plot_interactive(**params)

# %% [markdown]
# ## Poisson
#
# - Model the number of events in a fixed interval of time, space, etc
# - We assume that the events happen independently and at a constant average rate
# - Assume mean equal to variance
#
# - E.g.,
#   - Call centers: model the number of customers per hour
#   - Natural events: predict the number of earthquakes in a given region over a specific time
#   - Traffic flow: number of cars passing through a toll booth in a day
#   - Biology: count the number of mutations in a specific DNA segment over time

# %%
# ?pz.Poisson.__init__

# %%
pz.Poisson(mu=1.0).plot_interactive(**params)

# %% [markdown]
# ## NegativeBinomial
#
# - Model the number of failures/trials to achieve a fixed number of successes in a sequence of IID Bernoulli trials
# - It is a generalization of the geometric distribution, which models the number of trials needed to achieve the first success
# - It models overdispersion (i.e., when mean is much smaller than variance)
#
# - E.g.,
#     - Customer service: model the number of unsuccessful customer interactions before achieving success
#     - Sports: number of games a team needs to lose before winning a number of games

# %% [markdown]
# ## Flipping coins pyMC-style

# %%
n_trials = [0, 1, 2, 3, 4, 8, 16, 32, 50, 150]
n_heads = [0, 1, 1, 1, 1, 4, 6, 9, 13, 48]
theta_real = 0.35

params = (1, 1)
x = np.linspace(0, 1, 2000)

# %%
#help(pm.sample)

# %%
import contextlib
import os
import sys


def get_posterior(alpha, beta, data, verbosity=False):
    if not verbosity:
        old_val = logging.getLogger('pymc').getEffectiveLevel()
        logging.getLogger('pymc').setLevel(logging.WARNING)
    #
    with pm.Model() as model:
        # - Prior.
        # \theta ~ Beta(\alpha=1, \beta=1)
        theta = pm.Beta("theta", alpha=alpha, beta=beta)
        # Likelihood.
        # - We pass the data using `observed` to condition the unknown to the knows (data).
        y = pm.Bernoulli('y', p=theta, observed=data)
        # Inference button.
        # - Compute 1000 samples from the posterior and store in `idata`.
        # - NUTS is a sampler that works for continuous variables.
        #
        idata = pm.sample_prior_predictive()
        idata_sample = pm.sample(1000, progressbar=False, chains=1, random_seed=123)
        idata.extend(idata_sample)
        pm.sample_posterior_predictive(idata, extend_inferencedata=True)
    if not verbosity:
        logging.getLogger('pymc').setLevel(old_val)
    return idata


# %%
import logging


# %%
def generate_data(n_heads, n_trials):
    assert n_heads <= n_trials
    data = [1] * n_heads + [0] * (n_trials - n_heads)
    return data


# %%
data = generate_data(5, 10)

# %%
idata = get_posterior(1, 1, data)

# %%
idata

# %%
#az.plot_kde(idata.posterior["theta"].values);
az.plot_kde(idata.prior["theta"].values);

# %%
az.plot_posterior(idata);

# %%
#np.ravel(idata.posterior.theta.values)

# %%
sns.kdeplot(np.ravel(idata.posterior.theta.values))
#theta = pm.Beta("

# %% [markdown]
# ## 

# %%
for idx in range(len(n_trials)):
    n_h = n_heads[idx]
    n_t = n_trials[idx]
    data = generate_data(n_h, n_t)
    
    
        

