from aws_cdk import (
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    Stack,
    CfnOutput
)
from constructs import Construct

class SnsAlertStack(Stack):

    def __init__(self, scope: Construct, id: str, email_address: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # SNS Topic for latency alerts
        self.latency_alert_topic = sns.Topic(
            self, "LatencyAlertTopic",
            topic_name="HighLatencyAlerts"
        )

        # Add email subscription
        self.latency_alert_topic.add_subscription(
            subscriptions.EmailSubscription(email_address)
        )

        # Output the topic ARN so it can be referenced in scripts or other stacks
        CfnOutput(
            self, "SnsTopicArnOutput",
            value=self.latency_alert_topic.topic_arn,
            description="ARN of the SNS topic for latency alerts"
        )
