import json
import base64
import boto3
import joblib
import numpy as np
import os

# Load model once
model_path = os.path.join(os.path.dirname(__file__), "isolation_forest_model.pkl")
scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

sns = boto3.client("sns")
TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
firehose = boto3.client("firehose")
FIREHOSE_NAME = "btc-firehose-anomalies"
ANOMALY_SCORE_THRESHOLD = -0.001

def lambda_handler(event, context):
    for record in event["Records"]:
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        data = json.loads(payload)

        price = data.get("price")
        volume = data.get("volume")

        if price is not None and volume is not None:
            features = np.array([[price, volume]])
            scaled = scaler.transform(features)
            result = model.predict(features)
            # Get anomaly score
            score = model.decision_function(scaled)[0]

            if score < ANOMALY_SCORE_THRESHOLD:
                alert = f"Anomaly Detected! Price: {price}, Volume: {volume}"
                sns.publish(TopicArn=TOPIC_ARN, Message=alert)
                # Send to Firehose
                firehose.put_record(
                    DeliveryStreamName=FIREHOSE_NAME,
                    Record={"Data": json.dumps(alert) + "\n"}
                )

    return {"statusCode": 200, "body": "Processed"}
