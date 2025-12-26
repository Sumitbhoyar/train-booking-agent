# Train Booking API - Project Summary

## 📋 Project Overview

This is a complete serverless train booking system built with AWS services, featuring:
- REST API built with FastAPI
- AWS Bedrock Agent for conversational booking
- Fully automated deployment with AWS CDK
- In-memory database (easily replaceable with DynamoDB)

## 📦 What's Included

### Core Application Files

#### `app/` - FastAPI Application
- `main.py` - FastAPI app with Mangum adapter for Lambda
- `models.py` - Pydantic models for data validation
- `database.py` - In-memory data store with sample trains
- `config.py` - Configuration management
- `routers/trains.py` - Train search endpoints
- `routers/bookings.py` - Booking CRUD endpoints

#### `bedrock_agent/` - Bedrock Agent Integration
- `lambda_handler.py` - Action group Lambda using AWS Powertools
- `openapi_schema.json` - OpenAPI schema for agent actions

#### `infrastructure/` - AWS CDK Infrastructure
- `app.py` - CDK app entry point
- `stacks/api_stack.py` - Lambda + API Gateway stack
- `stacks/agent_stack.py` - Bedrock Agent stack
- `requirements.txt` - CDK dependencies

### Configuration & Deployment

- `Dockerfile` - Container image for Lambda
- `cdk.json` - CDK configuration
- `requirements.txt` - Python dependencies
- `requirements-dev.txt` - Development dependencies
- `deploy.sh` - Linux/Mac deployment script
- `deploy.ps1` - Windows deployment script
- `Makefile` - Common development commands

### Testing

- `tests/test_api.py` - Comprehensive unit tests with pytest
- `pyproject.toml` - Testing and code quality configuration

### Documentation

- `README.md` - Complete documentation
- `QUICKSTART.md` - Quick start guide
- `LICENSE` - MIT License
- `spec.txt` - Original specification

### Additional Files

- `.gitignore` - Git ignore rules
- `task-definition.json` - ECS task definition (if needed)

## 🎯 Key Features

### REST API Endpoints

1. **Train Search**
   - `GET /trains` - Search by route and date
   - `GET /trains/all` - Get all trains
   - `GET /trains/{train_number}` - Get specific train

2. **Booking Management**
   - `POST /bookings` - Create booking
   - `GET /bookings/{booking_id}` - Get booking status
   - `DELETE /bookings/{booking_id}` - Cancel booking

3. **Health & Info**
   - `GET /health` - Health check
   - `GET /` - API information

### Bedrock Agent Actions

1. `searchTrains` - Find available trains
2. `createBooking` - Book a ticket
3. `getBookingStatus` - Check booking
4. `cancelBooking` - Cancel reservation

### Sample Data

5 pre-configured trains:
- T101: Paris → Lyon (08:00, 50 seats)
- T102: Paris → Marseille (09:30, 45 seats)
- T103: Lyon → Paris (22:00, 60 seats)
- T104: Marseille → Paris (06:00, 40 seats)
- T105: Paris → Nice (14:00, 55 seats)

## 🚀 Deployment

### Quick Deploy

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```powershell
.\deploy.ps1
```

### Manual Deploy

```bash
# Install dependencies
pip install -r requirements.txt
cd infrastructure
pip install -r requirements.txt

# Bootstrap CDK (first time)
cdk bootstrap

# Deploy
cdk deploy --all
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Test REST API
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
```

### Test Bedrock Agent

AWS Console → Bedrock → Agents → train-booking-agent → Test

Try:
- "Show me trains from Paris to Lyon"
- "Book a ticket for John Doe on train T101"
- "What's the status of booking BK12345?"
- "Cancel booking BK12345"

## 📊 Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
   REST API      Bedrock Agent
       │              │
       ↓              ↓
┌──────────────┐  ┌────────────────┐
│ API Gateway  │  │  Claude 3      │
│  (HTTP API)  │  │  Sonnet        │
└──────┬───────┘  └────────┬───────┘
       │                   │
       ↓                   ↓
┌──────────────┐  ┌────────────────┐
│   Lambda     │  │   Lambda       │
│  (FastAPI)   │  │  (Actions)     │
└──────┬───────┘  └────────┬───────┘
       │                   │
       └───────┬───────────┘
               ↓
       ┌───────────────┐
       │   In-Memory   │
       │   Database    │
       └───────────────┘
```

## 💡 Development Commands

```bash
# Local development
make run                 # Run API locally
make test                # Run tests
make lint                # Run linters
make format              # Format code

# Docker
make docker-build        # Build image
make docker-run          # Run container

# AWS
make deploy              # Deploy to AWS
make destroy             # Destroy resources
make logs                # View API logs
make logs-agent          # View agent logs

# Cleanup
make clean               # Clean artifacts
```

## 🔧 Customization

### Add More Trains

Edit `app/database.py`:

```python
self.trains.append({
    "train_number": "T106",
    "name": "Your Train",
    "route": {"from": "City A", "to": "City B"},
    "departure_time": "10:00",
    "available_seats": 100
})
```

### Change Bedrock Model

Edit `infrastructure/stacks/agent_stack.py`:

```python
foundation_model="anthropic.claude-3-5-sonnet-20240620-v1:0"
```

### Add Database (DynamoDB)

1. Add DynamoDB table in `api_stack.py`
2. Update `database.py` to use boto3
3. Grant Lambda permissions

## 📈 Cost Optimization

- Using HTTP API instead of REST API (cheaper)
- In-memory database (no DB costs)
- ARM64 architecture option available
- On-demand pricing for Lambda

Estimated cost: **$1-6/month** for light usage

## ✅ Production Readiness

To make production-ready:

1. **Database**: Replace in-memory with DynamoDB
2. **Authentication**: Add Cognito or API keys
3. **Monitoring**: Set up CloudWatch alarms
4. **Logging**: Enhanced structured logging
5. **Rate Limiting**: Add API throttling
6. **Validation**: Enhanced input validation
7. **Security**: VPC, secrets management
8. **CI/CD**: GitHub Actions or CodePipeline

## 📝 Files Created

Total: 30+ files organized in a clean structure

### Python Files: 15
- Application code (7 files)
- Infrastructure code (4 files)
- Tests (2 files)
- Config files (2 files)

### Configuration: 8
- Docker, CDK, dependencies, tooling

### Documentation: 5
- README, QUICKSTART, LICENSE, specs

### Scripts: 2
- Deployment automation

## 🎓 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html)
- [Mangum](https://mangum.io/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit PR

## 📄 License

MIT License - see LICENSE file

## ✨ Features Highlights

- ✅ Complete REST API with FastAPI
- ✅ AWS Bedrock Agent integration
- ✅ Full AWS CDK infrastructure
- ✅ Docker containerization
- ✅ Unit tests included
- ✅ Comprehensive documentation
- ✅ One-command deployment
- ✅ Sample data included
- ✅ Cost-optimized architecture
- ✅ Production-ready structure

---

**Built with ❤️ using AWS, Python, and AI**

