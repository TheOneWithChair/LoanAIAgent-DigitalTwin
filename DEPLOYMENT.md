# 🚀 Deployment Guide - Loan AI Agent System

Complete step-by-step guide to deploy your loan processing system with LangGraph AI agents.

---

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **Neon DB Account**: [Sign up at neon.tech](https://neon.tech)
- **OpenAI API Key**: [Get from platform.openai.com](https://platform.openai.com)

---

## 🗄️ Database Setup (Neon DB)

### Step 1: Create Neon Project

1. Go to [neon.tech](https://neon.tech) and sign up
2. Click "Create a project"
3. Choose a region (closest to your users)
4. Note your connection string

### Step 2: Configure Connection

Your Neon connection string looks like:

```
postgresql://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

Copy it to your `.env` file:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and paste your connection string:

```env
DATABASE_URL=postgresql+asyncpg://username:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Important**: Change `postgresql://` to `postgresql+asyncpg://` for async support!

### Step 3: Initialize Database

```bash
# Install dependencies
pip install -r requirements-agents.txt

# Run database setup
python setup_database.py
```

Expected output:

```
✅ Database connection successful!
✅ All tables created successfully!
✅ loan_applications table exists
✅ agent_execution_logs table exists
```

---

## 🔑 API Keys Configuration

### OpenAI API Key

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Add to `.env`:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### Anthropic API Key (Optional)

If you want to use Claude models:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

---

## 🖥️ Backend Deployment

### Local Development

```bash
cd backend

# Activate virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements-agents.txt

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at:

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Production Deployment (Render/Railway/Fly.io)

#### Option 1: Render

1. Create `render.yaml`:

```yaml
services:
  - type: web
    name: loan-ai-backend
    runtime: python
    buildCommand: pip install -r requirements-agents.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: CORS_ORIGINS
        value: https://your-frontend-domain.vercel.app
```

2. Push to GitHub
3. Connect Render to your repo
4. Add environment variables in Render dashboard

#### Option 2: Railway

```bash
railway login
railway init
railway add
railway up
```

Add environment variables:

```bash
railway variables set DATABASE_URL=postgresql+asyncpg://...
railway variables set OPENAI_API_KEY=sk-proj-...
```

#### Option 3: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-agents.txt .
RUN pip install --no-cache-dir -r requirements-agents.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t loan-ai-backend .
docker run -p 8000:8000 --env-file .env loan-ai-backend
```

---

## 🌐 Frontend Deployment

### Local Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at: http://localhost:3000

### Production Deployment (Vercel)

#### Automatic Deployment

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "Import Project"
4. Select your repository
5. Vercel auto-detects Next.js
6. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```
7. Deploy!

#### Manual Deployment

```bash
npm install -g vercel
cd frontend
vercel
```

Follow the prompts and add environment variables when asked.

---

## 🔗 Connecting Frontend to Backend

### Update Frontend API URL

Edit `frontend/src/app/application/page.tsx`:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const response = await fetch(`${API_URL}/submit_loan_application`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(applicationData),
});
```

### Update Backend CORS

Edit `backend/.env`:

```env
CORS_ORIGINS=["https://your-frontend-domain.vercel.app", "http://localhost:3000"]
```

---

## 🧪 Testing the Complete System

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected:

```json
{ "status": "healthy" }
```

### 2. Submit Test Application

```bash
# Using PowerShell (Windows)
powershell -File backend/test_api.ps1

# Using curl (Mac/Linux)
curl -X POST http://localhost:8000/submit_loan_application \
  -H "Content-Type: application/json" \
  -d @backend/test_payload.json
```

Expected response:

```json
{
  "application_id": "LA-20251111-ABC123",
  "status": "processing_started",
  "final_decision": "approved",
  "calculated_credit_score": 720,
  "risk_level": "medium",
  "approved_amount": 45000.0,
  "interest_rate": 5.25
}
```

### 3. Verify Database

Check Neon dashboard → Tables → `loan_applications`

Should see your test application with all agent results stored in JSON columns.

### 4. Frontend Test

1. Go to http://localhost:3000
2. Click "Apply for Loan"
3. Fill out the form
4. Submit and verify success message

---

## 📊 Monitoring & Logging

### View Application Logs

```bash
# Backend logs (if using uvicorn)
tail -f uvicorn.log

# Or check your deployment platform's logs
render logs
railway logs
vercel logs
```

### Database Queries

Connect to Neon with psql:

```bash
psql postgresql://username:password@ep-xxx.neon.tech/neondb
```

Useful queries:

```sql
-- View all applications
SELECT application_id, status, final_decision, created_at
FROM loan_applications
ORDER BY created_at DESC;

-- View agent execution logs
SELECT application_id, agent_name, status, execution_time_seconds
FROM agent_execution_logs
WHERE application_id = 'LA-20251111-ABC123';

-- Check processing times
SELECT agent_name, AVG(execution_time_seconds) as avg_time
FROM agent_execution_logs
GROUP BY agent_name;
```

---

## 🔒 Security Best Practices

### Environment Variables

✅ **DO:**

- Store all secrets in `.env` file (never commit)
- Use environment variables in production
- Rotate API keys regularly
- Use different keys for dev/staging/prod

❌ **DON'T:**

- Commit `.env` to Git
- Hardcode API keys in code
- Share keys in chat/email

### Database

- Use connection pooling (already configured)
- Enable SSL (Neon requires it)
- Regularly backup data (Neon auto-backup)
- Monitor for unusual activity

### API

- Keep CORS origins restrictive
- Add rate limiting in production
- Validate all inputs (already done with Pydantic)
- Log security events

---

## 🐛 Troubleshooting

### "Database connection failed"

**Issue**: Can't connect to Neon
**Fix**:

1. Check DATABASE_URL has `postgresql+asyncpg://` prefix
2. Ensure `?sslmode=require` is in connection string
3. Verify Neon project is active (not paused)

### "Module not found: langgraph"

**Issue**: Missing dependencies
**Fix**:

```bash
pip install -r requirements-agents.txt
```

### "CORS error" in frontend

**Issue**: Frontend can't reach backend
**Fix**:

1. Check backend CORS_ORIGINS in `.env`
2. Add frontend URL: `CORS_ORIGINS=["http://localhost:3000"]`
3. Restart backend server

### "OpenAI API key error"

**Issue**: Invalid or missing API key
**Fix**:

1. Verify key starts with `sk-proj-` or `sk-`
2. Check key is set in `.env`: `OPENAI_API_KEY=...`
3. Restart server after adding key

### Frontend shows "Network Error"

**Issue**: Can't reach backend
**Fix**:

1. Check backend is running: `curl http://localhost:8000/health`
2. Verify API_URL in frontend matches backend address
3. Check firewall/network settings

---

## 📈 Performance Optimization

### Database

- Add indexes on frequently queried columns
- Use connection pooling (already configured)
- Monitor query performance in Neon dashboard

### Backend

- Use async/await throughout (already done)
- Add Redis for caching frequent queries
- Implement request timeout (configured: 30s)

### Frontend

- Enable Next.js image optimization
- Add loading skeletons
- Implement optimistic UI updates

---

## 🔄 Continuous Integration/Deployment

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## 📞 Support & Resources

- **Documentation**: See `AGENTS_README.md` for architecture details
- **API Docs**: http://your-backend-url/docs
- **Neon Docs**: https://neon.tech/docs
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

## ✅ Deployment Checklist

- [ ] Neon DB project created
- [ ] Database tables initialized
- [ ] OpenAI API key configured
- [ ] Backend deployed and healthy
- [ ] Frontend deployed
- [ ] CORS configured correctly
- [ ] Test application submitted successfully
- [ ] Database records verified
- [ ] Monitoring set up
- [ ] Backups configured

---

**🎉 Congratulations!** Your AI-powered loan processing system is now live!
