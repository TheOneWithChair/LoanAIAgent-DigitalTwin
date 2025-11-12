"""
Test script to check AI agent responses with Groq API
This will submit a loan application and show you the detailed agent responses
"""

import requests
import json
from datetime import datetime

# API endpoint
API_URL = "http://127.0.0.1:8000/submit_loan_application"

# Test loan application data (Indian format)
test_application = {
    "applicant_id": "IND001",
    "full_name": "Rahul Sharma",
    "date_of_birth": "1987-08-15",
    "phone_number": "+91-9876543210",
    "email": "rahul.sharma@example.in",
    "address": "123, MG Road, Bengaluru, Karnataka, 560001",
    
    # Credit History
    "credit_history_length_months": 72,
    "number_of_credit_accounts": 5,
    "credit_mix": {
        "secured_loans": 1,
        "unsecured_loans": 4
    },
    "credit_utilization_percent": 45.0,
    "recent_credit_inquiries_6m": 2,
    "repayment_history": {
        "on_time_payments": 65,
        "late_payments": 3,
        "defaults": 0,
        "write_offs": 0
    },
    
    # Employment
    "employment_status": "Employed",
    "employment_duration_months": 60,
    "monthly_income": 60000.0,
    "income_verified": True,
    
    # Loan Details
    "loan_amount_requested": 1500000.0,  # 15 lakhs INR
    "loan_purpose": "home",
    "loan_tenure_months": 120,
    "loan_to_value_ratio_percent": 60.0,
    "bank_lender": "SBI",
    "days_past_due": 0,
    "existing_debts": "Car loan EMI: 15000 INR/month",
    "risk_notes": "Good repayment history, stable salaried job"
}

print("="*80)
print("🚀 TESTING LOAN AI AGENT WITH GROQ API - INDIAN DATA")
print("="*80)
print(f"\n📋 Applicant: {test_application['full_name']}")
print(f"💰 Loan Amount: ₹{test_application['loan_amount_requested']:,.2f}")
print(f"🎯 Purpose: {test_application['loan_purpose']}")
print(f"📊 Monthly Income: ₹{test_application['monthly_income']:,.2f}")
print(f"⏱️  Credit History: {test_application['credit_history_length_months']} months")

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
        print(f"⚠️  Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"� Approved Amount: ₹{result.get('approved_amount', 0):,.2f}")
        print(f"📈 Interest Rate: {result.get('interest_rate', 0):.2f}%")
        
        # Save full response to file
        with open('agent_response_output_in_india.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full response saved to: agent_response_output_in_india.json")
        
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to API server")
    print("   Make sure the backend server is running at http://127.0.0.1:8000")
    print("   Run: cd backend && python -m uvicorn app.main:app --reload")

except requests.exceptions.Timeout:
    print("\n⏱️  ERROR: Request timed out (took longer than 2 minutes)")
    print("   The AI agents might be processing. Check server logs.")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n" + "="*80)
print("✨ TEST COMPLETE")
print("="*80)
