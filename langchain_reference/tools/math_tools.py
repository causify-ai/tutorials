from __future__ import annotations

from typing import Sequence
from math import sqrt
from langchain.tools import tool

def _as_floats(xs: Sequence[float]) -> list[float]:
    # Defensive conversion & validation (deterministic)
    if xs is None:
        raise ValueError("xs must not be None")
    xs_list = [float(x) for x in xs]
    if len(xs_list) == 0:
        raise ValueError("xs must be non-empty")
    return xs_list

@tool
def mean(xs: Sequence[float]) -> float:
    """Compute the arithmetic mean of a non-empty list of numbers.

    Args:
        xs: Sequence of numeric values. Must be non-empty.

    Returns:
        The arithmetic mean as a float.
    """
    xs_list = _as_floats(xs)
    return sum(xs_list) / len(xs_list)

@tool
def zscore(xs: Sequence[float], x: float) -> float:
    """Compute the z-score of value x relative to sample xs.

    z = (x - mean(xs)) / std(xs)

    Args:
        xs: Reference sample. Must be non-empty.
        x: The value to normalize.

    Returns:
        z-score as a float.

    Raises:
        ValueError: if sample std is 0 (constant sample).
    """
    xs_list = _as_floats(xs)
    mu = sum(xs_list) / len(xs_list)
    var = sum((v - mu) ** 2 for v in xs_list) / len(xs_list)
    std = sqrt(var)
    if std == 0.0:
        raise ValueError("std(xs) is 0; z-score undefined for constant sample")
    return (float(x) - mu) / std
