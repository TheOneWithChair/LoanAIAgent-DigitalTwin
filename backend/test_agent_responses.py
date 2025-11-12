"""
Test script to check AI agent responses with Groq API
This will submit a loan application and show you the detailed agent responses
"""

import requests
import json
from datetime import datetime

# API endpoint
API_URL = "http://127.0.0.1:8000/submit_loan_application"

# Test loan application data
test_application = {
    "applicant_id": "TEST001",
    "full_name": "Jane Smith",
    "date_of_birth": "1985-05-20",
    "phone_number": "+1-555-0123",
    "email": "jane.smith@example.com",
    "address": "456 Oak Ave, Los Angeles, CA 90001",
    
    # Credit History
    "credit_history_length_months": 84,
    "number_of_credit_accounts": 7,
    "credit_mix": {
        "secured_loans": 2,
        "unsecured_loans": 5
    },
    "credit_utilization_percent": 25.0,
    "recent_credit_inquiries_6m": 1,
    "repayment_history": {
        "on_time_payments": 80,
        "late_payments": 1,
        "defaults": 0,
        "write_offs": 0
    },
    
    # Employment
    "employment_status": "Employed",
    "employment_duration_months": 48,
    "monthly_income": 7500.0,
    "income_verified": True,
    
    # Loan Details
    "loan_amount_requested": 75000.0,
    "loan_purpose": "business",
    "loan_tenure_months": 84,
    "loan_to_value_ratio_percent": 70.0,
    "bank_lender": "Metro Bank",
    "days_past_due": 0,
    "existing_debts": "Mortgage: $1200/month, Car loan: $400/month",
    "risk_notes": "Excellent payment history, stable income"
}

print("="*80)
print("🚀 TESTING LOAN AI AGENT WITH GROQ API")
print("="*80)
print(f"\n📋 Applicant: {test_application['full_name']}")
print(f"💰 Loan Amount: ${test_application['loan_amount_requested']:,.2f}")
print(f"🎯 Purpose: {test_application['loan_purpose']}")
print(f"📊 Monthly Income: ${test_application['monthly_income']:,.2f}")
print(f"⏱️  Credit History: {test_application['credit_history_length_months']} months")

print("\n" + "="*80)
print("📤 SENDING APPLICATION TO AI AGENTS...")
print("="*80)

try:
    # Send POST request
    response = requests.post(
        API_URL,
        json=test_application,
        headers={"Content-Type": "application/json"},
        timeout=120  # 2 minutes timeout for AI processing
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        
        print("\n" + "="*80)
        print("🤖 AI AGENT RESPONSE")
        print("="*80)
        
        # Application Info
        print(f"\n📝 Application ID: {result.get('application_id', 'N/A')}")
        print(f"📋 Applicant ID: {result.get('applicant_id', 'N/A')}")
        print(f"✅ Status: {result.get('status', 'N/A')}")
        print(f"💬 Message: {result.get('message', 'N/A')}")
        
        # Final Decision
        print("\n" + "="*80)
        print("� LOAN DECISION")
        print("="*80)
        decision = result.get('final_decision', 'N/A').upper()
        icon = "✅" if decision == "APPROVED" else "❌" if decision == "REJECTED" else "⏳"
        print(f"\n{icon} DECISION: {decision}")
        print(f"� Credit Score: {result.get('calculated_credit_score', 'N/A')}")
        print(f"⚠️  Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"� Approved Amount: ${result.get('approved_amount', 0):,.2f}")
        print(f"📈 Interest Rate: {result.get('interest_rate', 0):.2f}%")
        
        # Save full response to file
        with open('agent_response_output.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full response saved to: agent_response_output.json")
        
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to API server")
    print("   Make sure the backend server is running at http://127.0.0.1:8000")
    print("   Run: cd backend && python -m uvicorn app.main:app --reload")

except requests.exceptions.Timeout:
    print("\n⏱️  ERROR: Request timed out (took longer than 2 minutes)")
    print("   The AI agents might be processing. Check server logs.")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "="*80)
print("✨ TEST COMPLETE")
print("="*80)

# To run the server, use the following commands:
# cd g:\dbs\LoanAIAgent-DigitalTwin\backend
# venv\Scripts\activate
# python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
