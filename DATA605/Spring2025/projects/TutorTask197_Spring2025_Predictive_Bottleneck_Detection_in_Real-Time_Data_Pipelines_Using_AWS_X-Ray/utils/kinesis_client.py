import boto3

def create_kinesis_client(region_name='us-east-1'):
    """
    Create a boto3 Kinesis client.
    """
    return boto3.client('kinesis', region_name=region_name)
