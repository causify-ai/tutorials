import json
import base64
import boto3
import joblib
import numpy as np
import os

# Load model once
model_path = os.path.join(os.path.dirname(__file__), "isolation_forest_model.pkl")
model = joblib.load(model_path)

sns = boto3.client("sns")
TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):
    for record in event["Records"]:
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        data = json.loads(payload)

        price = data.get("price")
        volume = data.get("volume")

        if price is not None and volume is not None:
            features = np.array([[price, volume]])
            result = model.predict(features)

            if result[0] == -1:
                alert = f"Anomaly Detected! Price: {price}, Volume: {volume}"
                sns.publish(TopicArn=TOPIC_ARN, Message=alert)

    return {"statusCode": 200, "body": "Processed"}
