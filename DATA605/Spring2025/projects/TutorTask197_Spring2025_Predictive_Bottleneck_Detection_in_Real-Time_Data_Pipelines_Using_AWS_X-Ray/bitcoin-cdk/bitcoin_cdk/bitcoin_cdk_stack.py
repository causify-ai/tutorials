from aws_cdk import (
    # Duration,
    Stack,
    aws_kinesis as kinesis,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as sources,
    RemovalPolicy,
    Duration,
)
from constructs import Construct

class BitcoinCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Create Kinesis stream
        stream = kinesis.Stream(
            self, 
            "BitcoinStream",
            stream_name="bitcoin-stream",
            shard_count=1,
            retention_period=Duration.hours(24),
        )

        # Create S3 bucket
        bucket = s3.Bucket(
            self, 
            "BitcoinBucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Create DynamoDB table
        table = dynamodb.Table(
            self, 
            "BitcoinAggregationTable",
            table_name="BitcoinAggregation",
            partition_key=dynamodb.Attribute(
                name="id", 
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Create Lambda function
        lambda_function = _lambda.Function(
            self, 
            "BitcoinLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "TABLE_NAME": table.table_name
            },
            timeout=Duration.seconds(30),
        )

        # Add Kinesis stream as event source for Lambda
        lambda_function.add_event_source(sources.KinesisEventSource(
            stream,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=1,
        ))

        # Grant permissions
        bucket.grant_put(lambda_function)
        stream.grant_read(lambda_function)
        table.grant_read_write_data(lambda_function)
