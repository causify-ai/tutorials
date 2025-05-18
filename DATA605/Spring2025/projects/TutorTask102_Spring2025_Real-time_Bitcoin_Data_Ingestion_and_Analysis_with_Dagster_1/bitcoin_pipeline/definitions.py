from dagster import Definitions
from bitcoin_pipeline.jobs import bitcoin_analysis_job
from bitcoin_pipeline.schedules import bitcoin_price_schedule

defs = Definitions(
    jobs=[bitcoin_analysis_job],
    schedules=[bitcoin_price_schedule],
)
