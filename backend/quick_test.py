"""
Quick test with detailed error output - Indian data
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/submit_loan_application"

test_data = {
    "applicant_id": "IND002",
    "full_name": "Neha Patel",
    "date_of_birth": "1990-02-10",
    "phone_number": "+91-9123456789",
    "email": "neha.patel@example.in",
    "address": "12 MG Street, Mumbai, Maharashtra, 400001",
    "credit_history_length_months": 60,
    "number_of_credit_accounts": 6,
    "credit_mix": {"secured_loans": 2, "unsecured_loans": 4},
    "credit_utilization_percent": 35.0,
    "recent_credit_inquiries_6m": 3,
    "repayment_history": {
        "on_time_payments": 58,
        "late_payments": 2,
        "defaults": 0,
        "write_offs": 0
    },
    "employment_status": "Self-employed",
    "employment_duration_months": 36,
    "monthly_income": 80000.0,
    "income_verified": True,
    "loan_amount_requested": 850000.0,   # 8.5 lakhs
    "loan_purpose": "business",
    "loan_tenure_months": 72,
    "loan_to_value_ratio_percent": 50.0,
    "bank_lender": "HDFC Bank",
    "days_past_due": 0,
    "existing_debts": "",
    "risk_notes": "Growing business, timely payments"
}

print("Sending request...")
try:
    response = requests.post(API_URL, json=test_data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
