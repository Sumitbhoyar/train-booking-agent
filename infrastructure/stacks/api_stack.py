"""API Stack - Lambda and API Gateway Infrastructure"""
from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigwv2,
    aws_ecr_assets as ecr_assets,
    aws_logs as logs,
)
from constructs import Construct
import os


class ApiStack(Stack):
    """Stack for Train Booking REST API"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Build Docker image for Lambda
        docker_image = ecr_assets.DockerImageAsset(
            self,
            "TrainBookingApiImage",
            directory=os.path.join(os.path.dirname(__file__), "../.."),
            file="Dockerfile",
            platform=ecr_assets.Platform.LINUX_AMD64
        )

        # Create Lambda function from Docker image
        self.api_function = lambda_.DockerImageFunction(
            self,
            "TrainBookingApiFunction",
            code=lambda_.DockerImageCode.from_ecr(
                repository=docker_image.repository,
                tag_or_digest=docker_image.image_tag
            ),
            function_name="train-booking-api",
            description="Train Booking REST API with FastAPI",
            timeout=Duration.seconds(30),
            memory_size=512,
            architecture=lambda_.Architecture.X86_64,
            log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                "LOG_LEVEL": "INFO"
            }
        )

        # Create HTTP API (API Gateway v2)
        http_api = apigwv2.HttpApi(
            self,
            "TrainBookingHttpApi",
            api_name="train-booking-api",
            description="Train Booking REST API Gateway",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_methods=[
                    apigwv2.CorsHttpMethod.GET,
                    apigwv2.CorsHttpMethod.POST,
                    apigwv2.CorsHttpMethod.DELETE,
                    apigwv2.CorsHttpMethod.OPTIONS
                ],
                allow_origins=["*"],
                allow_headers=["*"]
            )
        )

        # Add Lambda integration
        lambda_integration = apigwv2.HttpLambdaIntegration(
            "LambdaIntegration",
            handler=self.api_function,
            payload_format_version=apigwv2.PayloadFormatVersion.VERSION_2_0
        )

        # Add catch-all route
        http_api.add_routes(
            path="/{proxy+}",
            methods=[
                apigwv2.HttpMethod.GET,
                apigwv2.HttpMethod.POST,
                apigwv2.HttpMethod.DELETE,
                apigwv2.HttpMethod.PUT,
                apigwv2.HttpMethod.PATCH
            ],
            integration=lambda_integration
        )

        # Add root route
        http_api.add_routes(
            path="/",
            methods=[apigwv2.HttpMethod.GET],
            integration=lambda_integration
        )

        # Outputs
        CfnOutput(
            self,
            "ApiUrl",
            value=http_api.url,
            description="Train Booking API URL",
            export_name="TrainBookingApiUrl"
        )

        CfnOutput(
            self,
            "LambdaFunctionArn",
            value=self.api_function.function_arn,
            description="Lambda Function ARN",
            export_name="TrainBookingApiFunctionArn"
        )

        CfnOutput(
            self,
            "LambdaFunctionName",
            value=self.api_function.function_name,
            description="Lambda Function Name",
            export_name="TrainBookingApiFunctionName"
        )

