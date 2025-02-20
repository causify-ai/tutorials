# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
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
import pandas as pd
import seaborn as sns
import scipy.stats as stats
import matplotlib.pyplot as plt
import preliz as pz

# %% [markdown]
# ### Style notebook

# %%
plt.rcParams['figure.figsize'] = [8, 3]

dir_name = "/aux/code/book.2018.Martin.Bayesian_Analysis_with_Python.2e"

# %% [markdown]
# # Thinking probabilistically

# %% [markdown]
# # Programming probabilistically

# %% [markdown]
# # Hierarchical models

# %% [markdown]
# ## Hierarchical shifts

# %%
cs_data = pd.read_csv(dir_name + '/chemical_shifts_theo_exp.csv')
cs_data["diff"] = cs_data["theo"] - cs_data["exp"]
display(cs_data)

# %% [markdown]
# - ID: code of the protein
# - aa: name of the amino acid
# - theo: theoretical values of chemical shift
# - exp: experimental value

# %%
sns.kdeplot(cs_data["diff"]);

# %%
vals = cs_data["aa"].unique()
print("aa=", len(vals), vals)

# %%
diff = cs_data.theo.values - cs_data.exp.values
print("diff=", diff)

# Array of categorical values.
cat_encode = pd.Categorical(cs_data['aa'])
print("cat_encode=", cat_encode)
idx = cat_encode.codes
print("idx=", len(idx), idx)
coords = {"aa": cat_encode.categories}
print("coords=", coords)

# %% [markdown]
# ## Hierarchical shifts

# %% [markdown]
# ### Non-hierarchical model

# %%
# Non-hierarchical model.
with pm.Model(coords=coords) as cs_nh:
    # One separate prior for each group.
    mu = pm.Normal('mu', mu=0, sigma=10, dims="aa")
    sigma = pm.HalfNormal("sigma", sigma=10, dims="aa")
    # Likelihood.
    y = pm.Normal("y", mu=mu[idx], sigma=sigma[idx], observed=diff)
    idata_cs_nh = pm.sample()

# %%
pm.model_to_graphviz(cs_nh)

# %%
idata_cs_nh

# %% [markdown]
# ### Hierarchical model

# %% [markdown]
# - Assume that there are 2 hyperpriors one for mean and one for std dev of mu
# - We assume that \sigma is without hyperpriors
#     - \sigma is the same for all the groups

# %%
with pm.Model(coords=coords) as cs_h:
    # Hyper-priors.
    mu_mu = pm.Normal("mu_mu", mu=0, sigma=10)
    mu_sigma = pm.HalfNormal("mu_sigma", sigma=10)
    
    # Priors.
    mu = pm.Normal("mu", mu=mu_mu, sigma=mu_sigma, dims="aa")
    sigma = pm.HalfNormal("sigma", sigma=10, dims="aa")
    
    # Likelihood (same as before).
    y = pm.Normal("y", mu=mu[idx], sigma=sigma[idx], observed=diff)
    idata_cs_h = pm.sample()

# %%
pm.model_to_graphviz(cs_h)

# %%
idata_cs_h

# %% [markdown]
# ### Comparison

# %%
# We have two models and we want to compare the estimates.
# - There are 20 groups and each model has 4 estimates.
# - We plot the 94% credible intervals.
# - The vertical line is the global mean according to the hierarchical model.
# - The blue (hierarchical) means are pulled towards the mean, wrt the orange (non-hierarchical) ones.
axes = az.plot_forest([idata_cs_h, idata_cs_nh],
                      model_names=['h', 'n_h'],
                      var_names='mu',
                      combined=False,
                      colors='cycle')

y_lims = axes[0].get_ylim()
axes[0].vlines(idata_cs_h.posterior['mu_mu'].mean(), *y_lims, color='navy')
axes[0].vlines(idata_cs_nh.posterior['mu'].mean(), *y_lims, color='orange')


# %% [markdown]
# ## Water quality

# %%
def get_water_data(G_samples):
    # 3 different parts of the city.
    # N_samples is the number of samples for each group.
    N_samples = [30, 30, 30]
    
    # For each sample.
    group_idx = np.repeat(np.arange(len(N_samples)), N_samples)
    print("group_idx=", group_idx)
    
    # For each group.
    data = []
    for i in range(0, len(N_samples)):
        # Create a vector with 1 for good samples, and 0 for bad sample for each group.
        vals = np.repeat([1, 0], [G_samples[i], N_samples[i] - G_samples[i]])
        data.extend(vals)
        
    print("data=", data)
    return data


# %%
# Good samples per group.
G_samples = [18, 18, 18]
data = get_water_data(G_samples)


# %%
def fit(data):
    with pm.Model() as model_h:
        # Hyperpriors.
        mu = pm.Beta("mu", 1.0, 1.0)
        nu = pm.HalfNormal("nu", 10)
        # Priors.
        theta = pm.Beta("theta",
                        alpha=mu * nu,
                        beta=(1.0 - mu) * nu,
                        shape=len(N_samples))
        # Model.
        y = pm.Bernoulli('y', p=theta[group_idx], observed=data)
        idata_h = pm.sample(2000)
    return idata_h


# %%
idata_h = fit(data)

# %%
az.plot_trace(idata_h);

# %%
az.summary(idata_h, kind="stats")

# %% [markdown]
# ## Shrinkage
#

# %%
G_samples_array = [
    [18, 18, 18],
    [3, 3, 3],
    [18, 3, 3]]

idata = [None, None, None]
for i, G_samples in enumerate(G_samples_array):
    data = get_water_data(G_samples)
    idata[i] = fit(data)
    #idata = az.extract(idata)

# %%
az.plot_trace(idata[0]);
#az.summary(idata, kind="stats")

# %%
idata

# %%
data = []
for i in range(3):
    data_tmp = az.summary(idata[i]["posterior"]["theta"], kind="stats")["mean"].values
    print(G_samples_array[i], ":", data_tmp)
    data.append(data_tmp)

# %%
df = pd.DataFrame(
    data,
    index=map(str, G_samples_array))
df

# %%
df.plot(kind="bar")

# %%
# Plot the hyper priors.
x = np.linspace(0, 1, 100)

# Pick 10 priors.
n_priors = 100
for i in np.random.randint(0, len(idata_h), size=n_priors):
    u = idata_h.posterior['mu'][0][i]
    n = idata_h.posterior['nu'][0][i]
    pdf = stats.beta(u * n, (1.0 - u) * n).pdf(x)
    plt.plot(x, pdf, 'C1', alpha=0.2)

# Plot the mean prior.
u_mean = idata_h.posterior['mu'].mean()
n_mean = idata_h.posterior['nu'].mean()
dist = stats.beta(u_mean * n_mean, (1.0 - u_mean) * n_mean)
pdf = dist.pdf(x)

mode = x[np.argmax(pdf)]
mean = dist.moment(1)

plt.plot(x, pdf, lw=3, label=f'mode = {mode:.2f}\nmean = {mean:.2f}')
plt.yticks([])
plt.legend()
plt.xlabel('$θ_{prior}$')
plt.tight_layout()

# %% [markdown]
# ## Hierarchies all the way up

# %%
football = pd.read_csv(dir_name + "/data/football_players.csv", dtype={'position':'category'})
football

# %%
football["ratio"] = football["goals"] / football["shots"]
football.groupby("position")["ratio"].mean() * 100.0

# %%
football.groupby("position")["shots"].sum()

# %%
football.groupby("position")["goals"].sum()

# %%
pos_idx = football.position.cat.codes.values
print("pos_idx=", pos_idx)
pos_codes = football.position.cat.categories
print("pos_codes=", pos_codes)
n_pos = pos_codes.size
print("n_pos=", n_pos)
n_players = football.index.size
print("n_players=", n_players)

# %%
coords = {"pos": pos_codes}
with pm.Model(coords=coords) as model_football:
    # - Hyper params.
    # Weakly informative prior since we know that 0.5 is very high value.
    # This is choosen to have 95% of mass between 0 and 0.5
    mu = pm.Beta("mu", 1.7, 5.8)
    nu = pm.Gamma("nu", mu=125, sigma=50)
    # - Params for positions.
    mu_p = pm.Beta("mu_p", mu=mu, nu=nu, dims="pos")
    nu_p = pm.Gamma("nu_p", mu=125, sigma=50, dims="pos")
    # - Params for players.
    theta = pm.Beta("theta", mu=mu_p[pos_idx], nu=nu_p[pos_idx])
    gs = pm.Binomial("gs", n=football.shots.values, p=theta, observed=football.goals.values)
    #
    idata_football = pm.sample()

# %%
graph = pm.model_to_graphviz(model_football)
graph

# %%
pz.Beta(1.7, 5.8).plot_interactive()

# %%
pz.Gamma(mu=125, sigma=50).plot_interactive()

# %%
idata_football

# %%
# Plot the posterior mean for several scenarios.
_, ax = plt.subplots(3, 1, figsize=(12, 6), sharex=True)

az.plot_posterior(idata_football, var_names='mu', ax=ax[0])
ax[0].set_title(r"Global mean")

az.plot_posterior(idata_football.posterior.sel(pos="FW"), var_names='mu_p', ax=ax[1])
ax[1].set_title(r"Forward position mean")

az.plot_posterior(idata_football.posterior.sel(theta_dim_0=1457), var_names='theta', ax=ax[2])
ax[2].set_title(r"Messi mean")

# %%
# Plot the posterior distribution by position.
az.plot_forest(idata_football, var_names=['mu_p'], combined=True);
