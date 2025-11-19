# Tortoise ORM Quick Reference Guide

## 🚀 Quick Start Commands

### 1. Install Dependencies

```bash
pip install -r requirements_tortoise.txt
```

### 2. Set Environment Variable

```bash
# Windows CMD
set DATABASE_URL=postgresql://user:password@ep-example.neon.tech/loandb?sslmode=require

# Windows PowerShell
$env:DATABASE_URL="postgresql://user:password@ep-example.neon.tech/loandb?sslmode=require"

# Linux/Mac
export DATABASE_URL=postgresql://user:password@ep-example.neon.tech/loandb?sslmode=require
```

### 3. Test Setup

```bash
python test_tortoise_setup.py
```

### 4. Run with FastAPI

```bash
uvicorn app.main_tortoise_example:app --reload
```

---

## 📝 Common Operations Cheat Sheet

### Initialize Database (Startup)

```python
from app.tortoise_config import init_database

await init_database(generate_schemas=True, safe=True)
```

### Close Database (Shutdown)

```python
from app.tortoise_config import close_database

await close_database()
```

### FastAPI Integration

```python
from fastapi import FastAPI
from app.tortoise_config import lifespan_handler

app = FastAPI(lifespan=lifespan_handler)  # Auto init/close
```

---

## 🔨 CRUD Operations

### Create Loan Application

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
    total_payments=100,
    late_payments=2,
    utilization=30.0
)
```

### Get Application by ID

```python
from app.tortoise_crud import get_loan_application
from uuid import UUID

application = await get_loan_application(
    application_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    prefetch_related=True  # Include agent_results and analytics
)
```

### Get Applications by Applicant

```python
from app.tortoise_crud import get_loan_applications_by_applicant

applications = await get_loan_applications_by_applicant(
    applicant_id="APP123456",
    include_related=True
)
```

### Save Agent Result

```python
from app.tortoise_crud import save_agent_result
from app.db_models import AgentStatus

result = await save_agent_result(
    loan_application_id=application.id,
    agent_name="credit_scoring",
    status=AgentStatus.SUCCESS,
    output={"credit_score": 720, "tier": "Good"},
    execution_time=0.5
)
```

### Save Analytics

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
    recommended_interest_rate=7.5
)
```

### Update Application Status

```python
from app.tortoise_crud import update_loan_application_status
from app.db_models import ApplicationStatus

application = await update_loan_application_status(
    application_id=application.id,
    new_status=ApplicationStatus.APPROVED,
    final_decision="approved",
    approved_amount=45000.0,
    interest_rate=7.5,
    performed_by="ai_workflow"
)
```

### Save Complete Result (All-in-One)

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
            "output": {"credit_score": 720},
            "input": {"applicant_id": "APP123"},
            "execution_time": 0.5
        }
    ],
    conditions=["Proof of income required"],
    performed_by="ai_workflow"
)
```

### Query with Filters

```python
from app.tortoise_crud import query_applications_with_filters
from app.db_models import ApplicationStatus, RiskLevel
from datetime import datetime, timedelta

applications = await query_applications_with_filters(
    status=ApplicationStatus.APPROVED,
    risk_level=RiskLevel.LOW,
    min_amount=10000.0,
    max_amount=100000.0,
    submitted_after=datetime.now() - timedelta(days=30),
    limit=50,
    offset=0
)
```

---

## 🔍 Querying Tips

### Efficient Fetching (Use prefetch_related)

```python
# ✅ EFFICIENT - One query with JOIN
application = await get_loan_application(
    application_id=uuid,
    prefetch_related=True
)
for result in application.agent_results:
    print(result.agent_name)  # No extra query

# ❌ INEFFICIENT - N+1 queries
application = await get_loan_application(uuid, prefetch_related=False)
for result in application.agent_results:  # Each iteration = 1 query
    print(result.agent_name)
```

### Direct Tortoise Queries

```python
from app.db_models import LoanApplication

# Get all applications
apps = await LoanApplication.all()

# Filter by status
approved = await LoanApplication.filter(
    application_status="approved"
).all()

# Count applications
count = await LoanApplication.all().count()

# Order by date
recent = await LoanApplication.all().order_by("-submitted_at").limit(10)

# Complex filters
high_value = await LoanApplication.filter(
    requested_amount__gte=50000,
    application_status="approved"
).prefetch_related("agent_results", "analytics")
```

---

## 🎯 Enums Reference

### ApplicationStatus

- `ApplicationStatus.IN_PROGRESS` - "in_progress"
- `ApplicationStatus.APPROVED` - "approved"
- `ApplicationStatus.REJECTED` - "rejected"
- `ApplicationStatus.CONDITIONAL` - "conditional"

### AgentStatus

- `AgentStatus.SUCCESS` - "success"
- `AgentStatus.FAILED` - "failed"
- `AgentStatus.PENDING` - "pending"

### RiskLevel

- `RiskLevel.LOW` - "low"
- `RiskLevel.MEDIUM` - "medium"
- `RiskLevel.HIGH` - "high"
- `RiskLevel.VERY_HIGH` - "very_high"

---

## 🔧 Database Management

### Health Check

```python
from app.tortoise_config import health_check

status = await health_check()
print(status)
# {'status': 'healthy', 'database': 'connected', ...}
```

### Get Statistics

```python
from app.tortoise_config import get_database_stats

stats = await get_database_stats()
print(f"Total: {stats['total_applications']}")
print(f"Approved: {stats['approved_applications']}")
```

### Reset Database (⚠️ DANGER - Deletes all data!)

```python
from app.tortoise_config import reset_database

await reset_database()  # Drop and recreate all tables
```

---

## 🔄 Migrations with Aerich

### Initial Setup

```bash
# Install Aerich
pip install aerich

# Initialize (one-time)
aerich init -t app.tortoise_config.db_config.config

# Create initial schema
aerich init-db
```

### Create Migration

```bash
# After modifying models in db_models.py
aerich migrate --name "add_new_field"
```

### Apply Migrations

```bash
aerich upgrade
```

### Rollback Migration

```bash
aerich downgrade
```

### View History

```bash
aerich history
```

---

## 🚨 Error Handling

```python
from tortoise.exceptions import DoesNotExist, IntegrityError

try:
    application = await get_loan_application(uuid)
    if not application:
        print("Application not found")
except DoesNotExist:
    print("Application does not exist")
except IntegrityError as e:
    print(f"Database constraint violation: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 📊 Model Relationships

### LoanApplication → AgentResult (One-to-Many)

```python
application = await get_loan_application(uuid, prefetch_related=True)

# Access related agent results
for result in application.agent_results:
    print(f"{result.agent_name}: {result.status}")
```

### LoanApplication → ApplicationAnalytics (One-to-One)

```python
application = await get_loan_application(uuid, prefetch_related=True)

# Access related analytics
if application.analytics:
    print(f"Credit Score: {application.analytics.credit_score}")
    print(f"Risk Level: {application.analytics.risk_level}")
```

### LoanApplication → AuditLog (One-to-Many)

```python
from app.db_models import AuditLog

# Get audit logs for application
logs = await AuditLog.filter(
    loan_application_id=uuid
).order_by("-timestamp")

for log in logs:
    print(f"{log.timestamp}: {log.action}")
```

---

## 💡 Best Practices

### ✅ DO

- Use `prefetch_related` for related data
- Use transactions for multi-step operations
- Use enums for status fields
- Always handle `DoesNotExist` exceptions
- Close database connections on shutdown
- Use UUID for primary keys

### ❌ DON'T

- Don't use raw SQL unless necessary
- Don't forget to prefetch for N+1 queries
- Don't hardcode database URLs
- Don't skip error handling
- Don't create circular imports

---

## 🔗 Useful Links

- [Tortoise ORM Docs](https://tortoise.github.io/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [Aerich Migrations](https://github.com/tortoise/aerich)
- [FastAPI + Tortoise](https://tortoise.github.io/examples/fastapi.html)

---

## 📞 Common Issues & Solutions

### Issue: Connection Failed

**Solution:** Check DATABASE_URL format and network connectivity

```python
# Test connection
from app.tortoise_config import health_check
status = await health_check()
```

### Issue: Table doesn't exist

**Solution:** Run schema generation

```python
await init_database(generate_schemas=True, safe=True)
```

### Issue: N+1 Query Problem

**Solution:** Always use prefetch_related

```python
# ✅ Efficient
app = await get_loan_application(uuid, prefetch_related=True)

# ❌ Inefficient
app = await get_loan_application(uuid, prefetch_related=False)
```

### Issue: Migration conflicts

**Solution:** Reset migrations (development only)

```bash
rm -rf migrations/
aerich init -t app.tortoise_config.db_config.config
aerich init-db
```

---

**Last Updated:** 2024
**Status:** Production Ready ✅
