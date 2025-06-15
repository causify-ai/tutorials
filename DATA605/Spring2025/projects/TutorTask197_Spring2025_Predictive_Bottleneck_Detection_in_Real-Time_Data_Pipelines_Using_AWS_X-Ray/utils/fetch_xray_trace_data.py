import json
import boto3
import pandas as pd
from datetime import datetime, timedelta

xray = boto3.client('xray')

def fetch_today_trace_data():
    all_trace_data = []

    start_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = datetime.utcnow()

    summaries = []
    next_token = None
    while True:
        response = xray.get_trace_summaries(
            StartTime=start_time,
            EndTime=end_time,
            Sampling=False,
            NextToken=next_token if next_token else ''
        )
        summaries.extend(response['TraceSummaries'])
        next_token = response.get('NextToken')
        if not next_token:
            break

    trace_ids = [trace['Id'] for trace in summaries]

    def extract_annotated_subsegments(doc, trace_id):
        results = []
        if 'subsegments' in doc:
            for sub in doc['subsegments']:
                if 'annotations' in sub:
                    annotations = sub['annotations']
                    results.append({
                        'trace_id': trace_id,
                        'timestamp': datetime.utcfromtimestamp(doc.get('start_time')),
                        'flag': annotations.get('flag'),
                        'price_usd': annotations.get('price_usd'),
                        'processing_time_ms': annotations.get('processing_time_ms'),
                        'shard_id': annotations.get('shard_id'),
                        'error': annotations.get('error'),
                        'hour_str': annotations.get('hour_str'),
                        'data_volume_bytes': annotations.get('data_volume_bytes')
                    })
                results.extend(extract_annotated_subsegments(sub, trace_id))
        return results

    for i in range(0, len(trace_ids), 5):
        batch = trace_ids[i:i + 5]
        response = xray.batch_get_traces(TraceIds=batch)
        for trace in response['Traces']:
            for segment_doc in trace.get('Segments', []):
                doc = json.loads(segment_doc['Document'])
                all_trace_data.extend(extract_annotated_subsegments(doc, trace['Id']))

    df = pd.DataFrame(all_trace_data)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour_str'] = pd.to_datetime(df['hour_str'])
        df = df.sort_values('hour_str')
    return df
