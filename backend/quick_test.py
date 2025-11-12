"""
Quick test with detailed error output
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/submit_loan_application"

test_data = {
    "applicant_id": "TEST001",
    "full_name": "Jane Smith",
    "date_of_birth": "1985-05-20",
    "phone_number": "+1-555-0123",
    "email": "jane.smith@example.com",
    "address": "456 Oak Ave, Los Angeles, CA 90001",
    "credit_history_length_months": 84,
    "number_of_credit_accounts": 7,
    "credit_mix": {"secured_loans": 2, "unsecured_loans": 5},
    "credit_utilization_percent": 25.0,
    "recent_credit_inquiries_6m": 1,
    "repayment_history": {
        "on_time_payments": 80,
        "late_payments": 1,
        "defaults": 0,
        "write_offs": 0
    },
    "employment_status": "Employed",
    "employment_duration_months": 48,
    "monthly_income": 7500.0,
    "income_verified": True,
    "loan_amount_requested": 75000.0,
    "loan_purpose": "business",
    "loan_tenure_months": 84,
    "loan_to_value_ratio_percent": 70.0,
    "bank_lender": "Metro Bank",
    "days_past_due": 0,
    "existing_debts": "Mortgage: $1200/month, Car loan: $400/month",
    "risk_notes": "Excellent payment history, stable income"
}

print("Sending request...")
try:
    response = requests.post(API_URL, json=test_data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
