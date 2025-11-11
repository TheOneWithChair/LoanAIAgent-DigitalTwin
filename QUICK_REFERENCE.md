# ⚡ Quick Reference Guide

## 🚀 Start Development (5 Minutes)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements-agents.txt
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY
python setup_database.py
python -m uvicorn app.main:app --reload
```

**Backend ready at**: http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

**Frontend ready at**: http://localhost:3000

---

## 🔑 Required Environment Variables

### Backend `.env`

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech/db?sslmode=require
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📡 API Endpoints

| Method | Endpoint                   | Purpose                |
| ------ | -------------------------- | ---------------------- |
| POST   | `/submit_loan_application` | Submit new application |
| GET    | `/health`                  | Health check           |
| GET    | `/docs`                    | Swagger UI             |
| GET    | `/redoc`                   | ReDoc UI               |

---

## 🧪 Quick Test

### PowerShell

```powershell
cd backend
powershell -File test_api.ps1
```

### cURL

```bash
curl -X POST http://localhost:8000/submit_loan_application \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

---

## 🗄️ Database Quick Commands

### Connect to Neon

```bash
psql postgresql://user:pass@host.neon.tech/db
```

### View Applications

```sql
SELECT application_id, final_decision, approved_amount
FROM loan_applications
ORDER BY created_at DESC
LIMIT 10;
```

### View Agent Logs

```sql
SELECT agent_name, status, execution_time_seconds
FROM agent_execution_logs
WHERE application_id = 'LA-20251111-ABC123';
```

### Check Processing Times

```sql
SELECT agent_name, AVG(execution_time_seconds) as avg_time
FROM agent_execution_logs
GROUP BY agent_name;
```

---

## 🤖 Agent Flow

```
Application → Credit Scoring → Loan Decision → Verification → Risk Monitoring → Database → Response
```

### Agent Outputs

| Agent               | Key Outputs                                            |
| ------------------- | ------------------------------------------------------ |
| **Credit Scoring**  | `credit_score`, `risk_factors`, `recommendations`      |
| **Loan Decision**   | `decision`, `approved_amount`, `interest_rate`         |
| **Verification**    | `status`, `confidence_level`, `flagged_items`          |
| **Risk Monitoring** | `risk_level`, `fraud_indicators`, `monitoring_actions` |

---

## 🐛 Common Issues & Fixes

### "Database connection failed"

```bash
# Check DATABASE_URL has postgresql+asyncpg:// prefix
# Ensure ?sslmode=require is at the end
# Verify Neon project is active (not paused)
```

### "Module not found: langgraph"

```bash
pip install -r requirements-agents.txt
```

### "CORS error" in frontend

```env
# In backend/.env, add:
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend "Network Error"

```bash
# Ensure backend is running:
curl http://localhost:8000/health
```

---

## 📊 File Locations

### Key Backend Files

| File                  | Purpose           |
| --------------------- | ----------------- |
| `app/main.py`         | FastAPI app entry |
| `app/orchestrator.py` | LangGraph agents  |
| `app/models.py`       | Database ORM      |
| `app/schemas.py`      | Pydantic models   |
| `app/config.py`       | Settings          |

### Key Frontend Files

| File                           | Purpose      |
| ------------------------------ | ------------ |
| `src/app/page.tsx`             | Landing page |
| `src/app/application/page.tsx` | Loan form    |
| `src/app/layout.tsx`           | Root layout  |

---

## 🔄 Development Workflow

### 1. Make Changes

```bash
# Backend: Edit files in backend/app/
# Frontend: Edit files in frontend/src/app/
```

### 2. Test Locally

```bash
# Backend auto-reloads (--reload flag)
# Frontend auto-reloads (npm run dev)
```

### 3. Check API Docs

Visit http://localhost:8000/docs

### 4. Test End-to-End

1. Go to http://localhost:3000
2. Fill form
3. Submit
4. Check database

---

## 📦 Deploy to Production

### Backend (Render)

```bash
git push origin main
# Connect Render to GitHub repo
# Add env vars in Render dashboard
```

### Frontend (Vercel)

```bash
cd frontend
vercel
# Or connect GitHub repo to Vercel
```

### Environment Variables

Set in deployment platform dashboard:

- `DATABASE_URL`
- `OPENAI_API_KEY`
- `CORS_ORIGINS`
- `NEXT_PUBLIC_API_URL`

---

## 🎯 Testing Checklist

- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Database connection: `python setup_database.py`
- [ ] API test: `powershell -File test_api.ps1`
- [ ] Frontend loads: Open http://localhost:3000
- [ ] Form submits successfully
- [ ] Database records created
- [ ] Agent logs saved
- [ ] Response includes all fields

---

## 📚 Documentation Links

| Document                                               | Purpose            |
| ------------------------------------------------------ | ------------------ |
| [README.md](README.md)                                 | Project overview   |
| [DEPLOYMENT.md](DEPLOYMENT.md)                         | Deployment guide   |
| [AGENTS_README.md](backend/AGENTS_README.md)           | Agent architecture |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | What's been built  |

---

## 🆘 Get Help

1. Check API docs: http://localhost:8000/docs
2. View logs: Check terminal output
3. Database: Query `agent_execution_logs` for errors
4. Review documentation files above

---

## ⚡ Power User Tips

### Restart Everything

```powershell
# Stop servers (Ctrl+C)
cd backend
python -m uvicorn app.main:app --reload

# New terminal
cd frontend
npm run dev
```

### Reset Database

```bash
python setup_database.py
# Drops and recreates all tables
```

### View Real-time Logs

```bash
# Backend: Watch terminal where uvicorn is running
# Database: Check Neon dashboard → Monitoring
```

### Test Specific Agent

```python
from app.orchestrator import credit_scoring_agent, LoanProcessingState

state = LoanProcessingState(
    application_id="TEST-123",
    application_data={...}
)
result = credit_scoring_agent(state)
print(result)
```

---

<div align="center">

**Need more details?** See [README.md](README.md) or [DEPLOYMENT.md](DEPLOYMENT.md)

**Ready to code?** Start with [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

</div>
