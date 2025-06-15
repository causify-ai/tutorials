from dagster import Definitions
from .jobs import bitcoin_analysis_job
from .schedules import bitcoin_price_schedule

defs = Definitions(
    jobs=[bitcoin_analysis_job],
    schedules=[bitcoin_price_schedule],
)
