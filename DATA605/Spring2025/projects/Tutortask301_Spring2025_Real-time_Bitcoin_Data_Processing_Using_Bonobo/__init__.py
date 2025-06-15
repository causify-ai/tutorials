"""
Package initializer for Real-time Bitcoin Data Processing using Bonobo.

This __init__.py file allows the project to be used as a package.
It exposes the BitcoinPipeline API and optionally defines shortcuts for execution.
"""

from .bitcoin_API import BitcoinPipeline

__all__ = ["BitcoinPipeline"]
