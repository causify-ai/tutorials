from dagster import ScheduleDefinition
from .jobs import bitcoin_price_pipeline

bitcoin_price_schedule = ScheduleDefinition(
    job=bitcoin_price_pipeline,
    cron_schedule="*/5 * * * *",  # Every 5 minutes
)

schedules = [bitcoin_price_schedule]
