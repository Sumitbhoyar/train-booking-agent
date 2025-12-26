# Train Booking REST API with AWS Bedrock Agent

A serverless train booking system built with FastAPI, AWS Lambda, API Gateway, and AWS Bedrock Agent for conversational booking management.

## 🏗️ Architecture

- **AWS Lambda**: Hosts the FastAPI application as a containerized function
- **API Gateway**: HTTP API (v2) for REST endpoints
- **Amazon Bedrock Agent**: Conversational AI interface using Claude 3 Sonnet
- **AWS CDK**: Infrastructure as Code for deployment
- **In-Memory Database**: Python dictionaries for demo purposes

## 📁 Project Structure

```
train-booking-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with Mangum adapter
│   ├── models.py            # Pydantic models
│   ├── database.py          # In-memory data store
│   └── routers/
│       ├── trains.py        # Train search endpoints
│       └── bookings.py      # Booking CRUD endpoints
├── bedrock_agent/
│   ├── lambda_handler.py    # Action group Lambda handler
│   └── openapi_schema.json  # API schema for action group
├── infrastructure/
│   ├── app.py               # CDK app entry point
│   ├── requirements.txt     # CDK dependencies
│   └── stacks/
│       ├── api_stack.py     # Lambda + API Gateway
│       └── agent_stack.py   # Bedrock agent resources
├── Dockerfile
├── requirements.txt
├── cdk.json
└── README.md
```

## 🚀 REST API Endpoints

### Train Search
- `GET /trains` - Search trains by origin, destination, and date
- `GET /trains/all` - Get all available trains
- `GET /trains/{train_number}` - Get specific train details

### Bookings
- `POST /bookings` - Create a new booking
- `GET /bookings/{booking_id}` - Get booking status
- `DELETE /bookings/{booking_id}` - Cancel a booking

### Health
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API info

## 🤖 Bedrock Agent Actions

The Bedrock Agent supports conversational interactions for:
- **searchTrains**: Find available trains by route and date
- **createBooking**: Book a train ticket
- **getBookingStatus**: Check booking details
- **cancelBooking**: Cancel existing reservation

## 📦 Prerequisites

- Python 3.12+
- AWS Account with appropriate permissions
- AWS CLI configured
- Docker installed
- Node.js (for AWS CDK)

## 🛠️ Local Development

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install CDK dependencies
cd infrastructure
pip install -r requirements.txt
cd ..
```

### 2. Run Locally (Optional)

```bash
# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.

## ☁️ AWS Deployment

### 1. Bootstrap CDK (First Time Only)

```bash
cd infrastructure
cdk bootstrap
```

### 2. Deploy Stacks

```bash
# Deploy all stacks
cdk deploy --all

# Or deploy individually
cdk deploy TrainBookingApiStack
cdk deploy TrainBookingAgentStack
```

### 3. Get Outputs

After deployment, note the outputs:
- **ApiUrl**: REST API endpoint URL
- **AgentId**: Bedrock Agent ID
- **AgentAliasId**: Agent alias for testing

## 🧪 Testing

### REST API Testing

```bash
# Health check
curl https://<api-url>/health

# Search trains
curl "https://<api-url>/trains?origin=Paris&destination=Lyon&date=2025-12-27"

# Create booking
curl -X POST https://<api-url>/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "train_number": "T101",
    "passenger_name": "John Doe",
    "email": "john@example.com",
    "journey_date": "2025-12-27"
  }'

# Get booking status
curl https://<api-url>/bookings/{booking_id}

# Cancel booking
curl -X DELETE https://<api-url>/bookings/{booking_id}
```

### Bedrock Agent Testing

Test through AWS Console (Bedrock > Agents > Test):

1. "Show me trains from Paris to Lyon on December 27th"
2. "Book a ticket for John Doe on train T101 for December 27th, email john@example.com"
3. "What's the status of booking BK12345?"
4. "Cancel my booking BK12345"

## 📊 Sample Data

The system comes pre-loaded with 5 sample trains:
- **T101**: Paris → Lyon (08:00, 50 seats)
- **T102**: Paris → Marseille (09:30, 45 seats)
- **T103**: Lyon → Paris (22:00, 60 seats)
- **T104**: Marseille → Paris (06:00, 40 seats)
- **T105**: Paris → Nice (14:00, 55 seats)

## 🔐 IAM Permissions

### Lambda Execution Role
- Basic Lambda execution permissions (logs)

### Bedrock Agent Role
- `bedrock:InvokeModel` - Invoke foundation models
- `lambda:InvokeFunction` - Call action group Lambda

### Action Group Lambda Role
- Basic Lambda execution permissions

## 💰 Cost Considerations

- **Lambda**: Pay per invocation and execution time
- **API Gateway HTTP API**: Lower cost than REST API
- **Bedrock**: Pay per token (input/output)
- **No database costs**: Using in-memory storage

Suitable for development and low-traffic production workloads.

## 🔄 Update and Redeploy

```bash
# Update code
# ... make changes ...

# Redeploy
cd infrastructure
cdk deploy --all
```

## 🧹 Cleanup

```bash
cd infrastructure
cdk destroy --all
```

## 📝 Notes

- In-memory database resets on Lambda cold starts
- For production, consider using DynamoDB or RDS
- Lambda has 15-minute timeout, API Gateway HTTP API has 29-second timeout
- Docker images can be up to 10GB for Lambda

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Lambda Timeout
- Increase timeout in `api_stack.py`
- Check CloudWatch logs

### Bedrock Agent Not Working
- Ensure agent is "Prepared" in AWS Console
- Check Lambda permissions
- Verify OpenAPI schema syntax

### Docker Build Fails
- Ensure Docker is running
- Check Dockerfile syntax
- Verify all dependencies are listed in requirements.txt

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS CDK Python](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)
- [Mangum Documentation](https://mangum.io/)

