# 🏦 Loan Application API with Tortoise ORM

Complete FastAPI loan application system with AI agent processing simulation.

## 📋 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [Frontend Integration](#frontend-integration)
- [Testing](#testing)
- [Production Deployment](#production-deployment)

---

## ✨ Features

### Core Functionality
- ✅ **UUID Primary Keys** - All models use UUID for secure, distributed identifiers
- ✅ **Tortoise ORM** - Async ORM with relationships and migrations
- ✅ **AI Agent Simulation** - 4 processing agents (Credit Scoring, Risk Assessment, Verification, Decision Engine)
- ✅ **Real-time Processing** - Complete application processing in single request
- ✅ **Relationship Management** - One-to-Many and One-to-One relationships properly configured
- ✅ **Comprehensive Analytics** - Detailed metrics and scoring breakdowns

### API Features
- POST `/loan-applications` - Submit new application with immediate AI processing
- GET `/loan-applications/{uuid}` - Fetch complete application with all relationships
- GET `/health` - Database health check
- Automatic OpenAPI documentation at `/docs` and `/redoc`

---

## 🛠 Tech Stack

### Backend
- **FastAPI** 0.115.0 - Modern async web framework
- **Tortoise ORM** 0.25.1 - Async ORM with relationship support
- **Pydantic** 2.x - Data validation and serialization
- **asyncio** - Async/await support for concurrent processing

### Database (Flexible)
- **SQLite** - Default for development (included)
- **PostgreSQL** - Recommended for production (Neon, AWS RDS, etc.)
- **MySQL** - Also supported

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.11+
pip or uv
```

### Installation

#### Option 1: Using pip
```bash
# Clone repository
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn tortoise-orm pydantic pydantic-email-validator

# Or install from requirements
pip install -r requirements.txt
```

#### Option 2: Using uv (faster)
```bash
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install fastapi uvicorn tortoise-orm pydantic pydantic-email-validator
```

### Run Server

```bash
# Development mode with auto-reload
uvicorn app.loan_api_example:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.loan_api_example:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access API
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📡 API Endpoints

### POST /loan-applications

**Submit New Loan Application**

Creates a new loan application and triggers AI agent processing.

#### Request Body
```json
{
  "applicant_id": "APP12345",
  "full_name": "Jane Smith",
  "email": "jane.smith@example.com",
  "phone_number": "+1-555-0123",
  "date_of_birth": "1990-05-15",
  "address": "123 Main St, New York, NY 10001",
  "loan_amount_requested": 50000.00,
  "loan_purpose": "home_improvement",
  "loan_tenure_months": 60,
  "monthly_income": 6500.00,
  "employment_status": "employed",
  "employment_duration_months": 36,
  "credit_score": 720
}
```

#### Response (201 Created)
```json
{
  "status": "success",
  "message": "Loan application processed successfully. Decision: approved",
  "application_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "current_status": "completed",
  "loan_application": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "applicant_id": "APP12345",
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone_number": "+1-555-0123",
    "loan_amount_requested": 50000.0,
    "loan_purpose": "home_improvement",
    "loan_tenure_months": 60,
    "monthly_income": 6500.0,
    "employment_status": "employed",
    "status": "completed",
    "final_decision": "approved",
    "approved_amount": 50000.0,
    "interest_rate": 8.5,
    "created_at": "2025-11-25T10:30:00Z",
    "processed_at": "2025-11-25T10:30:02Z"
  },
  "agent_responses": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "agent_type": "credit_scoring",
      "agent_name": "Credit Scoring Agent",
      "response_data": {
        "calculated_credit_score": 745,
        "credit_tier": "Very Good",
        "score_breakdown": {
          "base_score": 720,
          "income_adjustment": 6.5,
          "employment_adjustment": 18.0
        },
        "factors_affecting_score": [
          "Payment history",
          "Credit utilization",
          "Length of credit history"
        ]
      },
      "confidence_score": 0.92,
      "execution_time_ms": 105,
      "status": "success",
      "created_at": "2025-11-25T10:30:01Z"
    },
    {
      "id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
      "agent_type": "risk_assessment",
      "agent_name": "Risk Assessment Agent",
      "response_data": {
        "risk_score": 28.5,
        "risk_level": "low",
        "debt_to_income_ratio": 0.1282,
        "loan_to_income_ratio": 0.6410,
        "risk_factors": [],
        "mitigation_suggestions": []
      },
      "confidence_score": 0.88,
      "execution_time_ms": 152,
      "status": "success",
      "created_at": "2025-11-25T10:30:01Z"
    }
  ],
  "analytics_snapshot": {
    "id": "c3d4e5f6-g7h8-9012-cdef-123456789012",
    "calculated_credit_score": 745,
    "risk_score": 28.5,
    "approval_probability": 0.85,
    "recommended_amount": 50000.0,
    "recommended_interest_rate": 8.5,
    "debt_to_income_ratio": 0.1282,
    "risk_factors": [],
    "positive_factors": ["Stable employment", "Good credit history"],
    "model_scores": {
      "credit_score": 745,
      "risk_score": 28.5,
      "verification_score": 0.92
    },
    "processing_time_seconds": 1.847,
    "total_agents_executed": 4,
    "created_at": "2025-11-25T10:30:02Z"
  },
  "processing_time_seconds": 1.847
}
```

#### Error Responses
- **400 Bad Request** - Invalid input data
- **500 Internal Server Error** - Processing failure

---

### GET /loan-applications/{application_id}

**Fetch Loan Application Details**

Retrieves complete loan application with all related agent responses and analytics.

#### Path Parameters
- `application_id` (string, UUID) - The unique identifier of the loan application

#### Example Request
```bash
GET http://localhost:8000/loan-applications/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

#### Response (200 OK)
```json
{
  "status": "success",
  "loan_application": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "applicant_id": "APP12345",
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone_number": "+1-555-0123",
    "loan_amount_requested": 50000.0,
    "loan_purpose": "home_improvement",
    "loan_tenure_months": 60,
    "monthly_income": 6500.0,
    "employment_status": "employed",
    "status": "completed",
    "final_decision": "approved",
    "approved_amount": 50000.0,
    "interest_rate": 8.5,
    "created_at": "2025-11-25T10:30:00Z",
    "processed_at": "2025-11-25T10:30:02Z"
  },
  "agent_responses": [...],
  "analytics_snapshot": {...}
}
```

#### Error Responses
- **400 Bad Request** - Invalid UUID format
- **404 Not Found** - Application not found
- **500 Internal Server Error** - Database error

---

## 🗄 Database Models

### LoanApplication
**Primary table for loan applications**

```python
class LoanApplication(Model):
    # Primary Key - UUID
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Applicant Information
    applicant_id = fields.CharField(max_length=100, index=True)
    full_name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, index=True)
    phone_number = fields.CharField(max_length=50)
    date_of_birth = fields.DateField(null=True)
    address = fields.TextField(null=True)
    
    # Loan Details
    loan_amount_requested = fields.DecimalField(max_digits=15, decimal_places=2)
    loan_purpose = fields.CharField(max_length=100)
    loan_tenure_months = fields.IntField()
    
    # Credit Information
    credit_score = fields.IntField(null=True)
    monthly_income = fields.DecimalField(max_digits=15, decimal_places=2)
    employment_status = fields.CharField(max_length=50)
    employment_duration_months = fields.IntField()
    
    # Application Status
    status = fields.CharEnumField(ApplicationStatus, default=ApplicationStatus.SUBMITTED)
    
    # Processing Results
    final_decision = fields.CharField(max_length=50, null=True)
    approved_amount = fields.DecimalField(max_digits=15, decimal_places=2, null=True)
    interest_rate = fields.FloatField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    processed_at = fields.DatetimeField(null=True)
```

### AgentResponse
**Stores AI agent execution results (One-to-Many with LoanApplication)**

```python
class AgentResponse(Model):
    # Primary Key - UUID
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Foreign Key to LoanApplication (CASCADE delete)
    loan_application = fields.ForeignKeyField(
        "models.LoanApplication",
        related_name="agent_responses",
        on_delete=fields.CASCADE
    )
    
    # Agent Information
    agent_type = fields.CharEnumField(AgentType)
    agent_name = fields.CharField(max_length=100)
    agent_version = fields.CharField(max_length=50, default="1.0")
    
    # Agent Output
    response_data = fields.JSONField()
    confidence_score = fields.FloatField(null=True)
    execution_time_ms = fields.IntField(null=True)
    
    # Status
    status = fields.CharField(max_length=50, default="success")
    error_message = fields.TextField(null=True)
    
    # Timestamp
    created_at = fields.DatetimeField(auto_now_add=True)
```

### AnalyticsSnapshot
**Stores calculated analytics (One-to-One with LoanApplication)**

```python
class AnalyticsSnapshot(Model):
    # Primary Key - UUID
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Foreign Key to LoanApplication (CASCADE delete)
    loan_application = fields.OneToOneField(
        "models.LoanApplication",
        related_name="analytics_snapshot",
        on_delete=fields.CASCADE
    )
    
    # Calculated Metrics
    calculated_credit_score = fields.IntField(null=True)
    risk_score = fields.FloatField(null=True)
    approval_probability = fields.FloatField(null=True)
    recommended_amount = fields.DecimalField(max_digits=15, decimal_places=2, null=True)
    recommended_interest_rate = fields.FloatField(null=True)
    
    # Debt Ratios
    debt_to_income_ratio = fields.FloatField(null=True)
    loan_to_income_ratio = fields.FloatField(null=True)
    
    # Risk Analysis
    risk_factors = fields.JSONField(null=True)
    positive_factors = fields.JSONField(null=True)
    model_scores = fields.JSONField(null=True)
    
    # Metadata
    processing_time_seconds = fields.FloatField(null=True)
    total_agents_executed = fields.IntField(default=0)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

### Relationship Diagram
```
LoanApplication (1) ──────< (Many) AgentResponse
       │
       │
       └──────── (1:1) ─────── AnalyticsSnapshot
```

---

## 🌐 Frontend Integration

Complete TypeScript integration code is available in:
```
frontend/src/services/loanApplicationApi.ts
```

### Quick Usage

#### 1. Submit Application (Fetch API)
```typescript
import { submitLoanApplication } from './services/loanApplicationApi';

const response = await submitLoanApplication({
  applicant_id: "APP12345",
  full_name: "Jane Smith",
  email: "jane.smith@example.com",
  phone_number: "+1-555-0123",
  loan_amount_requested: 50000,
  loan_purpose: "home_improvement",
  loan_tenure_months: 60,
  monthly_income: 6500,
  employment_status: "employed",
  employment_duration_months: 36,
  credit_score: 720
});

console.log("Application ID:", response.application_id);
console.log("Decision:", response.loan_application.final_decision);
```

#### 2. Fetch Application Details
```typescript
import { fetchLoanApplication } from './services/loanApplicationApi';

const details = await fetchLoanApplication(applicationId);

console.log("Status:", details.loan_application.status);
console.log("Approved Amount:", details.loan_application.approved_amount);
console.log("Risk Score:", details.analytics_snapshot?.risk_score);
```

#### 3. Using Axios
```typescript
import { submitLoanApplicationAxios } from './services/loanApplicationApi';

const response = await submitLoanApplicationAxios(applicationData);
```

### React Component Example
See `frontend/src/services/loanApplicationApi.ts` for complete React component with form handling.

---

## 🧪 Testing

### Manual Testing with cURL

#### Submit Application
```bash
curl -X POST "http://localhost:8000/loan-applications" \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "TEST001",
    "full_name": "Test User",
    "email": "test@example.com",
    "phone_number": "+1-555-0100",
    "loan_amount_requested": 25000,
    "loan_purpose": "personal",
    "loan_tenure_months": 36,
    "monthly_income": 5000,
    "employment_status": "employed",
    "employment_duration_months": 24,
    "credit_score": 700
  }'
```

#### Fetch Application
```bash
curl -X GET "http://localhost:8000/loan-applications/{application_id}"
```

### Python Testing Script

```python
import requests
import json

API_BASE_URL = "http://localhost:8000"

# Submit application
response = requests.post(
    f"{API_BASE_URL}/loan-applications",
    json={
        "applicant_id": "TEST002",
        "full_name": "Python Test",
        "email": "python@example.com",
        "phone_number": "+1-555-0200",
        "loan_amount_requested": 30000,
        "loan_purpose": "business",
        "loan_tenure_months": 48,
        "monthly_income": 7000,
        "employment_status": "self_employed",
        "employment_duration_months": 60,
        "credit_score": 680
    }
)

result = response.json()
application_id = result["application_id"]

print(f"Application ID: {application_id}")
print(f"Decision: {result['loan_application']['final_decision']}")

# Fetch details
details = requests.get(f"{API_BASE_URL}/loan-applications/{application_id}")
print(json.dumps(details.json(), indent=2))
```

---

## 🚀 Production Deployment

### Database Configuration

#### PostgreSQL (Recommended)
```python
# In loan_api_example.py, change:
register_tortoise(
    app,
    db_url="postgres://user:password@host:5432/database",
    modules={"models": ["__main__"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
```

#### Neon (Serverless PostgreSQL)
```python
db_url="postgres://user:password@ep-example.neon.tech/neondb?sslmode=require"
```

#### MySQL
```python
db_url="mysql://user:password@host:3306/database"
```

### Environment Variables
```bash
# .env file
DATABASE_URL=postgres://user:password@host:5432/database
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
API_SECRET_KEY=your-secret-key
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.loan_api_example:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t loan-api .
docker run -p 8000:8000 -e DATABASE_URL=postgres://... loan-api
```

### Production Checklist
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Set proper CORS origins
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Add authentication (JWT tokens)
- [ ] Implement rate limiting
- [ ] Set up logging and monitoring
- [ ] Configure database connection pooling
- [ ] Add API versioning
- [ ] Implement backup strategy
- [ ] Set up CI/CD pipeline

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Tortoise ORM Documentation**: https://tortoise.github.io/
- **Pydantic Documentation**: https://docs.pydantic.dev/

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Pull requests welcome! Please ensure all tests pass before submitting.

---

## 📧 Support

For issues or questions, please open an issue on GitHub.
