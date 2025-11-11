# LangGraph AI Agents Integration Guide

## Overview

This loan processing system uses **LangGraph** to orchestrate multiple AI agents that work together to evaluate loan applications. The system includes:

1. **Credit Scoring Agent** - Analyzes credit history and calculates credit score
2. **Loan Decision Agent** - Makes lending decision based on all available data
3. **Verification Agent** - Verifies applicant information
4. **Risk Monitoring Agent** - Assesses overall risk level

All results are saved to **Neon DB** (serverless Postgres) using async SQLAlchemy.

## Architecture

```
┌─────────────────┐
│  POST Request   │
│  (JSON Data)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  FastAPI Endpoint       │
│  /submit_loan_app       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Save to Database       │
│  (Initial Record)       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  LangGraph Orchestrator │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ Credit  │ │ Loan         │
│ Scoring │→│ Decision     │
└─────────┘ └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ Verification │
            └──────┬───────┘
                   │
                   ▼
            ┌──────────────┐
            │ Risk         │
            │ Monitoring   │
            └──────┬───────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Update Database │
         │ (Final Results) │
         └────────┬────────┘
                  │
                  ▼
         ┌────────────────┐
         │ JSON Response  │
         └────────────────┘
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements-agents.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database Configuration (Neon DB)
DATABASE_URL=postgresql+asyncpg://user:password@your-neon-host/dbname

# OpenAI API Key (optional - for AI models)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (optional - alternative AI provider)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
DEBUG=False
DB_ECHO=False

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Setup Neon DB

1. Sign up at [Neon.tech](https://neon.tech/)
2. Create a new project
3. Copy the connection string
4. Update `DATABASE_URL` in `.env`

Connection string format:

```
postgresql+asyncpg://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
```

### 4. Initialize Database

The database tables will be created automatically on first startup. To manually initialize:

```python
from app.database import init_db
import asyncio

async def setup():
    await init_db()

asyncio.run(setup())
```

### 5. Start the Server

```bash
# PowerShell
cd G:\dbs\LoanAIAgent-DigitalTwin\backend
$env:PYTHONPATH=(Get-Location).Path
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Agent Details

### Credit Scoring Agent

**Purpose**: Analyzes credit history and calculates a credit score (300-850)

**Inputs**:

- Credit history length (months)
- Number of credit accounts
- Credit utilization percentage
- Payment history (on-time, late, defaults, write-offs)
- Recent credit inquiries

**Outputs**:

- `calculated_credit_score` (300-850)
- `credit_tier` (Excellent/Good/Fair/Poor/Very Poor)
- `credit_score_factors` (list of contributing factors)
- `credit_score_rationale` (explanation)

**Algorithm** (simplified - replace with AI model):

- Base score: 500
- Credit history: +0-100 points
- Payment history: +0-200 points
- Credit utilization: +50 to -20 points
- Inquiries: -0 to -50 points
- Defaults/write-offs: Heavy penalties

### Loan Decision Agent

**Purpose**: Makes final lending decision

**Inputs**:

- Calculated credit score
- Loan amount requested
- Monthly income
- Employment status
- Loan tenure

**Outputs**:

- `final_decision` (approved/rejected/under_review)
- `approved_amount`
- `interest_rate`
- `decision_rationale`
- `rejection_reasons` (if rejected)
- `conditions` (if approved)

**Decision Logic**:

- Credit score >= 600 required
- Employment required (for large loans)
- DTI ratio <= 50%
- Interest rate based on credit tier

### Verification Agent

**Purpose**: Verifies applicant information

**Inputs**:

- Email address
- Phone number
- Income verification status
- Employment status

**Outputs**:

- `verification_status` (verified/pending/failed)
- `verified_fields` (list of verified fields)
- `pending_verifications` (list of pending fields)
- `verification_notes`

**Verification Checks**:

- Email format validation
- Phone number format validation
- Income verification status
- Employment verification

### Risk Monitoring Agent

**Purpose**: Assesses overall risk level

**Inputs**:

- Calculated credit score
- Final decision
- Repayment history (defaults, write-offs)
- Credit utilization

**Outputs**:

- `risk_level` (low/medium/high)
- `risk_score` (0-100, where 100 is highest risk)
- `risk_factors` (list of risk indicators)
- `recommended_actions` (mitigation steps)

**Risk Calculation**:

- Credit score < 600: +40 points
- High credit utilization (>80%): +20 points
- Payment defaults: +20 points per default
- Loan write-offs: +30 points per write-off
- Multiple inquiries: +10 points

## Database Schema

### loan_applications Table

Stores complete loan application data and results:

```sql
CREATE TABLE loan_applications (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(50) UNIQUE NOT NULL,
    applicant_id VARCHAR(50) NOT NULL,

    -- Personal details
    full_name VARCHAR(255) NOT NULL,
    date_of_birth TIMESTAMP NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    address TEXT,

    -- Credit profile
    credit_history_length_months INTEGER NOT NULL,
    number_of_credit_accounts INTEGER NOT NULL,
    credit_mix JSONB NOT NULL,
    credit_utilization_percent FLOAT NOT NULL,
    recent_credit_inquiries_6m INTEGER NOT NULL,
    repayment_history JSONB NOT NULL,

    -- Employment and income
    employment_status VARCHAR(50) NOT NULL,
    employment_duration_months INTEGER NOT NULL,
    monthly_income FLOAT NOT NULL,
    income_verified BOOLEAN NOT NULL,

    -- Loan request
    loan_amount_requested FLOAT NOT NULL,
    loan_purpose VARCHAR(100) NOT NULL,
    loan_tenure_months INTEGER NOT NULL,
    loan_to_value_ratio_percent FLOAT,

    -- Agent results (JSON)
    credit_scoring_result JSONB,
    loan_decision_result JSONB,
    verification_result JSONB,
    risk_monitoring_result JSONB,

    -- Aggregated results
    final_decision VARCHAR(50),
    calculated_credit_score INTEGER,
    risk_level VARCHAR(50),
    approved_amount FLOAT,
    interest_rate FLOAT,

    -- Status and metadata
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    processing_time_seconds FLOAT,
    error_message TEXT
);
```

### agent_execution_logs Table

Stores individual agent execution logs:

```sql
CREATE TABLE agent_execution_logs (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(50) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    agent_input JSONB,
    agent_output JSONB,
    execution_time_seconds FLOAT,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Usage

### Submit Loan Application

```bash
POST /submit_loan_application
Content-Type: application/json

{
  "applicant_id": "APP001",
  "full_name": "John Doe",
  "date_of_birth": "1990-01-15",
  "phone_number": "+1-555-0100",
  "email": "john.doe@example.com",
  "credit_history_length_months": 60,
  "number_of_credit_accounts": 5,
  "credit_mix": {
    "secured_loans": 1,
    "unsecured_loans": 4
  },
  "credit_utilization_percent": 35.5,
  "recent_credit_inquiries_6m": 2,
  "repayment_history": {
    "on_time_payments": 48,
    "late_payments": 2,
    "defaults": 0,
    "write_offs": 0
  },
  "employment_status": "Employed",
  "employment_duration_months": 36,
  "monthly_income": 5000.00,
  "income_verified": true,
  "loan_amount_requested": 50000.00,
  "loan_purpose": "home",
  "loan_tenure_months": 60
}
```

### Response

```json
{
  "status": "success",
  "message": "Loan application processed successfully. Decision: approved",
  "application_id": "LA-20251111-ABC123",
  "applicant_id": "APP001",
  "final_decision": "approved",
  "calculated_credit_score": 720,
  "risk_level": "low",
  "approved_amount": 50000.0,
  "interest_rate": 5.5
}
```

## Extending with Real AI Models

### Option 1: OpenAI Integration

```python
from langchain_openai import ChatOpenAI

async def credit_scoring_agent(state: LoanProcessingState) -> LoanProcessingState:
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    prompt = f"""
    Analyze this credit profile and calculate a credit score (300-850):

    Credit History: {state['application_data']['credit_history_length_months']} months
    Credit Accounts: {state['application_data']['number_of_credit_accounts']}
    Credit Utilization: {state['application_data']['credit_utilization_percent']}%
    Payment History: {state['application_data']['repayment_history']}

    Provide:
    1. Credit score (300-850)
    2. Key factors affecting the score
    3. Rationale

    Return as JSON.
    """

    response = await llm.ainvoke(prompt)
    # Parse and process response
    ...
```

### Option 2: Anthropic Integration

```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-opus-20240229", temperature=0)
```

## Testing

### Test with Sample Data

```bash
cd backend
.\test_api.ps1
```

### Check Database

```sql
-- View all applications
SELECT application_id, full_name, status, final_decision, calculated_credit_score
FROM loan_applications
ORDER BY created_at DESC;

-- View agent execution logs
SELECT application_id, agent_name, status, execution_time_seconds
FROM agent_execution_logs
ORDER BY created_at DESC;
```

## Monitoring and Logging

All agent executions are logged with:

- Execution time
- Input/output data
- Success/failure status
- Error messages (if any)

View logs in the console or check the `agent_execution_logs` table.

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure Neon DB connection
3. ✅ Set up environment variables
4. ✅ Test the API
5. 🔄 Replace simplified logic with real AI models
6. 🔄 Add more sophisticated credit scoring
7. 🔄 Implement document verification
8. 🔄 Add email/SMS notifications
9. 🔄 Create admin dashboard
10. 🔄 Add authentication

## Troubleshooting

### Database Connection Issues

```python
# Test database connection
from app.database import engine

async def test_connection():
    async with engine.begin() as conn:
        result = await conn.execute("SELECT 1")
        print("✅ Database connected!")

import asyncio
asyncio.run(test_connection())
```

### LangGraph Issues

- Ensure `langgraph` is installed: `pip install langgraph`
- Check that all agents return the correct state type
- Verify async/await usage is correct

### Agent Timeout

Adjust timeout in `config.py`:

```python
AGENT_TIMEOUT = 60  # Increase for slower models
```

## Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Neon DB Documentation](https://neon.tech/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
