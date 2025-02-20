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

# %%
# # !sudo /bin/bash -c "(source /venv/bin/activate; pip install --quiet jupyterlab-vim)"
# # !jupyter labextension enable

# %%
# %load_ext autoreload
# %autoreload 2

import arviz as az
import pymc as pm
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

# %% [markdown]
# ### Style notebook

# %%
plt.rcParams['figure.figsize'] = [8, 3]

# %% [markdown]
# # Chap1: Thinking probabilistically

# %% [markdown]
# # Chap 2: Programming probabilistically

# %% [markdown]
# ## Probabilistic programming

# %%
np.random.seed(123)

trials = 4
# Unknown value.
theta_real = 0.35

# Generate some values.
data = stats.bernoulli.rvs(p=theta_real, size=trials)
print(data)

# %%
with pm.Model() as model:
    # - Prior.
    # \theta ~ Beta(\alpha=1, \beta=1) ~ Uniform[0, 1]
    theta = pm.Beta("theta", alpha=1.0, beta=1.0)
    # Likelihood.
    # - We pass the data using `observed` to condition the unknown to the knows (data).
    y = pm.Bernoulli('y', p=theta, observed=data)
    # Inference button.
    # - Compute 1000 samples from the posterior and store in `idata`.
    # - NUTS is a sampler that works for continuous variables.
    idata = pm.sample(1000, random_seed=123)

# %% [markdown]
# ```
# Auto-assigning NUTS sampler...
# Initializing NUTS using jitter+adapt_diag...
# ```
# - NUTS sampler is an inference engine that works well for continuous variables
#
# ```
# Multiprocess sampling (4 chains in 4 jobs)
# ```
# - 4 chains are computed in parallel (based on the number of the available processors)
#
# ```
# NUTS: [theta]
# ```
# - Report which variable is sampled by which sampler
#
# ```
# Sampling 4 chains for 1_000 tune and 1_000 draw iterations (4_000 + 4_000 draws total) took 1 seconds.
# ```
# - 1,000 samples are used to tune the sampling algorithm and will be discarded

# %%
pm.model_to_graphviz(model)

# %%
print(type(idata))

# %%
idata

# %%
# import warnings
# warnings.filterwarnings("ignore")

# %%
# warnings.filterwarnings("error", category=FutureWarning, message="Series.__getitem__")

# %% [markdown]
# ## Summarizing the posterior

# %%
# Plot traces and Kernel Density Estimation (KDE) of the posterior (there are 4 posteriors) of the
# unobserved variable.
az.plot_trace(idata);

# %% [markdown]
# There is a KDE plot for each of the 4 chains
# - They should look smooth and with a clear pattern
# - They should look very similar

# %%
# Combine all the chains in a single distribution.
az.plot_trace(idata, combined=True);

# %%
# Rank plot of the chains.
# We want the histograms of all the chains be uniform to ensure that we are exploring different regions of the posterior.
az.plot_trace(idata, kind="rank_bars");

# %%
az.summary(idata, kind="stats").round(2)

# %% [markdown]
# - The mean of the posterior value of `theta` is 0.34
# - The value of `theta` is between 0.04 and 0.66 with 94% probabilitiy
# - Note that the highest density interval is more precise than mean and std

# %%
# Summarize the posterior.
# mean, std dev, 94% HPD interval of the unknown param.
az.summary(idata)

# %%
# Plot posterior.
az.plot_posterior(idata);

# %%
# Percentage of posterior below and above reference value.
az.plot_posterior(idata, ref_val=0.5);

# %% [markdown]
# ### Savage-Dickey density ratio

# %%
az.plot_bf(idata, var_name="theta", prior=np.random.uniform(0, 1, 10_000), ref_val=0.5);

# %% [markdown]
# ### ROPE

# %%
# KDE of posterior, ROPE, and % of posterior in ROPE.
az.plot_posterior(idata, rope=[0.45, 0.55]);

# %% [markdown]
# ## Loss functions

# %%
#idata["theta"]
#idata.get_values('theta', chains=[0])
#idata.to_dataframe()

# %%
grid = np.linspace(0, 1, 200)
#print(grid)
#theta_pos = idata["theta"]
theta_pos = idata.to_dataframe()[("posterior", "theta")]

# Absolute loss.
lossf_a = [np.mean(abs(i - theta_pos)) for i in grid]
lossf_b = [np.mean((i - theta_pos) ** 2) for i in grid]

for lossf, c in zip([lossf_a, lossf_b], ["C0", "C1"]):
    # Plot loss.
    plt.plot(grid, lossf)
    #
    min_x = np.argmin(lossf)
    # Plot minimum value.
    plt.plot(grid[min_x], lossf[min_x], 'o', color=c)
    
#
plt.yticks([])
plt.xlabel(r'$\hat{\theta}$')

# %% [markdown]
# ## Gaussian all the way down

# %% [markdown]
# ### Gaussian inference

# %%
# !ls /aux/code/book.2018.Martin.Bayesian_Analysis_with_Python.2e
dir_name = "/aux/code/book.2018.Martin.Bayesian_Analysis_with_Python.2e"

# %%
data = np.loadtxt(f"{dir_name}/chemical_shifts.csv")
print(len(data))
print(data)
#print(sorted(data))

# It looks Gaussian with a couple of outliers.
az.plot_kde(data, rug=True);

# %%
with pm.Model() as model_g:
    # The mean is Uniform in [40, 70] (which is larger than the data).
    mu = pm.Uniform("mu", lower=40, upper=70)
    # The std dev is half normal with a large value (which is a large value based on the data).
    sigma = pm.HalfNormal("sigma", sigma=10)
    # The model is N(mu, sigma).
    y = pm.Normal("y", mu=mu, sigma=sigma, observed=data)
    # Sample.
    idata_g = pm.sample(1000)

# %%
pm.model_to_graphviz(model_g)

# %%
#az.style.use("arviz-darkgrid")

# %%
# There are 2 traces.
az.plot_trace(idata_g);

# %%
# The posterior distribution of the params is bi-dimensional, since it has mu and sigma.
az.plot_pair(idata_g, kind='kde', marginals=True);

# %%
idata_g

# %%
# Extract the 2 chains of the posterior.
#idata_g.posterior["chain"]

# %%
# Extract the posterior.
#posterior = az.extract(idata_g)
#posterior

# %%
# Report a summary of the inference.
az.summary(idata_g, kind="stats").round(2)

# %% [markdown]
# ### Posterior predictive check
# $$\Pr(\hat{y} | y) = \int \Pr(\hat{y} | \theta) \Pr(\theta | y) d\theta$$

# %%
# Compute 100 posterior predictive samples.
y_pred_g = pm.sample_posterior_predictive(idata_g, model=model_g)

# %%
y_pred_g

# %%
# #?az.plot_ppc

# %%
# Black line is KDE of the data (observed)
# Blue lines are KDEs of the posterior predictive samples
az.plot_ppc(y_pred_g, mean=True, num_pp_samples=100);

# %% [markdown]
# - The mean of the posterior looks more on the right than the data
# - The std dev of the posterior looks larger
# - This is a result of the two "outliers" from the bulk of the distribution

# %% [markdown]
# ## Robust inference
#
# One could argue that the assumption of gaussianity of the data is incorrect
# - The normal distribution is "surprised" to see outliers
# - The result is fitting too much
#
# Solutions
# 1) Remove the outliers
# 2) Change the model
#     - E.g., switch from Gaussian to T-distribution

# %%
# Almost Gaussian (df \to \infty)
vals = stats.t(loc=0, scale=1, df=100).rvs(1000)
print(vals[:10])
print(np.mean(vals))
print(np.std(vals))

# %%
az.plot_posterior(vals);

# %%
# Cauchy (df=1)
az.plot_posterior(stats.t(loc=0, scale=1, df=1).rvs(1000));

# %%
# Show the PDF for various values of \nu.

# Points to be used to sample the PDF.
x_values = np.linspace(-10, 10, 500)

# Plot t-student sweeping \nu.
for df in [1, 2, 5, 10, 30]:
    # Student-t with df.
    distr = stats.t(df)
    # Compute PDF.
    x_pdf = distr.pdf(x_values)
    plt.plot(x_values, x_pdf, label=f"nu={df}")
    
# Plot gaussian.
x_pdf = stats.norm.pdf(x_values)
plt.plot(x_values, x_pdf, "k--", label="Gauss / nu=infty")

plt.xlim(-5, 5) 
plt.legend();

# %%
# Use a Student-T model.
with pm.Model() as model_t:
    mu = pm.Uniform("mu", 40, 75)
    sigma = pm.HalfNormal("sigma", sigma=10)
    # A student with nu = 30 is close to a Gaussian.
    nu = pm.Exponential("nu", 1/30)
    #
    y = pm.StudentT("y", mu=mu, sigma=sigma, nu=nu, observed=data)
    idata_t = pm.sample(1_000)

# %%
az.plot_trace(idata_t);

# %% [markdown]
# - mu is similar to the estimate with a Gaussian
# - sigma is smaller
# - nu ~ 5, which is not very Gaussian
#
# The outliers have the effect of decreasing nu, instead of pulling the mean towards them
# and increasing the std.

# %%
az.summary(idata_t, kind="stats").round(2)

# %%
# Compute 100 posterior predictive samples.
y_ppc_t = pm.sample_posterior_predictive(idata_t, model_t)

# %%
ax = az.plot_ppc(y_ppc_t, num_pp_samples=100, mean=True)
ax.set_xlim(40, 70)

# %% [markdown]
# - The plot is "hairy".
# - The reason is that KDE is estimated only in the actual interval of the data, and it's 0 outside.
#

# %% [markdown]
# ## Inference data

# %%
idata_g = idata_g

idata_g

# %%
posterior = idata_g["posterior"]
posterior

# %%
# Select the first draw from chain 0 and 2.
posterior.sel(draw=0, chain=[0, 2])

# %%
# First 100 draws from all chains.
posterior.sel(draw=slice(0, 100))

# %%
posterior.mean()

# %%
# Combine all the `chain` in a single one.
stacked = az.extract(idata_g)
stacked

# %% [markdown]
# ## Group comparison

# %%
import pandas as pd
import seaborn as sns
import pprint

# %%
tips = pd.read_csv(dir_name + '/tips.csv')
tips

# %% [markdown]
# - Study the effect of the day of the week on the tips earned at a restaurant

# %%
sns.violinplot(x='day', y='tip', data=tips);

# %%
# Extract the tips.
tip = tips['tip'].values
print(tip[:10])

# Create a vector going from day to group idx.
idx = pd.Categorical(tips['day']).codes
print("idx=", idx)

# Count the groups.
groups = np.unique(idx)
n_groups = len(groups)
print("groups=", n_groups, groups)

# %%
# The model is the same as before but it can be easily vectorized.
# There is no need to write a for-loop.
with pm.Model() as comparing_groups:
    # mu is a vector of 4 elems.
    mu = pm.Normal('mu', mu=0, sigma=10, shape=n_groups)
    # sigma is a vector of 4 elems.
    sigma = pm.HalfNormal("sigma", sigma=10, shape=n_groups)
    # y is a vector of 4 normals each with mean and sigma for the group.
    y = pm.Normal('y', mu=mu[idx], sigma=sigma[idx], observed=tip)
    idata_cg = pm.sample(5000)

# %% [markdown]
# ### Model from xarray.Dataset

# %%
categories = np.array("Thur Fri Sat Sun".split())
coords = {"days": categories, "days_flat": categories[idx]}
print("coords=", pprint.pformat(coords))

# %%
with pm.Model(coords=coords) as comparing_groups:
    mu = pm.HalfNormal("mu", sigma=5, dims="days")
    sigma = pm.HalfNormal("sigma", sigma=1, dims="days")
    y = pm.Gamma("y", mu=mu[idx], sigma=sigma[idx], observed=tip, dims="days_flat")
    idata_cg = pm.sample()
    idata_cg.extend(pm.sample_posterior_predictive(idata_cg))

# %%
idata_cg

# %%
az.plot_trace(idata_cg);

# %%
_, axes = plt.subplots(2, 2)
az.plot_ppc(idata_cg, num_pp_samples=100,
            coords={"days_flat": [categories]},
            flatten=[],
            ax=axes)

# %%
i = 0
j = 1
mean_diff = idata_cg.posterior['mu'][:, i] - idata_cg.posterior['mu'][:, j]
sd1 = idata_cg.posterior['sigma'][:, i] ** 2
sd2 = idata_cg.posterior['sigma'][:, j] ** 2

cohen_d = mean_diff / np.sqrt((sd1 + sd2)/2)
#print(cohen_d)

#plt.plot(cohen_d)
az.plot_posterior(cohen_d, ref_val=0);
