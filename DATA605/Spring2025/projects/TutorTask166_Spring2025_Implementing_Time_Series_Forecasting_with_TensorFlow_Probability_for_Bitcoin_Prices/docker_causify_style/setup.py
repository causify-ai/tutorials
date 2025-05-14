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
        "pandas==2.2.1",
        "numpy==1.26.4",
        "scikit-learn",
        # visualization
        "matplotlib==3.8.3",
        "seaborn==0.13.2",
        "plotly==5.19.0",
        "streamlit==1.32.2",
        # HTTP client & streaming
        "requests==2.31.0",
        "websockets==12.0",
        "kafka-python==2.0.2",
        # config + utilities
        "PyYAML==6.0.1",
        "python-dotenv==1.0.1",
        # bitcoin data
        "yfinance==0.2.36",
    ],
    entry_points={
        "console_scripts": [
            # so you can run `run_history` or `run_instant` directly
            "run_history = mains.run_history:main",
            "run_instant = bitcoin_forecast_app.mains.run_instant:main",
        ],
    },
)