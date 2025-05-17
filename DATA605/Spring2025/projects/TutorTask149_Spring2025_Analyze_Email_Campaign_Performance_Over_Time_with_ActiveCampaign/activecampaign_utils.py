import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from pycaret.classification import setup, compare_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_data(df: pd.DataFrame, target_column: str, test_size: float = 0.2):
    logger.info(\"Splitting data into train and test sets\")
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=42)

def run_pycaret_classification(df: pd.DataFrame, target_column: str):
    logger.info(\"Running PyCaret classification setup\")
    s = setup(df, target=target_column, silent=True, verbose=False)
    return compare_models()

