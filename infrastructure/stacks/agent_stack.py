"""Agent Stack - AWS Bedrock Agent Infrastructure"""
from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_bedrock as bedrock,
    aws_logs as logs,
)
from constructs import Construct
import json
import os


class AgentStack(Stack):
    """Stack for Bedrock Agent and Action Group"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create IAM role for Bedrock Agent
        agent_role = iam.Role(
            self,
            "BedrockAgentRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Role for Train Booking Bedrock Agent"
        )

        # Add permissions to invoke foundation models
        agent_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
                    f"arn:aws:bedrock:{self.region}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
                ]
            )
        )

        # Create Lambda function for action group
        action_group_function = lambda_.Function(
            self,
            "ActionGroupFunction",
            function_name="train-booking-action-group",
            description="Action group Lambda for Bedrock Agent",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="lambda_handler.lambda_handler",
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../../bedrock_agent")
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "LOG_LEVEL": "INFO"
            }
        )

        # Grant Bedrock Agent permission to invoke the Lambda
        action_group_function.grant_invoke(agent_role)

        # Create Bedrock Agent
        agent = bedrock.CfnAgent(
            self,
            "TrainBookingAgent",
            agent_name="train-booking-agent",
            agent_resource_role_arn=agent_role.role_arn,
            foundation_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            instruction="""You are a helpful train booking assistant. Your role is to help users with:
1. Searching for available trains between stations
2. Creating new train bookings
3. Checking the status of existing bookings
4. Cancelling bookings

Always be polite and confirm booking details before finalizing. When showing train options, present them clearly with train number, name, route, departure time, and available seats. For bookings, always confirm the passenger name, email, train details, and journey date before proceeding.""",
            description="AI agent for train booking operations",
            idle_session_ttl_in_seconds=600,
            auto_prepare=True
        )

        # Read OpenAPI schema
        schema_path = os.path.join(
            os.path.dirname(__file__), 
            "../../bedrock_agent/openapi_schema.json"
        )
        with open(schema_path, 'r') as f:
            api_schema = json.load(f)

        # Create Action Group
        action_group = bedrock.CfnAgentActionGroup(
            self,
            "TrainBookingActionGroup",
            action_group_name="train-booking-actions",
            agent_id=agent.attr_agent_id,
            agent_version="DRAFT",
            description="Action group for train booking operations",
            action_group_executor=bedrock.CfnAgentActionGroup.ActionGroupExecutorProperty(
                lambda_=action_group_function.function_arn
            ),
            api_schema=bedrock.CfnAgentActionGroup.APISchemaProperty(
                payload=json.dumps(api_schema)
            )
        )

        # Add Lambda resource-based policy for Bedrock
        action_group_function.add_permission(
            "BedrockInvokePermission",
            principal=iam.ServicePrincipal("bedrock.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=f"arn:aws:bedrock:{self.region}:{self.account}:agent/{agent.attr_agent_id}"
        )

        # Create Agent Alias
        agent_alias = bedrock.CfnAgentAlias(
            self,
            "TrainBookingAgentAlias",
            agent_alias_name="production",
            agent_id=agent.attr_agent_id,
            description="Production alias for Train Booking Agent"
        )

        # Ensure action group is created before alias
        agent_alias.add_dependency(action_group)

        # Outputs
        CfnOutput(
            self,
            "AgentId",
            value=agent.attr_agent_id,
            description="Bedrock Agent ID",
            export_name="TrainBookingAgentId"
        )

        CfnOutput(
            self,
            "AgentAliasId",
            value=agent_alias.attr_agent_alias_id,
            description="Bedrock Agent Alias ID",
            export_name="TrainBookingAgentAliasId"
        )

        CfnOutput(
            self,
            "ActionGroupLambdaArn",
            value=action_group_function.function_arn,
            description="Action Group Lambda Function ARN",
            export_name="ActionGroupLambdaArn"
        )

