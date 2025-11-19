# Tortoise ORM Setup for Loan Processing Backend

Complete database layer implementation using Tortoise ORM with Neon PostgreSQL for async-first loan application processing.

## 📁 Files Overview

### Core Files

1. **`app/db_models.py`** - Tortoise ORM Models

   - `LoanApplication` - Main application model with all applicant data
   - `AgentResult` - Stores AI agent execution results
   - `ApplicationAnalytics` - Analytics and metrics for applications
   - `AuditLog` - Change tracking and audit trail
   - Enums: `ApplicationStatus`, `AgentStatus`, `RiskLevel`

2. **`app/tortoise_config.py`** - Database Configuration

   - `DatabaseConfig` - Configuration manager
   - `init_database()` - Initialize Tortoise and create schemas
   - `close_database()` - Cleanup connections
   - `lifespan_handler()` - FastAPI lifespan context manager
   - `health_check()` - Database health monitoring
   - `get_database_stats()` - Statistics and metrics

3. **`app/tortoise_crud.py`** - CRUD Operations

   - LoanApplication CRUD: create, get, update, delete
   - AgentResult CRUD: save, query, get latest
   - ApplicationAnalytics CRUD: save, get, update
   - `save_complete_loan_result()` - Save all data in transaction
   - `query_applications_with_filters()` - Advanced querying

4. **`app/main_tortoise_example.py`** - FastAPI Integration Example
   - Complete example showing how to integrate Tortoise with existing endpoints
   - Full workflow: create application → run AI agents → save results → return response

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install tortoise-orm==0.21.0 asyncpg==0.30.0 aerich==0.7.2
```

### 2. Set Environment Variable

Create `.env` file with your Neon PostgreSQL connection string:

```env
DATABASE_URL=postgresql://user:password@ep-example.neon.tech/loandb?sslmode=require
```

### 3. Initialize Database

```python
from app.tortoise_config import init_database

# Initialize and create tables
await init_database(generate_schemas=True, safe=True)
```

### 4. Use in FastAPI

```python
from fastapi import FastAPI
from app.tortoise_config import lifespan_handler

app = FastAPI(lifespan=lifespan_handler)

# Database automatically initializes on startup
# and closes on shutdown
```

## 📊 Database Schema

### LoanApplication Table

```sql
CREATE TABLE loan_applications (
    id UUID PRIMARY KEY,
    applicant_id VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    address TEXT,
    application_status VARCHAR(20) NOT NULL,  -- 'in_progress', 'approved', 'rejected', 'conditional'
    requested_amount DECIMAL(15,2) NOT NULL,
    approved_amount DECIMAL(15,2),
    loan_purpose VARCHAR(255),
    interest_rate DECIMAL(5,2),
    annual_income DECIMAL(15,2) NOT NULL,
    credit_score INT,
    employment_status VARCHAR(100),
    employment_duration_months INT,
    existing_debts DECIMAL(15,2),
    monthly_debt_payments DECIMAL(15,2),
    total_payments INT,
    late_payments INT,
    utilization DECIMAL(5,2),
    credit_inquiries INT,
    credit_mix JSONB,
    repayment_history JSONB,
    final_decision VARCHAR(50),
    risk_level VARCHAR(20),
    rejection_reasons JSONB,
    conditions JSONB,
    submitted_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    processed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_applicant_id ON loan_applications(applicant_id);
CREATE INDEX idx_status ON loan_applications(application_status);
CREATE INDEX idx_submitted_at ON loan_applications(submitted_at);
```

### AgentResult Table

```sql
CREATE TABLE agent_results (
    id UUID PRIMARY KEY,
    loan_application_id UUID NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'success', 'failed', 'pending'
    output JSONB NOT NULL,
    agent_input JSONB,
    error_message TEXT,
    execution_time DECIMAL(10,3),
    timestamp TIMESTAMP NOT NULL,
    agent_version VARCHAR(50)
);

-- Indexes
CREATE INDEX idx_loan_app_id ON agent_results(loan_application_id);
CREATE INDEX idx_agent_name ON agent_results(agent_name);
CREATE INDEX idx_timestamp ON agent_results(timestamp);
```

### ApplicationAnalytics Table

```sql
CREATE TABLE application_analytics (
    id UUID PRIMARY KEY,
    loan_application_id UUID UNIQUE NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
    credit_score INT NOT NULL,
    credit_tier VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high', 'very_high'
    risk_score DECIMAL(5,2) NOT NULL,
    approval_probability DECIMAL(5,4) NOT NULL,
    recommended_amount DECIMAL(15,2) NOT NULL,
    recommended_interest_rate DECIMAL(5,2) NOT NULL,
    dti_ratio DECIMAL(5,2),
    front_end_dti DECIMAL(5,2),
    back_end_dti DECIMAL(5,2),
    credit_score_breakdown JSONB,
    risk_factors JSONB,
    decision_factors JSONB,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

-- Index
CREATE INDEX idx_analytics_loan_app ON application_analytics(loan_application_id);
```

### AuditLog Table

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    loan_application_id UUID REFERENCES loan_applications(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    old_value JSONB,
    new_value JSONB,
    performed_by VARCHAR(255),
    ip_address VARCHAR(45),
    timestamp TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_audit_loan_app ON audit_logs(loan_application_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_action ON audit_logs(action);
```

## 💡 Usage Examples

### Example 1: Create Loan Application

```python
from app.tortoise_crud import create_loan_application

application = await create_loan_application(
    applicant_id="APP123456",
    full_name="John Doe",
    email="john@example.com",
    phone_number="+1234567890",
    address="123 Main St",
    requested_amount=50000.0,
    loan_purpose="home_improvement",
    annual_income=80000.0,
    credit_score=720,
    employment_status="employed",
    employment_duration_months=36,
    existing_debts=15000.0,
    monthly_debt_payments=500.0,
    total_payments=100,
    late_payments=2,
    utilization=30.0,
    credit_inquiries=1,
    credit_mix=["credit_card", "auto_loan"],
    repayment_history=[
        {"month": "2024-01", "status": "on_time"},
        {"month": "2024-02", "status": "on_time"}
    ]
)

print(f"Created application ID: {application.id}")
```

### Example 2: Save Agent Results

```python
from app.tortoise_crud import save_agent_result
from app.db_models import AgentStatus

# Save credit scoring agent result
await save_agent_result(
    loan_application_id=application.id,
    agent_name="credit_scoring",
    status=AgentStatus.SUCCESS,
    output={
        "credit_score": 720,
        "credit_tier": "Good",
        "breakdown": {
            "payment_history": 280,
            "credit_age": 95,
            "utilization": 85
        }
    },
    agent_input={
        "total_payments": 100,
        "late_payments": 2
    },
    execution_time=0.5,
    agent_version="1.0"
)
```

### Example 3: Save Analytics

```python
from app.tortoise_crud import save_analytics
from app.db_models import RiskLevel

analytics = await save_analytics(
    loan_application_id=application.id,
    credit_score=720,
    credit_tier="Good",
    risk_level=RiskLevel.MEDIUM,
    risk_score=45.5,
    approval_probability=0.85,
    recommended_amount=45000.0,
    recommended_interest_rate=7.5,
    dti_ratio=25.5,
    front_end_dti=22.0,
    back_end_dti=28.0,
    credit_score_breakdown={
        "payment_history": 280,
        "credit_age": 95
    },
    risk_factors={
        "high_utilization": False,
        "recent_inquiries": False
    },
    decision_factors={
        "primary": "good_credit_history",
        "secondary": "stable_income"
    }
)
```

### Example 4: Save Complete Loan Result (All in One Transaction)

```python
from app.tortoise_crud import save_complete_loan_result
from app.db_models import RiskLevel

application = await save_complete_loan_result(
    application_id=application.id,
    final_decision="approved",
    approved_amount=45000.0,
    interest_rate=7.5,
    credit_score=720,
    credit_tier="Good",
    risk_level=RiskLevel.MEDIUM,
    risk_score=45.5,
    approval_probability=0.85,
    agent_results=[
        {
            "agent_name": "credit_scoring",
            "output": {"credit_score": 720, "credit_tier": "Good"},
            "input": {"applicant_id": "APP123456"},
            "execution_time": 0.5
        },
        {
            "agent_name": "risk_assessment",
            "output": {"risk_level": "medium", "risk_score": 45.5},
            "input": {"credit_score": 720},
            "execution_time": 0.3
        }
    ],
    conditions=["Proof of income required"],
    credit_score_breakdown={"payment_history": 280},
    risk_factors={"high_utilization": False},
    decision_factors={"primary": "good_credit_history"},
    performed_by="ai_workflow"
)
```

### Example 5: Query Applications with Filters

```python
from app.tortoise_crud import query_applications_with_filters
from app.db_models import ApplicationStatus, RiskLevel
from datetime import datetime, timedelta

# Get all approved applications with low risk from last 30 days
applications = await query_applications_with_filters(
    status=ApplicationStatus.APPROVED,
    risk_level=RiskLevel.LOW,
    min_amount=10000.0,
    max_amount=100000.0,
    submitted_after=datetime.now() - timedelta(days=30),
    limit=50,
    offset=0
)

for app in applications:
    print(f"Application {app.id}: {app.full_name} - ${app.approved_amount}")
```

### Example 6: Get Application with All Related Data

```python
from app.tortoise_crud import get_loan_application

# Fetch with prefetch_related for efficiency
application = await get_loan_application(
    application_id=application_uuid,
    prefetch_related=True
)

if application:
    print(f"Application Status: {application.application_status}")
    print(f"Agent Results: {len(application.agent_results)}")

    # Access related agent results
    for result in application.agent_results:
        print(f"Agent: {result.agent_name}, Status: {result.status}")

    # Access related analytics
    if application.analytics:
        print(f"Credit Score: {application.analytics.credit_score}")
        print(f"Risk Level: {application.analytics.risk_level}")
```

## 🔧 Database Migrations with Aerich

### Initialize Aerich

```bash
# Install Aerich
pip install aerich

# Initialize Aerich (one-time setup)
aerich init -t app.tortoise_config.db_config.config

# Initialize database
aerich init-db
```

### Create and Apply Migrations

```bash
# Create a new migration
aerich migrate --name "add_new_field"

# Apply migrations
aerich upgrade

# Rollback migrations
aerich downgrade

# View migration history
aerich history
```

## 🔍 Monitoring and Health Checks

### Check Database Health

```python
from app.tortoise_config import health_check

status = await health_check()
print(status)
# Output: {'status': 'healthy', 'database': 'connected', ...}
```

### Get Database Statistics

```python
from app.tortoise_config import get_database_stats

stats = await get_database_stats()
print(f"Total Applications: {stats['total_applications']}")
print(f"Approved: {stats['approved_applications']}")
print(f"Rejected: {stats['rejected_applications']}")
```

## 🚨 Error Handling

All CRUD functions include comprehensive error handling:

```python
from tortoise.exceptions import DoesNotExist, IntegrityError
from app.tortoise_crud import create_loan_application

try:
    application = await create_loan_application(...)
except IntegrityError as e:
    # Handle duplicate applicant_id or constraint violation
    print(f"Integrity error: {e}")
except Exception as e:
    # Handle other errors
    print(f"Unexpected error: {e}")
```

## 📝 Environment Variables

Required environment variables:

```env
# Database Connection (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@ep-example.neon.tech/loandb?sslmode=require

# Optional: Logging
LOG_LEVEL=INFO

# Optional: Connection Pool Settings
DB_MIN_POOL_SIZE=5
DB_MAX_POOL_SIZE=20
```

## 🎯 Key Features

✅ **Async-First**: All operations use async/await for maximum performance
✅ **Transaction Support**: Critical operations wrapped in transactions
✅ **Relationship Management**: Proper foreign keys with CASCADE/SET NULL
✅ **Audit Trail**: Automatic change tracking in AuditLog
✅ **Type Safety**: Enums for status fields (ApplicationStatus, AgentStatus, RiskLevel)
✅ **JSON Fields**: Flexible storage for credit_mix, repayment_history, breakdowns
✅ **Indexes**: Optimized for common query patterns
✅ **Prefetch Support**: Efficient loading of related data
✅ **Health Monitoring**: Built-in health checks and statistics
✅ **Migration Support**: Aerich integration for schema evolution

## 🔄 Migrating from SQLAlchemy

If you have existing SQLAlchemy code, here's how to migrate:

### Before (SQLAlchemy):

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

@app.post("/loan/apply")
async def apply(request: Request, db: AsyncSession = Depends(get_db)):
    # SQLAlchemy code
    pass
```

### After (Tortoise ORM):

```python
from app.tortoise_config import lifespan_handler

app = FastAPI(lifespan=lifespan_handler)

@app.post("/loan/apply")
async def apply(request: Request):
    # Tortoise ORM code (no dependency injection needed)
    from app.tortoise_crud import create_loan_application
    application = await create_loan_application(...)
```

## 📚 Additional Resources

- [Tortoise ORM Documentation](https://tortoise.github.io/)
- [Neon PostgreSQL Documentation](https://neon.tech/docs)
- [Aerich Migrations](https://github.com/tortoise/aerich)
- [FastAPI with Tortoise](https://tortoise.github.io/examples/fastapi.html)

## 🐛 Troubleshooting

### Connection Issues

```python
# Test connection
from app.tortoise_config import health_check

status = await health_check()
if status['status'] != 'healthy':
    print(f"Database error: {status.get('error')}")
```

### Schema Generation Issues

```python
# Reset database (WARNING: deletes all data)
from app.tortoise_config import reset_database
await reset_database()
```

### Query Performance

```python
# Always use prefetch_related for related data
application = await get_loan_application(
    application_id=uuid,
    prefetch_related=True  # This is efficient
)

# This causes N+1 queries (inefficient)
application = await get_loan_application(uuid, prefetch_related=False)
for result in application.agent_results:  # Causes extra queries
    print(result.agent_name)
```

## 📄 License

This code is part of the Loan Processing AI Agent project.

---

**Created**: 2024
**Status**: Production Ready ✅
**Database**: Neon PostgreSQL
**ORM**: Tortoise ORM 0.21.0
