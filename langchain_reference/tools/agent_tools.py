from __future__ import annotations
from langchain.tools import tool
from datetime import datetime, timezone
import math

@tool
def utc_now() -> str:
    """Return the current time in UTC as an ISO string."""
    return datetime.now(timezone.utc).isoformat()

@tool
def mean(xs: list[float]) -> float:
    """Return the arithmetic mean of a non-empty list of numbers."""
    if not xs:
        raise ValueError("xs must be non-empty")
    return sum(xs) / len(xs)

@tool
def sqrt(x: float) -> float:
    """Return sqrt(x). x must be >= 0."""
    if x < 0:
        raise ValueError("x must be >= 0")
    return math.sqrt(x)
