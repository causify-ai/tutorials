import subprocess
import boto3
import pandas as pd

# 🧠 Load your forecast DataFrame
from analyze_traces import hourly_latency_forecast_df as df  # or replace with in-memory

# ✅ Get SNS Topic ARN dynamically from CDK output
def get_sns_topic_arn():
    result = subprocess.check_output(
        ["cdk", "output", "SnsAlertStack.SnsTopicArnOutput"]
    )
    return result.decode().strip()

topic_arn = get_sns_topic_arn()
sns = boto3.client("sns")

LATENCY_THRESHOLD = 100
alerts = df[df["yhat"] > LATENCY_THRESHOLD]

for _, row in alerts.iterrows():
    message = (
        f"⚠️ High predicted latency alert\n"
        f"Timestamp: {row['ds']}\n"
        f"Predicted Latency: {round(row['yhat'], 2)} ms"
    )
    sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject="🚨 High Latency Prediction Alert"
    )
    print(f"📤 Alert sent for {row['ds']}")
