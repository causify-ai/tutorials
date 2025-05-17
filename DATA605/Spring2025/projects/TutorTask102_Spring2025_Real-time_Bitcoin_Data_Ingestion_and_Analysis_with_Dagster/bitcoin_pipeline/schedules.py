from dagster import ScheduleDefinition  # ✅ Correct import
from bitcoin_pipeline.jobs import bitcoin_analysis_job  # 🔁 Use full path if not relative

bitcoin_price_schedule = ScheduleDefinition(
    job=bitcoin_analysis_job,
    cron_schedule="*/5 * * * *",  # Every 5 minutes
)
