# 🧪 HOW TO TEST AI AGENT RESPONSES

## Quick Testing Guide

### Method 1: Using the Test Script (RECOMMENDED)

**Step 1: Start the Backend Server**

Open a **NEW PowerShell terminal** and run:

```powershell
cd g:\dbs\LoanAIAgent-DigitalTwin\backend
.\start_server.bat
```

**Wait for this message:**

```
INFO:     Application startup complete.
API will run in Groq-only mode without database persistence
```

**Step 2: Open ANOTHER PowerShell Terminal**

Leave the server running and open a **second terminal**, then run:

```powershell
cd g:\dbs\LoanAIAgent-DigitalTwin\backend
.\venv\Scripts\python.exe test_agent_responses.py
```

This will:

- ✅ Send a test loan application
- ✅ Show detailed responses from all 4 AI agents
- ✅ Display credit score, loan decision, verification status, risk assessment
- ✅ Save full response to `agent_response_output.json`

---

### Method 2: Using API Docs (Interactive)

**Step 1: Start the Server** (same as above)

**Step 2: Open Browser**

- Go to: http://127.0.0.1:8000/docs
- This opens the **interactive API documentation**

**Step 3: Test the Loan Application Endpoint**

1. Click on `POST /api/loan/application`
2. Click "Try it out"
3. Use this sample data (or modify):

```json
{
  "applicant_id": "TEST002",
  "full_name": "Sarah Johnson",
  "date_of_birth": "1992-08-15",
  "phone_number": "+1-555-9876",
  "email": "sarah.j@email.com",
  "address": "789 Pine St, Chicago, IL 60601",
  "credit_history_length_months": 96,
  "number_of_credit_accounts": 8,
  "credit_mix": {
    "secured_loans": 3,
    "unsecured_loans": 5
  },
  "credit_utilization_percent": 15.0,
  "recent_credit_inquiries_6m": 0,
  "repayment_history": {
    "on_time_payments": 95,
    "late_payments": 1,
    "defaults": 0,
    "write_offs": 0
  },
  "employment_status": "Employed",
  "employment_duration_months": 72,
  "monthly_income": 9500.0,
  "income_verified": true,
  "loan_amount_requested": 100000.0,
  "loan_purpose": "business",
  "loan_tenure_months": 120,
  "loan_to_value_ratio_percent": 65.0,
  "bank_lender": "Capital Bank",
  "days_past_due": 0,
  "existing_debts": "Mortgage: $1500/month",
  "risk_notes": "Excellent credit profile, long employment history"
}
```

4. Click "Execute"
5. **See the AI agent responses!**

---

### Method 3: Using Frontend (Full Experience)

**Step 1: Start Backend** (same as above)

**Step 2: Start Frontend**

Open **another terminal**:

```powershell
cd g:\dbs\LoanAIAgent-DigitalTwin\frontend
npm run dev
```

**Step 3: Open Browser**

- Go to: http://localhost:3000/application
- Fill out the loan application form
- Click "Submit Application"
- **See the AI agent responses in real-time!**

---

## 🔍 What You'll See in the Response

### 1. Credit Scoring Agent

```json
{
  "calculated_credit_score": 742,
  "credit_tier": "Good",
  "credit_score_rationale": "Score based on payment history...",
  "credit_score_factors": [
    "Credit history: 96 months",
    "Payment history: 99.0% on-time",
    "Credit utilization: 15.0%",
    ...
  ]
}
```

### 2. Loan Decision Agent

```json
{
  "final_decision": "approved",
  "approved_amount": 100000.0,
  "interest_rate": 5.75,
  "decision_rationale": "Applicant meets all criteria...",
  "conditions": [
    "Maintain current employment",
    "Provide income verification",
    ...
  ]
}
```

### 3. Verification Agent

```json
{
  "verification_status": "verified",
  "verification_checks": [
    "✓ Income verified",
    "✓ Employment status confirmed",
    "✓ Credit history validated",
    ...
  ],
  "flags_raised": []
}
```

### 4. Risk Monitoring Agent

```json
{
  "risk_score": 25,
  "risk_category": "Low Risk",
  "risk_assessment": "Applicant shows strong indicators...",
  "mitigation_strategies": [
    "Regular income verification",
    "Quarterly credit monitoring",
    ...
  ]
}
```

---

## 💡 Testing Different Scenarios

### High-Risk Applicant

```json
{
  "credit_utilization_percent": 85.0,
  "recent_credit_inquiries_6m": 8,
  "repayment_history": {
    "on_time_payments": 20,
    "late_payments": 15,
    "defaults": 2,
    "write_offs": 1
  },
  "monthly_income": 3000.0,
  "loan_amount_requested": 150000.0
}
```

### Ideal Applicant

```json
{
  "credit_utilization_percent": 10.0,
  "recent_credit_inquiries_6m": 0,
  "repayment_history": {
    "on_time_payments": 120,
    "late_payments": 0,
    "defaults": 0,
    "write_offs": 0
  },
  "monthly_income": 15000.0,
  "loan_amount_requested": 50000.0
}
```

---

## 🛠️ Troubleshooting

**Server won't stay running?**

- Make sure you're not running the timeout command
- Keep the server terminal open and active
- Don't press any keys in the server terminal

**"Connection refused" error?**

- Server isn't running
- Check if port 8000 is already in use
- Try: `netstat -ano | findstr :8000`

**AI responses seem generic?**

- Currently using simplified logic (rule-based)
- To enable full Groq AI responses:
  - Uncomment the AI calls in `app/orchestrator.py`
  - Or check that your Groq API key is valid

---

## 📊 Expected Response Time

- **Rule-based (current)**: < 1 second
- **With Groq AI**: 2-5 seconds per agent
- **Total processing**: 5-15 seconds with AI

---

## 🎯 Next Steps

After testing responses:

1. ✅ Verify all 4 agents return data
2. ✅ Check that credit scores are calculated correctly
3. ✅ Confirm loan decisions match the logic
4. ✅ Review the JSON structure for frontend integration
5. ✅ Test with different loan amounts and credit profiles

---

**Ready to test? Start with Method 1 (test script) - it's the easiest!** 🚀
