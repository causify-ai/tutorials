import os, io, json, pickle
import boto3, pandas as pd
from prophet import Prophet
from datetime import datetime, timedelta
import numpy as np
RAW_BUCKET   = os.environ['RAW_BUCKET']
MODEL_BUCKET = os.environ['MODEL_BUCKET']
s3 = boto3.client('s3')

def handler(event, context):
    # 1) Gather last 7 days of raw data
    cutoff = datetime.utcnow() - timedelta(days=7)
    objs = s3.list_objects_v2(Bucket=RAW_BUCKET).get('Contents',[])
    rows = []
    for o in objs:
        ts = datetime.fromisoformat(o['Key'].split('.')[0])
        if ts > cutoff:
            data = json.loads(s3.get_object(Bucket=RAW_BUCKET,Key=o['Key'])['Body'].read())
            rows.append({'ds': ts, 'y': data['price']})
    df = pd.DataFrame(rows)
    # 2) Train Prophet
    m = Prophet()
    m.fit(df)
    buf = io.BytesIO()
    pickle.dump(m, buf)
    buf.seek(0)
    # 3) Upload model artifact
    s3.put_object(Bucket=MODEL_BUCKET,
                  Key='model.pkl',
                  Body=buf.read())
    
