#!/usr/bin/env python3
import os

import aws_cdk as cdk

from bitcoin_cdk.bitcoin_cdk_stack import BitcoinCdkStack
from bitcoin_cdk.sns_alert_stack import SnsAlertStack

app = cdk.App()

env=cdk.Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION"))

# Deploy the Bitcoin stack
BitcoinCdkStack(
    app,
    "BitcoinCdkStack", 
    env=env
)

# Deploy the SNS alert stack
SnsAlertStack(
    app,
    "SnsAlertStack",
    email_address="gourav@umd.edu",
    env=env
)

app.synth()