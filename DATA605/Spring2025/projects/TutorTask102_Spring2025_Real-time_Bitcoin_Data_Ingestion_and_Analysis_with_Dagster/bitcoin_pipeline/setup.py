from setuptools import find_packages, setup

setup(
    name="bitcoin_pipeline",
    packages=find_packages(exclude=["bitcoin_pipeline_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "pandas",
        "matplotlib",
        "statsmodels",
        "requests",
        "seaborn",
        "numpy",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
