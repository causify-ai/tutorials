"""
template_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
"""

import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from pycaret.classification import compare_models

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Example 1: Split the dataset into train and test sets
# -----------------------------------------------------------------------------

def split_data(df: pd.DataFrame, target_column: str, test_size: float = 0.2):
    """
    Split the dataset into training and testing sets.

    :param df: full dataset
    :param target_column: name of the target column
    :param test_size: proportion of test data (default = 0.2)

    :return: X_train, X_test, y_train, y_test
    """
    logger.info("Splitting data into train and test sets")
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=42)

# -----------------------------------------------------------------------------
# Example 2: PyCaret classification pipeline
# -----------------------------------------------------------------------------

def run_pycaret_classification(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
    """
    Run a basic PyCaret classification experiment.

    :param df: dataset containing features and target
    :param target_column: name of the target column

    :return: comparison of top-performing models
    """
    logger.info("Initializing PyCaret classification setup")
    ...

    logger.info("Comparing models")
    results = compare_models()
    ...

    return results


