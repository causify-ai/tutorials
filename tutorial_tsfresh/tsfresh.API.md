# tsfresh API Tutorial

<!-- toc -->

- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
- [Setting Up](#setting-up)
  * [Dependencies](#dependencies)
- [Data Handling](#data-handling)
- [Feature Extraction](#feature-extraction)
  * [Example Use Case](#example-use-case)
- [Feature Selection](#feature-selection)
  * [Example Use Case](#example-use-case-1)
  * [Key Features](#key-features)
- [Building a Classification System](#building-a-classification-system)
- [Extensions and Integration](#extensions-and-integration)
  * [Example Use Case](#example-use-case-2)

<!-- tocstop -->

## Introduction

- **tsfresh** is a Python library for **time series feature extraction**.
- It automatically calculates hundreds of statistical, temporal, and
  frequency-domain features from raw time series data.
- Its primary use cases include:
  - **Classification**: Predicting discrete labels from time windows.
  - **Regression**: Predicting continuous values from temporal patterns.
  - **Anomaly Detection**: Flagging unusual series based on extracted features.
- Tsfresh accelerates development by removing the need for manual feature
  engineering in time series problems.
- More documentation details:
  [tsfresh Documentation](https://tsfresh.readthedocs.io/).

This tutorial covers:

- Preparing time series data in **long format**.
- Extracting features using pre-defined or custom calculators.
- Selecting relevant features with statistical tests.
- Building an end-to-end ML pipeline for classification.

---

## Architecture Overview

tsfresh's workflow consists of four core components:

1. **Data Preparation**
   - Convert raw time series into a **long-format DataFrame** with columns:
     - `id`: entity identifier.
     - `time`: time index.
     - `value`: measurement value.
     - `kind`: optional, for multivariate signals.
   - This format enables handling multiple entities and channels.

2. **Feature Extraction**
   - Apply built-in feature calculators (mean, variance, Fourier coefficients,
     autocorrelation, etc.).
   - Choose from predefined sets:
     - `MinimalFCParameters` (fast, small subset).
     - `EfficientFCParameters` (balanced).
     - `ComprehensiveFCParameters` (large, slow).

3. **Feature Selection**
   - Use `select_features()` to keep only statistically significant features
     relative to the target.
   - Reduces dimensionality and improves model performance.

4. **Model Training**
   - Feed the selected features into **any scikit-learn compatible estimator**
     (e.g., RandomForest, XGBoost).

---

## Setting Up

### Dependencies

To get started, install tsfresh and typical ML dependencies:

```bash
pip install tsfresh scikit-learn pandas numpy matplotlib
```

Optional extras for speed and scaling:

- `dask` — parallel/distributed computing.
- `statsmodels` — additional statistical features.

---

## Data Handling

tsfresh requires your data in **long format**.

Example for one accelerometer signal:

| id  | time | value |
| --- | ---- | ----- |
| 0   | 0    | 0.256 |
| 0   | 1    | 0.345 |
| 0   | 2    | 0.298 |
| 1   | 0    | 0.521 |
| 1   | 1    | 0.490 |

For **multivariate signals**, add a `kind` column:

| id  | time | kind  | value  |
| --- | ---- | ----- | ------ |
| 0   | 0    | acc_x | 0.256  |
| 0   | 0    | acc_y | -0.345 |
| 0   | 0    | acc_z | 0.120  |

---

## Feature Extraction

Feature extraction is done via:

```python
from tsfresh import extract_features
from tsfresh.feature_extraction import EfficientFCParameters

settings = EfficientFCParameters()
X_features = extract_features(
    df_long,
    column_id="id",
    column_sort="time",
    column_kind="kind",        # optional
    column_value="value",
    default_fc_parameters=settings
)
```

Features can be **statistical**, **frequency-based**, or **shape-based**.

---

### Example Use Case

For the **UCI HAR** dataset:

1. Convert accelerometer & gyroscope signals into long format.
2. Extract features for each 2.56-second window (128 samples).
3. Store hundreds of features per signal axis per sample.

---

## Feature Selection

After extraction, many features may be irrelevant or noisy. Use:

```python
from tsfresh import select_features
X_selected = select_features(X_features, y_labels)
```

This:

- Runs statistical relevance tests for each feature.
- Removes features with low correlation to the target.

---

### Example Use Case

Continuing with UCI HAR:

- Label = type of human activity (walking, sitting, etc.).
- Selection removes features unrelated to distinguishing activities.

---

### Key Features

- **Automated relevance testing**: built-in hypothesis tests.
- **Supports classification & regression targets**.
- **Dimensionality reduction** without manual feature pruning.

---

## Building a Classification System

1. **Prepare Data**: Long format.
2. **Extract Features**: Choose appropriate parameter set.
3. **Select Features**: Keep only relevant features.
4. **Train Model**:

```python
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(X_selected, y_labels)
```

5. **Evaluate**: Accuracy, F1, ROC-AUC.

---

## Extensions and Integration

tsfresh integrates well with:

- **scikit-learn Pipelines**: Wrap extraction & selection as transformer steps.
- **dask**: Parallelize feature calculation.
- **Custom calculators**: Write your own domain-specific features.

---

### Example Use Case

Fault detection in industrial machines:

1. Sensor readings in long format.
2. Extract domain-specific vibration features + tsfresh defaults.
3. Select relevant features.
4. Train predictive maintenance classifier.
