# Train Booking API - Architecture Documentation

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                                │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Gateway (HTTP API v2)              │  │
│  │                  https://api-id.execute-api.region.amazonaws.com │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                      │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Lambda Function (Container)                 │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │          FastAPI Application                      │   │  │
│  │  │                                                    │   │  │
│  │  │  ├─ app/main.py (Mangum adapter)                 │   │  │
│  │  │  ├─ app/routers/trains.py                        │   │  │
│  │  │  ├─ app/routers/bookings.py                      │   │  │
│  │  │  └─ app/database.py (In-Memory)                  │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Amazon Bedrock Agent                         │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────┐             │  │
│  │  │  Claude 3 Sonnet Foundation Model      │             │  │
│  │  │  (Orchestration & Conversation)        │             │  │
│  │  └────────────────┬───────────────────────┘             │  │
│  │                   │                                       │  │
│  │                   ↓                                       │  │
│  │  ┌────────────────────────────────────────┐             │  │
│  │  │       Action Group                      │             │  │
│  │  │  - searchTrains                         │             │  │
│  │  │  - createBooking                        │             │  │
│  │  │  - getBookingStatus                     │             │  │
│  │  │  - cancelBooking                        │             │  │
│  │  └────────────────┬───────────────────────┘             │  │
│  └───────────────────┼───────────────────────────────────┘  │
│                      │                                        │
│                      ↓                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Lambda Function (Action Group Executor)           │  │
│  │                                                            │  │
│  │  ├─ bedrock_agent/lambda_handler.py                      │  │
│  │  ├─ AWS Powertools BedrockAgentResolver                  │  │
│  │  └─ Shares data with main API Lambda                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow

### REST API Flow

```
User Request
    ↓
1. API Gateway receives HTTP request
    ↓
2. API Gateway forwards to Lambda
    ↓
3. Mangum adapter converts API Gateway event to ASGI
    ↓
4. FastAPI routes request to appropriate endpoint
    ↓
5. Endpoint processes request (validate, business logic)
    ↓
6. Database layer (in-memory) handles data operations
    ↓
7. FastAPI returns response
    ↓
8. Mangum converts ASGI response to Lambda response
    ↓
9. API Gateway returns HTTP response to user
```

### Bedrock Agent Flow

```
User Message (Conversational)
    ↓
1. Bedrock Agent receives natural language input
    ↓
2. Claude 3 Sonnet processes and understands intent
    ↓
3. Agent determines which action(s) to invoke
    ↓
4. Agent calls Action Group Lambda function
    ↓
5. Lambda handler routes to appropriate function
    ↓
6. Function processes request with business logic
    ↓
7. Function accesses in-memory database
    ↓
8. Response returned to Bedrock Agent
    ↓
9. Claude 3 Sonnet generates natural language response
    ↓
10. User receives conversational response
```

## 📦 Component Details

### 1. API Gateway (HTTP API v2)

**Purpose**: Entry point for REST API requests

**Features**:
- HTTP API (cheaper than REST API)
- CORS enabled
- Automatic SSL/TLS
- CloudWatch logging
- Throttling and rate limiting

**Endpoints**:
- `GET /trains` - Search trains
- `GET /trains/all` - List all trains
- `GET /trains/{train_number}` - Get train details
- `POST /bookings` - Create booking
- `GET /bookings/{booking_id}` - Get booking
- `DELETE /bookings/{booking_id}` - Cancel booking
- `GET /health` - Health check
- `GET /` - API info

### 2. Lambda Function (FastAPI Container)

**Purpose**: Hosts the REST API application

**Specifications**:
- Runtime: Python 3.12
- Package: Docker container (up to 10GB)
- Memory: 512 MB
- Timeout: 30 seconds
- Architecture: x86_64

**Components**:
- **Mangum**: ASGI-to-Lambda adapter
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **In-Memory DB**: Python dictionaries

**Environment Variables**:
- `LOG_LEVEL`: INFO
- Custom configs as needed

### 3. Amazon Bedrock Agent

**Purpose**: Conversational AI interface

**Specifications**:
- Foundation Model: Claude 3 Sonnet
- Session TTL: 10 minutes
- Auto-prepare: Enabled

**Instructions**:
```
You are a helpful train booking assistant. Help users search for trains, 
make bookings, check booking status, and cancel reservations. Always 
confirm booking details before finalizing.
```

**Capabilities**:
- Natural language understanding
- Multi-turn conversations
- Action orchestration
- Context retention

### 4. Action Group Lambda

**Purpose**: Execute booking operations for Bedrock Agent

**Specifications**:
- Runtime: Python 3.12
- Memory: 256 MB
- Timeout: 30 seconds
- Handler: `lambda_handler.lambda_handler`

**Actions**:
- `searchTrains(origin, destination, date)`
- `createBooking(train_number, passenger_name, email, journey_date)`
- `getBookingStatus(booking_id)`
- `cancelBooking(booking_id)`

**Framework**:
- AWS Lambda Powertools
- BedrockAgentResolver

## 🗄️ Data Model

### Train Schema

```python
{
    "train_number": "T101",           # Unique identifier
    "name": "Express 2025",           # Display name
    "route": {
        "from": "Paris",              # Origin station
        "to": "Lyon"                  # Destination station
    },
    "departure_time": "08:00",        # HH:MM format
    "available_seats": 50             # Integer >= 0
}
```

### Booking Schema

```python
{
    "booking_id": "BK12345678",       # Unique ID (BK + 8 hex chars)
    "train_number": "T101",           # Reference to train
    "passenger_name": "John Doe",     # Passenger name
    "email": "john@example.com",      # Valid email
    "journey_date": "2025-12-27",     # ISO date format
    "seat_number": "A12",             # Assigned seat
    "status": "confirmed"             # confirmed | cancelled
}
```

## 🔐 Security & IAM

### Lambda Execution Role (API Function)

```yaml
Permissions:
  - logs:CreateLogGroup
  - logs:CreateLogStream
  - logs:PutLogEvents
```

### Bedrock Agent Service Role

```yaml
Permissions:
  - bedrock:InvokeModel
  - bedrock:InvokeModelWithResponseStream
  - lambda:InvokeFunction (Action Group Lambda)
```

### Action Group Lambda Role

```yaml
Permissions:
  - logs:CreateLogGroup
  - logs:CreateLogStream
  - logs:PutLogEvents

Resource Policies:
  - Allow bedrock.amazonaws.com to invoke function
```

## 📊 Data Flow Diagrams

### Create Booking Flow

```
User
  │
  ├─ REST API Path ────────────────────────┐
  │                                         │
  │  POST /bookings                         │
  │  {                                      │
  │    "train_number": "T101",             │
  │    "passenger_name": "John",           │
  │    "email": "john@example.com",        │
  │    "journey_date": "2025-12-27"        │
  │  }                                      │
  │                                         │
  ↓                                         ↓
API Gateway ───────────────────→ Lambda (FastAPI)
                                    │
                                    ├─ Validate input (Pydantic)
                                    ├─ Check train exists
                                    ├─ Check seat availability
                                    ├─ Generate booking ID
                                    ├─ Assign seat number
                                    ├─ Create booking record
                                    ├─ Decrease available seats
                                    ↓
                                 Response
                                    │
                                    ├─ 201 Created (success)
                                    └─ 404/400 (error)
```

### Conversational Booking Flow

```
User: "Book me a ticket from Paris to Lyon on Dec 27"
  ↓
Bedrock Agent (Claude 3 Sonnet)
  │
  ├─ Understand intent: booking
  ├─ Extract: origin=Paris, destination=Lyon, date=2025-12-27
  ├─ Determine action: searchTrains first
  │
  ↓
Action Group Lambda: searchTrains(Paris, Lyon, 2025-12-27)
  │
  ├─ Query in-memory database
  ├─ Filter by route and availability
  │
  ↓
Returns: [Train T101, Train T102, ...]
  ↓
Agent: "I found 2 trains. T101 at 08:00 or T102 at 09:30. 
        Which would you prefer? Also, may I have your name 
        and email?"
  ↓
User: "T101 please. John Doe, john@example.com"
  ↓
Agent determines: createBooking needed
  ↓
Action Group Lambda: createBooking(T101, John Doe, 
                     john@example.com, 2025-12-27)
  │
  ├─ Validate train
  ├─ Create booking
  ├─ Assign seat
  │
  ↓
Returns: {booking_id: "BK12345678", seat_number: "A1", ...}
  ↓
Agent: "Great! I've booked you on Train T101 from Paris 
        to Lyon on December 27 at 08:00. Your booking ID 
        is BK12345678 and you're in seat A1."
```

## 🚀 Deployment Architecture

```
Developer Workstation
  │
  ├─ Source Code
  │  ├─ app/
  │  ├─ bedrock_agent/
  │  ├─ infrastructure/
  │  └─ Dockerfile
  │
  ↓
AWS CDK (Infrastructure as Code)
  │
  ├─ Build Docker Image
  │  └─ Push to Amazon ECR
  │
  ├─ Create API Stack
  │  ├─ Lambda Function (from ECR)
  │  └─ API Gateway
  │
  └─ Create Agent Stack
     ├─ Bedrock Agent
     ├─ Action Group
     └─ Action Group Lambda
  
Result:
  ├─ API URL: https://xyz.execute-api.region.amazonaws.com
  ├─ Agent ID: AGENT123
  └─ CloudFormation Stacks deployed
```

## 📈 Scaling & Performance

### Automatic Scaling

- **Lambda**: Scales automatically (0-1000+ concurrent)
- **API Gateway**: Handles any request volume
- **Bedrock**: Managed service, auto-scales

### Performance Characteristics

- **Cold Start**: ~1-3 seconds (Docker container)
- **Warm Response**: ~50-200ms (REST API)
- **Bedrock Response**: ~2-5 seconds (LLM processing)

### Optimization Strategies

1. **Keep Lambda Warm**: Provisioned concurrency
2. **Reduce Container Size**: Multi-stage builds
3. **Database**: Replace in-memory with DynamoDB
4. **Caching**: Add CloudFront or Redis
5. **ARM64**: Switch architecture for cost savings

## 💰 Cost Breakdown

### Monthly Estimates (1000 requests/day)

```
API Gateway HTTP API:
  30,000 requests × $0.0000010 = $0.03

Lambda (API):
  30,000 invocations × $0.0000002 = $0.006
  30,000 × 0.5 seconds × 512MB × $0.0000166667 = $0.125

Lambda (Action Group):
  5,000 invocations × $0.0000002 = $0.001
  5,000 × 0.3 seconds × 256MB × $0.0000166667 = $0.006

Bedrock (Claude 3 Sonnet):
  5,000 conversations
  ~500 input tokens × $0.003/1K = $7.50
  ~200 output tokens × $0.015/1K = $1.50

CloudWatch Logs:
  ~$0.50/month

Total: ~$10/month (mostly Bedrock usage)
```

## 🔍 Monitoring & Observability

### CloudWatch Metrics

- **Lambda**: Invocations, Duration, Errors, Throttles
- **API Gateway**: Request Count, Latency, 4xx/5xx Errors
- **Bedrock**: Model Invocations, Token Usage

### CloudWatch Logs

- `/aws/lambda/train-booking-api`
- `/aws/lambda/train-booking-action-group`
- `/aws/apigateway/train-booking-api`

### Recommended Alarms

1. Lambda Error Rate > 5%
2. API Gateway 5xx Errors > 1%
3. Lambda Duration > 25 seconds
4. API Gateway Latency > 1 second

## 🔄 CI/CD Pipeline (Optional)

```
GitHub Repository
  │
  ├─ Push to main branch
  │
  ↓
GitHub Actions / CodePipeline
  │
  ├─ Run Tests (pytest)
  ├─ Run Linters (flake8, mypy)
  ├─ Build Docker Image
  ├─ Deploy with CDK
  │
  ↓
Production Environment
```

## 📝 Future Enhancements

1. **Database**: DynamoDB for persistence
2. **Authentication**: Cognito or API keys
3. **Payments**: Stripe integration
4. **Notifications**: SES for email confirmations
5. **Analytics**: Track booking patterns
6. **Multi-region**: Global deployment
7. **WebSocket**: Real-time updates
8. **Mobile App**: React Native frontend

---

**Architecture designed for scalability, cost-efficiency, and maintainability**

