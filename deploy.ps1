# Deploy Script for Train Booking API (Windows)

Write-Host "🚀 Starting deployment of Train Booking API..." -ForegroundColor Green

# Check if AWS CLI is configured
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✅ AWS CLI is configured" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI is not configured. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Install CDK dependencies
Write-Host "📦 Installing CDK dependencies..." -ForegroundColor Yellow
Set-Location infrastructure
pip install -r requirements.txt

# Bootstrap CDK if needed
Write-Host "🔧 Bootstrapping CDK (if not already done)..." -ForegroundColor Yellow
cdk bootstrap

# Deploy stacks
Write-Host "☁️ Deploying infrastructure stacks..." -ForegroundColor Yellow
cdk deploy --all --require-approval never

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Check the outputs above for API URL and Agent IDs"
Write-Host "2. Test the REST API endpoints"
Write-Host "3. Test the Bedrock Agent in AWS Console"
Write-Host ""
Write-Host "🔗 Useful commands:" -ForegroundColor Cyan
Write-Host "  - Test API: curl <API-URL>/health"
Write-Host "  - View logs: aws logs tail /aws/lambda/train-booking-api --follow"
Write-Host "  - Update code: cdk deploy --all"
Write-Host "  - Cleanup: cdk destroy --all"

