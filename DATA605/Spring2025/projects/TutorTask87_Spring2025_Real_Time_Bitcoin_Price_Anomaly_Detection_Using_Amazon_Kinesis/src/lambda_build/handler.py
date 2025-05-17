import json, base64
import boto3, os


sns = boto3.client("sns")
TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
firehose = boto3.client("firehose")
FIREHOSE_NAME = "btc-firehose-anomalies"
def lambda_handler(event, context):
    for record in event["Records"]:
        payload = json.loads(base64.b64decode(record["kinesis"]["data"]))
        print("ANOMALY RECORD:", payload)
        data = json.loads(payload)

        price = data.get("price")
        volume = data.get("volume")

        alert = f"Anomaly Detected! Price: {price}, Volume: {volume}"
        sns.publish(TopicArn=TOPIC_ARN, Message=alert)
        # Send to Firehose
        firehose.put_record(
            DeliveryStreamName=FIREHOSE_NAME,
            Record={"Data": json.dumps(alert) + "\n"}
        )