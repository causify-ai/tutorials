from setuptools import setup, find_packages

setup(
    name="bitcoin-forecast",
    version="0.1.0",
    description="Time-series forecasting for Bitcoin prices using TensorFlow Probability",
    author="Your Name",
    python_requires=">=3.10,<3.11",
    packages=find_packages(),            # finds src/, mains/, utilities/, etc.
    include_package_data=True,           # pick up any package_data
    install_requires=[
        # core ML
        "tensorflow==2.18.0",
        "tensorflow-probability[tf]==0.25.0",
        # data handling
        "pandas>=2.0.0",
        "numpy>=1.23.5,<2.0.0",
        # visualization
        "matplotlib>=3.5.0",
        "seaborn>=0.12.0",
        # HTTP client & streaming
        "requests>=2.28.0",
        "websockets>=15.0.1",
        # config + utilities
        "PyYAML>=6.0",
        # bitcoin data
        "yfinance==0.2.57",
    ],
    entry_points={
        "console_scripts": [
            # so you can run `run_history` or `run_instant` directly
            "run_history = mains.run_history:main",
            "run_instant = mains.run_instant:main",
        ],
    },
)