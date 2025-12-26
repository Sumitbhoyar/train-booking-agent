#!/bin/bash

# Deploy Script for Train Booking API

set -e

echo "🚀 Starting deployment of Train Booking API..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Prerequisites checked"

# Install CDK dependencies
echo "📦 Installing CDK dependencies..."
cd infrastructure
pip install -r requirements.txt

# Bootstrap CDK if needed
echo "🔧 Bootstrapping CDK (if not already done)..."
cdk bootstrap

# Deploy stacks
echo "☁️ Deploying infrastructure stacks..."
cdk deploy --all --require-approval never

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Check the outputs above for API URL and Agent IDs"
echo "2. Test the REST API endpoints"
echo "3. Test the Bedrock Agent in AWS Console"
echo ""
echo "🔗 Useful commands:"
echo "  - Test API: curl <API-URL>/health"
echo "  - View logs: aws logs tail /aws/lambda/train-booking-api --follow"
echo "  - Update code: cdk deploy --all"
echo "  - Cleanup: cdk destroy --all"

