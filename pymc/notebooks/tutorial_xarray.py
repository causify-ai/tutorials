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
# #!pip install xarray
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install xarray)"

# %%
# !sudo /bin/bash -c "(source /venv/bin/activate; pip install yapf)"

# %%
import numpy as np

print("numpy version=", np.__version__)
import xarray as xr

print("xarray version=", xr.__version__)

# %%
from IPython.display import HTML, display

display(HTML("<style>.container { width:77% !important; }</style>"))

# %% [markdown]
# # Overview: why xarray?

# %% [markdown]
# - `xarray` adds labels (e.g., dimensions, coordinates, attributes) to `numpy` N-dim arrays (aka tensors)
#
# - `xarray` allows to:
#     - apply operations over dimensions by name
#     - use dimension names (e.g., `dim='time'` vs `axis=0`)
#     - select values by label (instead of integer location)
#     - vectorizes
#     - split-apply-combine paradigm
#     - write less code
#     - label-based operations frees users to know how the data is organized
#
# - `DataArray` is labeled N-dimensional array
#     - generalizes `pd.Series` to N dimensions
#     - attaches labels to `np.ndarray`
#
# - `Dataset` is dict-like container of `DataArray`
#     - arrays in `Dataset` can have different number of dimensions
#
# - `xarray` integrates with the Pydata ecosystem (`numpy`, `pandas`, `Dask`, `matplotlib`)
#     - It's easy to get data in and out

# %% [markdown]
# # Quick overview
#
# From https://docs.xarray.dev/en/stable/getting-started-guide/quick-overview.html

# %% [markdown]
# ## Create DataArray

# %%
np.random.seed(314)
data = xr.DataArray(
    # - Create a 2D array.
    # np.random.rand(2, 3),
    [[1, 2, 3], [4, 5, 6]],
    # - Assign x and y to the dimensions.
    dims=("x", "y"),
    # - Assign coordinate labels 10 and 20 to locations along x dimension.
    coords={"x": [10, 20]},
)
data

# x has 2 dimensions "x", "y"
# the x dimensions has coordinates/names

# %%
print(type(data))

# %%
print(data)

# %%
# Extract the numpy data structure.
vals = data.values
print(type(vals))
print(vals)

# %%
# Extract the dimension names which are a tuple.
print(type(data.dims))
print(data.dims)

# %%
# Extract the coordinates.
print(type(data.coords))
print(data.coords)

# %%
# Extract the attributes.
data.attrs

# %% [markdown]
# ### Indexing

# %%
data

# %% [markdown]
# - Slicing an xarray returns another xarray with the slice

# %%
# Set the x dimension to be 0 (like numpy), so get the first row.
data[0, :]

# %%
# Set the x dimension to be 1 (like numpy), so get the second row.
data[1, :]

# %%
# loc, "location": select by coordinate label (like pandas)
# Get data along the first dimension for the index called `10`.
data.loc[10]

# %%
# isel, "integer select": select by dimension name and integer label
# Get data along the dimension `x` for the first index
data.isel(x=0)

# %%
# isel, "integer select": select by dimension name and integer label
# Get data along the dimension `y` for the second index
data.isel(y=1)

# %%
# sel, "select", by dimension name and coordinate label
# Get data along the dimension `x` and the index `10`
data.sel(x=10)

# %% [markdown]
# ### Attributes
#
# - You can add metadata attributes to `DataArray` or to coordinates
# - They are used automatically in the plots

# %%
data.attrs["long_name"] = "random_velocity"
data.attrs["units"] = "m/s"
data.attrs["description"] = "A random var created as an example"

print(data.attrs)

# %%
data

# %%
data.x.attrs["units"] = "x units"

# %%
data

# %% [markdown]
# ### Computation

# %%
data + 10

# %%
data.sum()

# %%
# Compute mean over one dimension by label.
data.mean(dim="x")

# %%
# Transposition.
data.T

# %%
np.random.seed(314)
# Create a 1-vector with coordinates.
a = xr.DataArray(np.random.randn(3), {"y": [0, 1, 2]})
display(a)
# Create a 1-vector with dimension.
b = xr.DataArray(np.random.randn(4), dims="z")
display(b)

# %%
# No need for
a + b

# %%
np.random.seed(314)
# Create a 1-vector with coordinates.
a = xr.DataArray(np.random.randn(3), {"z": [0, 1, 2]})
# Create a 1-vector with dimension.
b = xr.DataArray(np.random.randn(3), dims="z")

a + b

# %% [markdown]
# ### Pandas interaction

# %%
# From xarray to multi-index pd.Series.
srs = data.to_series()
srs

# %%
# From pd.Series to xarray.
srs.to_xarray()

# %%
df = data.to_dataframe(name="hello")
df

# %% [markdown]
# ### Plotting

# %%
# The plot uses the attributes.
data.plot()

# %% [markdown]
# ## Datasets
#
# - Variables in a `Dataset` can have different dimensions and dtypes
# - If two variables have the same dimension (e.g., `x`) the dimension must be identical in both variables

# %%
# Create a dictionary with heterogeneous data.
dict_ = dict(foo=data, bar=("x", [1, 2]), baz=np.pi)
print(dict_)

# %%
# Create a dataset from the dict.
# - foo is a DataArray (with 2 dimensions)
# - bar is a one-dimensional
# - baz is a scalar (with no dimensions)
ds = xr.Dataset(dict_)
ds

# %%
# Extract one variable from the dataset.
ds["foo"]
# Equivalent to:
# ds.foo

# %%
# Both `foo` and `bar` variables have the same coordinate `x`.
# So we can use `x` to slice the data.
ds["x"]
# ds.bar["x"]
# ds.foo["x"]

# %%
