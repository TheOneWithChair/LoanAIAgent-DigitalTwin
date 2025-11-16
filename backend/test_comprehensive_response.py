"""
Test script to demonstrate comprehensive response fields
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/submit_loan_application"

# Test with a good credit profile
test_data = {
    "applicant_id": "TEST_COMP_001",
    "full_name": "Aisha Khan",
    "date_of_birth": "1988-06-15",
    "phone_number": "+91-9876543210",
    "email": "aisha.khan@example.in",
    "address": "45 Bandra West, Mumbai, Maharashtra, 400050",
    "credit_history_length_months": 72,  # 6 years
    "number_of_credit_accounts": 6,
    "credit_mix": {"secured_loans": 2, "unsecured_loans": 4},
    "credit_utilization_percent": 28.0,
    "recent_credit_inquiries_6m": 2,
    "repayment_history": {
        "on_time_payments": 70,
        "late_payments": 1,
        "defaults": 0,
        "write_offs": 0
    },
    "employment_status": "Employed",
    "employment_duration_months": 72,
    "monthly_income": 95000.0,
    "income_verified": True,
    "loan_amount_requested": 1200000.0,  # 12 lakhs
    "loan_purpose": "home",
    "loan_tenure_months": 180,
    "loan_to_value_ratio_percent": 75.0,
    "bank_lender": "HDFC Bank",
    "days_past_due": 0,
    "existing_debts": "",
    "risk_notes": "Stable employment, good credit history"
}

print("=" * 100)
print("COMPREHENSIVE RESPONSE TEST")
print("=" * 100)
print()

print("📝 SENDING APPLICATION...")
print(f"Applicant: {test_data['full_name']}")
print(f"Loan Amount: ₹{test_data['loan_amount_requested']:,.0f}")
print(f"Credit History: {test_data['credit_history_length_months']} months")
print(f"Payment Record: {test_data['repayment_history']['on_time_payments']} on-time, {test_data['repayment_history']['late_payments']} late")
print()

try:
    response = requests.post(API_URL, json=test_data, timeout=30)
    
    if response.status_code == 201:
        result = response.json()
        
        print("✅ APPLICATION PROCESSED SUCCESSFULLY")
        print("=" * 100)
        
        # Standard Response Fields
        print("\n📋 STANDARD RESPONSE FIELDS:")
        print(f"  Status: {result.get('status')}")
        print(f"  Message: {result.get('message')}")
        print(f"  Application ID: {result.get('application_id')}")
        print(f"  Applicant ID: {result.get('applicant_id')}")
        
        # Decision Fields
        print("\n🎯 DECISION DETAILS:")
        print(f"  Final Decision: {result.get('final_decision', 'N/A').upper()}")
        print(f"  Credit Score: {result.get('calculated_credit_score', 'N/A')} ({result.get('credit_tier', 'N/A')})")
        print(f"  Risk Level: {result.get('risk_level', 'N/A').upper()}")
        
        # Financial Terms
        print("\n💰 FINANCIAL TERMS:")
        print(f"  Approved Amount: ₹{result.get('approved_amount', 0):,.2f}")
        if result.get('interest_rate'):
            print(f"  Interest Rate: {result.get('interest_rate')}%")
        if result.get('estimated_monthly_emi'):
            print(f"  Estimated Monthly EMI: ₹{result.get('estimated_monthly_emi'):,.2f}")
        
        # Decision Explanation
        print("\n📖 DECISION EXPLANATION:")
        if result.get('decision_rationale'):
            print(f"  Rationale: {result.get('decision_rationale')}")
        
        if result.get('rejection_reasons'):
            print(f"  Rejection Reasons:")
            for reason in result.get('rejection_reasons', []):
                print(f"    - {reason}")
        
        if result.get('conditions'):
            print(f"  Conditions:")
            for condition in result.get('conditions', []):
                print(f"    - {condition}")
        
        # Agent Outputs
        print("\n🤖 AGENT OUTPUTS:")
        agent_outputs = result.get('agent_outputs', {})
        
        if agent_outputs.get('credit_scoring'):
            print("  Credit Scoring Agent:")
            cs = agent_outputs['credit_scoring']
            print(f"    - Score: {cs.get('calculated_credit_score')} ({cs.get('credit_tier')})")
            if cs.get('credit_score_breakdown'):
                breakdown = cs['credit_score_breakdown']
                print(f"    - Breakdown: Base={breakdown.get('base_score')}, "
                      f"History=+{breakdown.get('credit_history_score')}, "
                      f"Payment=+{breakdown.get('payment_history_score')}, "
                      f"Util={breakdown.get('credit_utilization_score'):+d}, "
                      f"Inq=-{breakdown.get('inquiry_penalty')}, "
                      f"Def=-{breakdown.get('default_penalty')}")
        
        if agent_outputs.get('loan_decision'):
            print("  Loan Decision Agent:")
            ld = agent_outputs['loan_decision']
            print(f"    - Decision: {ld.get('final_decision', 'N/A')}")
            print(f"    - Interest Rate: {ld.get('interest_rate', 'N/A')}%")
            if ld.get('debt_to_income_ratio'):
                print(f"    - DTI Ratio: {ld.get('debt_to_income_ratio'):.1%}")
        
        if agent_outputs.get('verification'):
            print("  Verification Agent:")
            ver = agent_outputs['verification']
            print(f"    - Status: {ver.get('verification_status', 'N/A')}")
            if ver.get('verified_fields'):
                print(f"    - Verified: {', '.join(ver.get('verified_fields', []))}")
        
        if agent_outputs.get('risk_monitoring'):
            print("  Risk Monitoring Agent:")
            rm = agent_outputs['risk_monitoring']
            print(f"    - Risk Level: {rm.get('risk_level', 'N/A')}")
            if rm.get('risk_score') is not None:
                print(f"    - Risk Score: {rm.get('risk_score')}/100")
        
        # Processing Metadata
        print("\n⏱️  PROCESSING METADATA:")
        print(f"  Processing Time: {result.get('processing_time_seconds', 0):.2f} seconds")
        print(f"  Workflow Status: {result.get('workflow_status', 'N/A')}")
        
        # Full JSON Response
        print("\n" + "=" * 100)
        print("📄 FULL JSON RESPONSE:")
        print("=" * 100)
        print(json.dumps(result, indent=2))
        
    else:
        print(f"❌ ERROR: Status {response.status_code}")
        print(json.dumps(response.json(), indent=2))

except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 100)
print("All standard fields are now included in the response!")
print("=" * 100)
