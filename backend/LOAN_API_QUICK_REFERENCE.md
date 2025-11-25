# 🚀 Loan API - Quick Reference Guide

## 📋 Quick Start (1 minute)

### 1. Install Dependencies

```bash
pip install fastapi uvicorn tortoise-orm pydantic pydantic-email-validator
```

### 2. Start Server

```bash
uvicorn app.loan_api_example:app --reload
```

### 3. Test API

```bash
python test_loan_api.py
```

### 4. View Documentation

Open: http://localhost:8000/docs

---

## 🔌 API Endpoints Cheat Sheet

### POST /loan-applications

**Submit new loan application**

```bash
curl -X POST http://localhost:8000/loan-applications \
  -H "Content-Type: application/json" \
  -d '{
    "applicant_id": "APP001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+1-555-0100",
    "loan_amount_requested": 50000,
    "loan_purpose": "home_improvement",
    "loan_tenure_months": 60,
    "monthly_income": 6500,
    "employment_status": "employed",
    "employment_duration_months": 36,
    "credit_score": 720
  }'
```

**Returns:** `application_id` (UUID), decision, approved_amount, agent_responses, analytics

---

### GET /loan-applications/{id}

**Fetch application details**

```bash
curl http://localhost:8000/loan-applications/{uuid}
```

**Returns:** Complete application with agent_responses and analytics_snapshot

---

### GET /health

**Check API health**

```bash
curl http://localhost:8000/health
```

---

## 📦 Database Models

### LoanApplication

- **Primary Key:** UUID (auto-generated)
- **Status:** submitted → processing → completed
- **Decisions:** approved, rejected, pending_review

### AgentResponse

- **Relationship:** Many-to-One with LoanApplication
- **Types:** credit_scoring, risk_assessment, verification, decision_engine
- **Contains:** response_data (JSON), confidence_score, execution_time_ms

### AnalyticsSnapshot

- **Relationship:** One-to-One with LoanApplication
- **Contains:** calculated_credit_score, risk_score, approval_probability, DTI ratio, risk_factors

---

## 💻 Frontend Integration

### TypeScript Example

```typescript
// Submit application
const response = await fetch("http://localhost:8000/loan-applications", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    applicant_id: "APP001",
    full_name: "Jane Smith",
    email: "jane@example.com",
    phone_number: "+1-555-0123",
    loan_amount_requested: 50000,
    loan_purpose: "home_improvement",
    loan_tenure_months: 60,
    monthly_income: 6500,
    employment_status: "employed",
    employment_duration_months: 36,
    credit_score: 720,
  }),
});

const result = await response.json();
console.log("Application ID:", result.application_id);
console.log("Decision:", result.loan_application.final_decision);

// Fetch details
const details = await fetch(
  `http://localhost:8000/loan-applications/${result.application_id}`
);
const data = await details.json();
```

### Axios Example

```typescript
import axios from "axios";

const { data } = await axios.post(
  "http://localhost:8000/loan-applications",
  applicationData
);

console.log("Application ID:", data.application_id);
```

---

## 🏗️ Key Features

✅ **UUID Primary Keys** - All models use UUID for distributed systems
✅ **Async Processing** - Non-blocking AI agent execution
✅ **Relationships** - Proper Foreign Keys and One-to-One relations
✅ **Prefetch Optimization** - Related data loaded efficiently
✅ **JSON Storage** - Flexible data in response_data and model_scores
✅ **Timestamps** - Auto-managed created_at and updated_at
✅ **Enums** - Type-safe status and agent types
✅ **Validation** - Pydantic models ensure data integrity

---

## 🎯 Response Structure

### POST Response

```json
{
  "status": "success",
  "application_id": "uuid",
  "current_status": "completed",
  "loan_application": {
    "id": "uuid",
    "full_name": "...",
    "final_decision": "approved|rejected|pending_review",
    "approved_amount": 50000.0,
    "interest_rate": 8.5
  },
  "agent_responses": [
    {
      "agent_name": "Credit Scoring Agent",
      "response_data": { ... },
      "confidence_score": 0.92
    }
  ],
  "analytics_snapshot": {
    "calculated_credit_score": 745,
    "risk_score": 28.5,
    "approval_probability": 0.85,
    "debt_to_income_ratio": 0.1282,
    "risk_factors": []
  }
}
```

### GET Response

```json
{
  "status": "success",
  "loan_application": { ... },
  "agent_responses": [ ... ],
  "analytics_snapshot": { ... }
}
```

---

## 🔧 Configuration

### Change Database

```python
# SQLite (default - development)
db_url="sqlite://./loan_application.db"

# PostgreSQL (production)
db_url="postgres://user:pass@host:5432/database"

# Neon (serverless)
db_url="postgres://user:pass@ep-xxx.neon.tech/db?sslmode=require"

# MySQL
db_url="mysql://user:pass@host:3306/database"
```

### Update CORS Origins

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🧪 Testing Commands

### Run Test Suite

```bash
python test_loan_api.py
```

### Manual cURL Tests

**Submit:**

```bash
curl -X POST http://localhost:8000/loan-applications \
  -H "Content-Type: application/json" \
  -d @test_application.json
```

**Fetch:**

```bash
curl http://localhost:8000/loan-applications/{uuid}
```

**Health:**

```bash
curl http://localhost:8000/health
```

### Python Test

```python
import requests

# Submit
response = requests.post(
    "http://localhost:8000/loan-applications",
    json={...}
)
app_id = response.json()["application_id"]

# Fetch
details = requests.get(
    f"http://localhost:8000/loan-applications/{app_id}"
)
```

---

## 🚨 Error Codes

| Code | Meaning        | Cause                              |
| ---- | -------------- | ---------------------------------- |
| 201  | Created        | Application submitted successfully |
| 200  | OK             | Application retrieved successfully |
| 400  | Bad Request    | Invalid UUID or validation error   |
| 404  | Not Found      | Application doesn't exist          |
| 500  | Internal Error | Server/database error              |

---

## 📊 AI Agents Explained

### 1. Credit Scoring Agent

- Calculates credit score based on income, employment
- Returns: score, tier, breakdown

### 2. Risk Assessment Agent

- Evaluates financial risk
- Returns: risk_score, DTI ratio, risk_factors

### 3. Verification Agent

- Simulates identity/document verification
- Returns: verification status, documents required

### 4. Decision Engine Agent

- Makes final loan decision
- Returns: approved/rejected/pending, amount, interest_rate

---

## 🎨 Decision Logic

```
Credit Score >= 700 + Risk < 40 + DTI < 0.4
  → APPROVED (100% amount, 8.5% rate)

Credit Score >= 650 + Risk < 60 + DTI < 0.5
  → APPROVED (80% amount, 11.5% rate)

Credit Score >= 600
  → PENDING REVIEW (60% amount, 14.5% rate)

Otherwise
  → REJECTED (0% amount)
```

---

## 📂 File Structure

```
backend/
├── app/
│   └── loan_api_example.py       # Main API file
├── test_loan_api.py               # Test suite
├── start_loan_api.bat             # Windows starter
├── LOAN_API_README.md             # Full documentation
└── LOAN_API_QUICK_REFERENCE.md    # This file

frontend/
└── src/
    └── services/
        └── loanApplicationApi.ts  # TypeScript integration
```

---

## 🔗 Important URLs

- **API Base:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 💡 Pro Tips

1. **Use UUIDs** - All IDs are UUIDs, not integers
2. **Check Status** - Use `/health` to verify database connection
3. **Prefetch Relations** - GET endpoint automatically loads all related data
4. **JSON Fields** - response_data and model_scores store flexible JSON
5. **Async Everywhere** - All database operations are async
6. **Type Safety** - Enums ensure valid status and agent types
7. **Timestamps** - created_at and updated_at auto-managed

---

## 🛠️ Troubleshooting

### Server won't start

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
uvicorn app.loan_api_example:app --port 8001
```

### Database errors

```bash
# Delete and recreate database
rm loan_application.db
# Restart server (schemas auto-generated)
```

### Import errors

```bash
# Reinstall dependencies
pip install --upgrade fastapi uvicorn tortoise-orm pydantic
```

### CORS errors

```python
# Add your frontend URL to allow_origins
allow_origins=["http://localhost:3000"]
```

---

## 📈 Performance Tips

- Use PostgreSQL for production (better concurrency)
- Enable database connection pooling
- Use Redis for caching frequently accessed applications
- Implement pagination for list endpoints
- Add database indexes on frequently queried fields

---

## 🔐 Security Recommendations

- [ ] Add JWT authentication
- [ ] Implement rate limiting
- [ ] Use HTTPS in production
- [ ] Validate input data
- [ ] Sanitize JSON fields
- [ ] Add API versioning
- [ ] Log all access attempts
- [ ] Use environment variables for secrets

---

## 📚 Next Steps

1. ✅ Test API with provided test script
2. ✅ Integrate frontend using TypeScript code
3. ⬜ Switch to PostgreSQL for production
4. ⬜ Add authentication
5. ⬜ Implement real AI agents
6. ⬜ Add pagination and search
7. ⬜ Deploy to cloud (AWS, Azure, GCP)
8. ⬜ Set up monitoring and logging

---

**Need Help?** Check LOAN_API_README.md for detailed documentation
