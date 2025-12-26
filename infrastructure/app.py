#!/usr/bin/env python3
"""AWS CDK App Entry Point"""
import aws_cdk as cdk
from stacks.api_stack import ApiStack
from stacks.agent_stack import AgentStack

app = cdk.App()

# Deploy API Stack (Lambda + API Gateway)
api_stack = ApiStack(
    app, 
    "TrainBookingApiStack",
    description="Train Booking REST API with Lambda and API Gateway"
)

# Deploy Agent Stack (Bedrock Agent)
agent_stack = AgentStack(
    app,
    "TrainBookingAgentStack",
    description="AWS Bedrock Agent for Train Booking"
)

# Add dependencies
agent_stack.add_dependency(api_stack)

app.synth()

