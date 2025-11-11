# 🚀 Quick Reference Card

## Start Backend Server

```powershell
cd G:\dbs\LoanAIAgent-DigitalTwin\backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='$PWD'; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
```

## Start Frontend Server

```bash
cd G:\dbs\LoanAIAgent-DigitalTwin\frontend
npm run dev
```

## Test Backend API

```powershell
cd G:\dbs\LoanAIAgent-DigitalTwin\backend
.\test_api.ps1
```

## URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Status

- ✅ Backend: WORKING (Tested successfully)
- ⏳ Frontend: Ready to start
- ✅ API Schema: Validated
- ✅ CORS: Configured
- ✅ Validation: Active
