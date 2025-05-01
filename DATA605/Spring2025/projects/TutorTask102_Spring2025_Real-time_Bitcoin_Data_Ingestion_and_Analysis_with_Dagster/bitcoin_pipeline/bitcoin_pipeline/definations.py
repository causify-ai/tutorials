from dagster import Definitions
from .jobs import bitcoin_price_pipeline
from .schedules import schedules

defs = Definitions(
    jobs=[bitcoin_price_pipeline],
    schedules=schedules,
)