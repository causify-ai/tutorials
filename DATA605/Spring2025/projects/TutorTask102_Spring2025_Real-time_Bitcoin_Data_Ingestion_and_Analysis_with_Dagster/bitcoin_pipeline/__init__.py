from dagster import Definitions
from .jobs import bitcoin_analysis_job

defs = Definitions(jobs=[bitcoin_analysis_job])
