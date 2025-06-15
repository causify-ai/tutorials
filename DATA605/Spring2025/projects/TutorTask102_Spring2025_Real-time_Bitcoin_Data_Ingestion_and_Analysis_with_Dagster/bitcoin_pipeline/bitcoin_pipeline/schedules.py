from dagster import ScheduleDefinition
from .jobs import bitcoin_analysis_job

bitcoin_price_schedule = ScheduleDefinition(
    job=bitcoin_analysis_job,
    cron_schedule="*/5 * * * *",  # Every 5 minutes
)
