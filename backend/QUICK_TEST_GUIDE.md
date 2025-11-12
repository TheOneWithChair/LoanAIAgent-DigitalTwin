# 🚀 QUICK START: Testing AI Agent Responses

## Problem Fixed!

- ✅ Updated API endpoint to `/submit_loan_application`
- ✅ Fixed response parsing to match actual API structure
- ✅ Created easy-to-use batch files

## How to Test (2 Steps)

### Step 1: Start the Server

**Open PowerShell/CMD Terminal 1:**

```cmd
cd g:\dbs\LoanAIAgent-DigitalTwin\backend
start_server_no_reload.bat
```

Wait for: `INFO: Application startup complete.`

### Step 2: Run the Test

**Open PowerShell/CMD Terminal 2:**

```cmd
cd g:\dbs\LoanAIAgent-DigitalTwin\backend
run_test.bat
```

## What You'll See

```
================================================================================
🚀 TESTING LOAN AI AGENT WITH GROQ API
================================================================================

📋 Applicant: Jane Smith
💰 Loan Amount: $75,000.00
🎯 Purpose: business
📊 Monthly Income: $7,500.00

================================================================================
📤 SENDING APPLICATION TO AI AGENTS...
================================================================================

✅ Response Status: 201

================================================================================
🤖 AI AGENT RESPONSE
================================================================================

📝 Application ID: LA-20251112-XXXXXXX
📋 Applicant ID: TEST001
✅ Status: success
💬 Message: Loan application processed successfully

================================================================================
🎯 LOAN DECISION
================================================================================

✅ DECISION: APPROVED
💳 Credit Score: 742
⚠️  Risk Level: low
💰 Approved Amount: $75,000.00
📈 Interest Rate: 5.75%

💾 Full response saved to: agent_response_output.json
```

## Alternative: Manual Test

If you prefer, run directly:

**Terminal 1 (Server):**

```cmd
cd g:\dbs\LoanAIAgent-DigitalTwin\backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 (Test):**

```cmd
cd g:\dbs\LoanAIAgent-DigitalTwin\backend
.\venv\Scripts\python.exe test_agent_responses.py
```

## Troubleshooting

**"Port 8000 is already in use":**

```cmd
netstat -ano | findstr :8000
taskkill /F /PID <PID_NUMBER>
```

**"Module not found":**

- Make sure you're in the `backend` folder
- Check that `venv` is activated

## Next: View in Browser

While server is running, open:

- **API Docs**: http://127.0.0.1:8000/docs
- **Try endpoint**: POST /submit_loan_application

---

**Ready to test? Just run the 2 commands above!** 🎯
