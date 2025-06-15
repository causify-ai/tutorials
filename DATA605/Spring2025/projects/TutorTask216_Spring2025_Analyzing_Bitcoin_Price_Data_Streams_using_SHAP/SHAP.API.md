# SHAP API Tutorial

This markdown file documents key functionalities of the SHAP Python library and serves as a companion to the `SHAP.API.ipynb` tutorial notebook. It provides a high-level overview of available SHAP explainers and visual tools for interpreting machine learning model predictions.

## Table of Contents

The structure mirrors the SHAP API walkthrough provided in the notebook, covering both explainer initialization and output interpretation.

<!-- toc -->

- [SHAP API Tutorial](#shap-api-tutorial)
  - [Table of Contents](#table-of-contents)
    - [Hierarchy](#hierarchy)
  - [General Guidelines](#general-guidelines)
- [1. Overview](#1-overview)
- [2. SHAP Explainers Covered](#2-shap-explainers-covered)
- [3. Visualization Functions](#3-visualization-functions)
  - [3.1 `summary_plot()`](#31-summary_plot)
  - [3.2 `dependence_plot()`](#32-dependence_plot)
  - [3.3 `force_plot()`](#33-force_plot)
  - [3.4 `decision_plot()`](#34-decision_plot)
- [4. Model Types Supported](#4-model-types-supported)
- [5. Usage Example (Notebook)](#5-usage-example-notebook)
- [6. Future Improvements](#6-future-improvements)

<!-- tocstop -->

### Hierarchy

```
# Level 1 (Used as title)
## Level 2
### Level 3
```

## General Guidelines

- This documentation complements `SHAP.API.ipynb`.
- It focuses on explaining SHAP’s official Python API.
- All functions shown are directly usable via the `shap` Python package.

---

## 1. Overview

The SHAP library offers model interpretability by attributing prediction outcomes to input features using Shapley values from game theory. This project uses SHAP to:

- Explain both global and local model behavior
- Visualize prediction drivers
- Support both tree-based and black-box models
- Extend explanations to image and text data

---

## 2. SHAP Explainers Covered

| Explainer                | Use Case                                      |
| ------------------------ | --------------------------------------------- |
| `TreeExplainer`          | Fast and exact SHAP values for tree models    |
| `KernelExplainer`        | Model-agnostic explanations (any ML model)    |
| `DeepExplainer`          | Explaining deep learning models (e.g. CNNs)   |
| `Explainer` (text/image) | General entry point for modern SHAP workflows |

---

## 3. Visualization Functions

### 3.1 `summary_plot()`

Summarizes global feature importance using SHAP values across all instances.

### 3.2 `dependence_plot()`

Shows how a single feature's value affects its SHAP contribution, and highlights interactions.

### 3.3 `force_plot()`

Visualizes SHAP values for one or multiple predictions — great for local explanation.

### 3.4 `decision_plot()`

Tracks how model decisions accumulate over features for one or many predictions.

---

## 4. Model Types Supported

- XGBoost, LightGBM, CatBoost (via `TreeExplainer`)
- Any sklearn-compatible model (via `KernelExplainer`)
- Deep learning models in TensorFlow/Keras (via `DeepExplainer`)
- Text and image models using SHAP’s modern `Explainer` interface

---

## 5. Usage Example (Notebook)

The notebook `SHAP.API.ipynb` demonstrates:

- Training a classifier (XGBoost, MLP)
- Creating SHAP explainers for different model types
- Generating summary, force, dependence, decision, and interaction plots
- Explaining predictions on tabular, image, and text data

---

## 6. Future Improvements

- Move reusable logic into a centralized `SHAP_utils.py`
- Add support for multi-class interpretation tools
- Integrate SHAP value aggregation across folds for cross-validation
- Add CLI-based interface for batch SHAP runs
