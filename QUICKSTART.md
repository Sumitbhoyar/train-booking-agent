# Train Booking API - Quick Start Guide

## Prerequisites Checklist

- [ ] AWS Account with admin access
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Python 3.13+ installed (or 3.12+)
- [ ] Docker installed and running
- [ ] Node.js 18+ (for AWS CDK)

## Quick Setup (5 minutes)

### Option 1: Automated Deployment (Linux/Mac)

```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Automated Deployment (Windows)

```powershell
.\deploy.ps1
```

### Option 3: Manual Deployment

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install CDK dependencies
cd infrastructure
pip install -r requirements.txt

# 3. Bootstrap CDK (first time only)
cdk bootstrap

# 4. Deploy infrastructure
cdk deploy --all

# 5. Note the outputs (API URL, Agent IDs)
```

## Testing Your Deployment

### 1. Test REST API

```bash
# Replace <API-URL> with your deployed API URL from outputs

# Health check
curl https://<API-URL>/health

# Get all trains
curl https://<API-URL>/trains/all

# Search trains
curl "https://<API-URL>/trains?origin=Paris&destination=Lyon&date=2025-12-27"

# Create booking
curl -X POST https://<API-URL>/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "train_number": "T101",
    "passenger_name": "John Doe",
    "email": "john.doe@example.com",
    "journey_date": "2025-12-27"
  }'

# Get booking (replace {booking_id} with actual ID from previous response)
curl https://<API-URL>/bookings/{booking_id}

# Cancel booking
curl -X DELETE https://<API-URL>/bookings/{booking_id}

# Export booking as PDF
curl -O https://<API-URL>/bookings/{booking_id}/pdf
```

### 2. Test Bedrock Agent

1. Go to AWS Console → Amazon Bedrock → Agents
2. Find "train-booking-agent"
3. Click "Test" button
4. Try these prompts:

```
"Show me trains from Paris to Lyon on December 27th"
"Book a ticket for Jane Smith on train T101 for December 27, 2025. Email is jane@example.com"
"What's the status of booking BK12345?" (use actual booking ID)
"Cancel booking BK12345" (use actual booking ID)
"Export my booking BK12345 as PDF" (NEW! - Returns download URL)
```

## API Documentation

Once deployed, visit:
- Swagger UI: `https://<API-URL>/docs`
- ReDoc: `https://<API-URL>/redoc`

## Available Trains

The system includes 5 pre-configured trains:

| Train | Route | Time | Seats |
|-------|-------|------|-------|
| T101 | Paris → Lyon | 08:00 | 50 |
| T102 | Paris → Marseille | 09:30 | 45 |
| T103 | Lyon → Paris | 22:00 | 60 |
| T104 | Marseille → Paris | 06:00 | 40 |
| T105 | Paris → Nice | 14:00 | 55 |

## Common Commands

```bash
# View Lambda logs
aws logs tail /aws/lambda/train-booking-api --follow

# View Agent logs
aws logs tail /aws/lambda/train-booking-action-group --follow

# Update deployment
cd infrastructure
cdk deploy --all

# Destroy everything
cd infrastructure
cdk destroy --all
```

## Troubleshooting

### Docker Build Issues
```bash
# Ensure Docker is running
docker info

# Test local build
docker build -t train-booking-api .
```

### CDK Bootstrap Issues
```bash
# Re-bootstrap with specific region
cdk bootstrap aws://ACCOUNT-ID/REGION
```

### Lambda Timeout
- Check CloudWatch logs
- Increase timeout in `infrastructure/stacks/api_stack.py`

### Bedrock Agent Not Responding
- Ensure agent is "Prepared" in console
- Check action group Lambda logs
- Verify IAM permissions

## Cost Estimate

For light usage (100 requests/day):
- Lambda: ~$0.20/month
- API Gateway: ~$0.10/month
- Bedrock (Claude 3.5 Sonnet v2): ~$1-5/month (varies by usage)
- **Total: ~$1-6/month**

## Next Steps

1. ✅ Deploy the infrastructure
2. ✅ Test REST API endpoints
3. ✅ Test Bedrock Agent
4. ✅ Try PDF export feature
5. 🔄 Customize train data
6. 🔄 Add more features (payment, notifications)
7. 🔄 Integrate with real database (DynamoDB)
8. 🔄 Add authentication (Cognito)

## Support

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS CDK Python](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)

---

**Happy Coding! 🚂✨**

