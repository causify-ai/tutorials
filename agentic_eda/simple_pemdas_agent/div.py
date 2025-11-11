"""Division helper for the simple BEDMAS agent."""

from __future__ import annotations


def run(a: float, b: float) -> float:
    """Return the quotient of two operands rounded to two decimals.

    :param a: Numerator operand.
    :param b: Denominator operand.
    :return: Rounded quotient `a / b`.
    """
    return round(a / b, 2)
