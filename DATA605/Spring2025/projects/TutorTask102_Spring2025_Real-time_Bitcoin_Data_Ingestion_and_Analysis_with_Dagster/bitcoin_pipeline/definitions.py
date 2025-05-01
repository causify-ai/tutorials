from dagster import Definitions
from .jobs import bitcoin_price_pipeline
from .schedules import bitcoin_price_schedule  # <- import the actual schedule, not a list

defs = Definitions(
    jobs=[bitcoin_price_pipeline],
    schedules=[bitcoin_price_schedule],  # <- wrap it in a list here
)