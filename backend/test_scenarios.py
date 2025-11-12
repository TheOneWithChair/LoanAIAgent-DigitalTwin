"""
Comprehensive Test Scenarios for Loan Application System
Tests various credit profiles to validate scoring accuracy
"""
import requests
import json
import time

API_URL = "http://127.0.0.1:8000/submit_loan_application"

# Test Scenarios with Expected Results
test_scenarios = [
    {
        "name": "EXCELLENT CREDIT - Premium Customer",
        "expected_score_range": (750, 850),
        "expected_decision": "approved",
        "expected_interest_range": (8.5, 9.5),
        "data": {
            "applicant_id": "TEST001",
            "full_name": "Amit Sharma",
            "date_of_birth": "1985-05-15",
            "phone_number": "+91-9876543210",
            "email": "amit.sharma@example.in",
            "address": "45 Marine Drive, Mumbai, Maharashtra, 400020",
            "credit_history_length_months": 96,  # 8 years
            "number_of_credit_accounts": 8,
            "credit_mix": {"secured_loans": 3, "unsecured_loans": 5},
            "credit_utilization_percent": 15.0,  # Very low
            "recent_credit_inquiries_6m": 1,
            "repayment_history": {
                "on_time_payments": 95,
                "late_payments": 0,  # Perfect record
                "defaults": 0,
                "write_offs": 0
            },
            "employment_status": "Employed",
            "employment_duration_months": 96,
            "monthly_income": 150000.0,
            "income_verified": True,
            "loan_amount_requested": 2000000.0,  # 20 lakhs
            "loan_purpose": "home",
            "loan_tenure_months": 240,
            "loan_to_value_ratio_percent": 70.0,
            "bank_lender": "HDFC Bank",
            "days_past_due": 0,
            "existing_debts": "",
            "risk_notes": "Prime borrower with excellent history"
        }
    },
    {
        "name": "VERY GOOD CREDIT - Strong Profile",
        "expected_score_range": (700, 749),
        "expected_decision": "approved",
        "expected_interest_range": (9.5, 10.5),
        "data": {
            "applicant_id": "TEST002",
            "full_name": "Priya Desai",
            "date_of_birth": "1988-08-20",
            "phone_number": "+91-9123456780",
            "email": "priya.desai@example.in",
            "address": "23 Koramangala, Bangalore, Karnataka, 560034",
            "credit_history_length_months": 72,  # 6 years
            "number_of_credit_accounts": 6,
            "credit_mix": {"secured_loans": 2, "unsecured_loans": 4},
            "credit_utilization_percent": 25.0,
            "recent_credit_inquiries_6m": 2,
            "repayment_history": {
                "on_time_payments": 70,
                "late_payments": 1,  # One minor late payment
                "defaults": 0,
                "write_offs": 0
            },
            "employment_status": "Employed",
            "employment_duration_months": 72,
            "monthly_income": 100000.0,
            "income_verified": True,
            "loan_amount_requested": 1500000.0,  # 15 lakhs
            "loan_purpose": "car",
            "loan_tenure_months": 60,
            "loan_to_value_ratio_percent": 80.0,
            "bank_lender": "ICICI Bank",
            "days_past_due": 0,
            "existing_debts": "",
            "risk_notes": "Solid borrower with minor late payment"
        }
    },
    {
        "name": "GOOD CREDIT - Moderate Profile",
        "expected_score_range": (650, 699),
        "expected_decision": "approved",
        "expected_interest_range": (11.0, 12.0),
        "data": {
            "applicant_id": "TEST003",
            "full_name": "Rajesh Kumar",
            "date_of_birth": "1990-03-10",
            "phone_number": "+91-9988776655",
            "email": "rajesh.kumar@example.in",
            "address": "78 Sector 18, Noida, UP, 201301",
            "credit_history_length_months": 48,  # 4 years
            "number_of_credit_accounts": 5,
            "credit_mix": {"secured_loans": 1, "unsecured_loans": 4},
            "credit_utilization_percent": 40.0,
            "recent_credit_inquiries_6m": 3,
            "repayment_history": {
                "on_time_payments": 45,
                "late_payments": 2,  # 2 late payments
                "defaults": 0,
                "write_offs": 0
            },
            "employment_status": "Employed",
            "employment_duration_months": 48,
            "monthly_income": 70000.0,
            "income_verified": True,
            "loan_amount_requested": 800000.0,  # 8 lakhs
            "loan_purpose": "education",
            "loan_tenure_months": 84,
            "loan_to_value_ratio_percent": 60.0,
            "bank_lender": "SBI",
            "days_past_due": 0,
            "existing_debts": "",
            "risk_notes": "Average borrower with some late payments"
        }
    },
    {
        "name": "FAIR CREDIT - Conditional Approval Expected",
        "expected_score_range": (600, 649),
        "expected_decision": "conditional",
        "expected_interest_range": (13.0, 14.0),
        "data": {
            "applicant_id": "TEST004",
            "full_name": "Sunita Reddy",
            "date_of_birth": "1992-11-25",
            "phone_number": "+91-9876012345",
            "email": "sunita.reddy@example.in",
            "address": "12 Jubilee Hills, Hyderabad, Telangana, 500033",
            "credit_history_length_months": 36,  # 3 years
            "number_of_credit_accounts": 4,
            "credit_mix": {"secured_loans": 1, "unsecured_loans": 3},
            "credit_utilization_percent": 55.0,  # High utilization
            "recent_credit_inquiries_6m": 4,
            "repayment_history": {
                "on_time_payments": 32,
                "late_payments": 3,  # 3 late payments
                "defaults": 0,
                "write_offs": 0
            },
            "employment_status": "Employed",
            "employment_duration_months": 36,
            "monthly_income": 55000.0,
            "income_verified": True,
            "loan_amount_requested": 500000.0,  # 5 lakhs
            "loan_purpose": "personal",
            "loan_tenure_months": 60,
            "loan_to_value_ratio_percent": 50.0,
            "bank_lender": "Axis Bank",
            "days_past_due": 0,
            "existing_debts": "",
            "risk_notes": "Borderline case with payment issues"
        }
    },
    {
        "name": "POOR CREDIT - Conditional/High Risk",
        "expected_score_range": (550, 599),
        "expected_decision": "conditional",
        "expected_interest_range": (15.5, 16.5),
        "data": {
            "applicant_id": "TEST005",
            "full_name": "Vikram Singh",
            "date_of_birth": "1993-07-08",
            "phone_number": "+91-9123498765",
            "email": "vikram.singh@example.in",
            "address": "56 Civil Lines, Jaipur, Rajasthan, 302006",
            "credit_history_length_months": 30,  # 2.5 years
            "number_of_credit_accounts": 4,
            "credit_mix": {"secured_loans": 0, "unsecured_loans": 4},
            "credit_utilization_percent": 65.0,  # Very high
            "recent_credit_inquiries_6m": 5,
            "repayment_history": {
                "on_time_payments": 25,
                "late_payments": 4,  # Multiple late payments
                "defaults": 0,
                "write_offs": 0
            },
            "employment_status": "Self-employed",
            "employment_duration_months": 24,
            "monthly_income": 45000.0,
            "income_verified": True,
            "loan_amount_requested": 300000.0,  # 3 lakhs
            "loan_purpose": "business",
            "loan_tenure_months": 48,
            "loan_to_value_ratio_percent": 40.0,
            "bank_lender": "IDFC First Bank",
            "days_past_due": 0,
            "existing_debts": "",
            "risk_notes": "High risk with multiple late payments"
        }
    },
    {
        "name": "VERY POOR CREDIT - Rejection Expected",
        "expected_score_range": (300, 549),
        "expected_decision": "rejected",
        "expected_interest_range": (None, None),
        "data": {
            "applicant_id": "TEST006",
            "full_name": "Mohan Verma",
            "date_of_birth": "1995-12-30",
            "phone_number": "+91-9988001122",
            "email": "mohan.verma@example.in",
            "address": "89 Salt Lake, Kolkata, West Bengal, 700091",
            "credit_history_length_months": 24,  # 2 years
            "number_of_credit_accounts": 3,
            "credit_mix": {"secured_loans": 0, "unsecured_loans": 3},
            "credit_utilization_percent": 85.0,  # Critical
            "recent_credit_inquiries_6m": 7,
            "repayment_history": {
                "on_time_payments": 15,
                "late_payments": 8,  # Many late payments
                "defaults": 1,  # Has a default
                "write_offs": 0
            },
            "employment_status": "Employed",
            "employment_duration_months": 18,
            "monthly_income": 35000.0,
            "income_verified": True,
            "loan_amount_requested": 200000.0,  # 2 lakhs
            "loan_purpose": "personal",
            "loan_tenure_months": 36,
            "loan_to_value_ratio_percent": 30.0,
            "bank_lender": "Yes Bank",
            "days_past_due": 15,
            "existing_debts": "",
            "risk_notes": "Very high risk with default history"
        }
    },
    {
        "name": "NEW TO CREDIT - Limited History",
        "expected_score_range": (550, 650),
        "expected_decision": "conditional",
        "expected_interest_range": (13.0, 16.0),
        "data": {
            "applicant_id": "TEST007",
            "full_name": "Kavya Iyer",
            "date_of_birth": "1998-04-18",
            "phone_number": "+91-9876543222",
            "email": "kavya.iyer@example.in",
            "address": "34 Anna Nagar, Chennai, Tamil Nadu, 600040",
            "credit_history_length_months": 18,  # 1.5 years - limited
            "number_of_credit_accounts": 2,
            "credit_mix": {"secured_loans": 0, "unsecured_loans": 2},
            "credit_utilization_percent": 30.0,
            "recent_credit_inquiries_6m": 2,
            "repayment_history": {
                "on_time_payments": 18,
                "late_payments": 0,  # Perfect but limited
                "defaults": 0,
                "write_offs": 0
            },
            "employment_status": "Employed",
            "employment_duration_months": 24,
            "monthly_income": 60000.0,
            "income_verified": True,
            "loan_amount_requested": 400000.0,  # 4 lakhs
            "loan_purpose": "car",
            "loan_tenure_months": 60,
            "loan_to_value_ratio_percent": 85.0,
            "bank_lender": "Kotak Mahindra",
            "days_past_due": 0,
            "existing_debts": "",
            "risk_notes": "Young professional with limited credit history"
        }
    },
    {
        "name": "HIGH INCOME - Recent Late Payments",
        "expected_score_range": (650, 700),
        "expected_decision": "approved",
        "expected_interest_range": (10.0, 12.0),
        "data": {
            "applicant_id": "TEST008",
            "full_name": "Arjun Mehta",
            "date_of_birth": "1987-09-12",
            "phone_number": "+91-9123450987",
            "email": "arjun.mehta@example.in",
            "address": "101 Banjara Hills, Hyderabad, Telangana, 500034",
            "credit_history_length_months": 84,  # 7 years
            "number_of_credit_accounts": 7,
            "credit_mix": {"secured_loans": 3, "unsecured_loans": 4},
            "credit_utilization_percent": 35.0,
            "recent_credit_inquiries_6m": 2,
            "repayment_history": {
                "on_time_payments": 80,
                "late_payments": 2,  # Recent issues
                "defaults": 0,
                "write_offs": 0
            },
            "employment_status": "Employed",
            "employment_duration_months": 84,
            "monthly_income": 200000.0,  # High income
            "income_verified": True,
            "loan_amount_requested": 3000000.0,  # 30 lakhs
            "loan_purpose": "home",
            "loan_tenure_months": 300,
            "loan_to_value_ratio_percent": 75.0,
            "bank_lender": "HDFC Bank",
            "days_past_due": 0,
            "existing_debts": "",
            "risk_notes": "High earner with recent payment issues"
        }
    }
]

def validate_result(scenario, result):
    """Validate if the result matches expectations"""
    issues = []
    
    # Check credit score range
    score = result.get("calculated_credit_score", 0)
    exp_min, exp_max = scenario["expected_score_range"]
    if not (exp_min <= score <= exp_max):
        issues.append(f"Score {score} outside expected range [{exp_min}-{exp_max}]")
    
    # Check decision
    decision = result.get("final_decision", "")
    exp_decision = scenario["expected_decision"]
    if decision != exp_decision:
        issues.append(f"Decision '{decision}' != expected '{exp_decision}'")
    
    # Check interest rate (if approved/conditional)
    if decision in ["approved", "conditional"]:
        interest = result.get("interest_rate")
        exp_min_int, exp_max_int = scenario["expected_interest_range"]
        if interest is not None and exp_min_int is not None:
            if not (exp_min_int <= interest <= exp_max_int):
                issues.append(f"Interest {interest}% outside expected range [{exp_min_int}-{exp_max_int}%]")
    
    return issues

def run_tests():
    """Run all test scenarios"""
    print("=" * 80)
    print("LOAN APPLICATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    results_summary = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_scenarios)}: {scenario['name']}")
        print(f"{'='*80}")
        
        # Show applicant profile
        data = scenario['data']
        print(f"\n📋 APPLICANT PROFILE:")
        print(f"   Name: {data['full_name']}")
        print(f"   Income: ₹{data['monthly_income']:,.0f}/month")
        print(f"   Loan Request: ₹{data['loan_amount_requested']:,.0f} for {data['loan_purpose']}")
        
        repayment = data['repayment_history']
        total_payments = repayment['on_time_payments'] + repayment['late_payments']
        on_time_rate = (repayment['on_time_payments'] / total_payments * 100) if total_payments > 0 else 0
        
        print(f"\n📊 CREDIT PROFILE:")
        print(f"   Credit History: {data['credit_history_length_months']} months")
        print(f"   Payment Record: {repayment['on_time_payments']} on-time, {repayment['late_payments']} late ({on_time_rate:.1f}%)")
        print(f"   Utilization: {data['credit_utilization_percent']}%")
        print(f"   Inquiries (6m): {data['recent_credit_inquiries_6m']}")
        print(f"   Defaults: {repayment['defaults']}, Write-offs: {repayment['write_offs']}")
        
        print(f"\n🎯 EXPECTED RESULTS:")
        print(f"   Score Range: {scenario['expected_score_range'][0]}-{scenario['expected_score_range'][1]}")
        print(f"   Decision: {scenario['expected_decision'].upper()}")
        if scenario['expected_interest_range'][0]:
            print(f"   Interest: {scenario['expected_interest_range'][0]}-{scenario['expected_interest_range'][1]}%")
        
        # Send request
        print(f"\n⏳ Sending request...")
        try:
            response = requests.post(API_URL, json=data, timeout=30)
            
            if response.status_code == 201:
                result = response.json()
                
                print(f"\n✅ ACTUAL RESULTS:")
                print(f"   Status: {response.status_code} SUCCESS")
                print(f"   Application ID: {result.get('application_id')}")
                print(f"   Credit Score: {result.get('calculated_credit_score')} ({get_tier_name(result.get('calculated_credit_score'))})")
                print(f"   Decision: {result.get('final_decision').upper()}")
                print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
                
                if result.get('interest_rate'):
                    print(f"   Interest Rate: {result.get('interest_rate')}%")
                
                approved_amt = result.get('approved_amount', 0)
                if approved_amt > 0:
                    print(f"   Approved Amount: ₹{approved_amt:,.0f}")
                    if approved_amt < data['loan_amount_requested']:
                        reduction = (1 - approved_amt/data['loan_amount_requested']) * 100
                        print(f"   (Reduced by {reduction:.0f}%)")
                
                # Validate results
                issues = validate_result(scenario, result)
                
                if issues:
                    print(f"\n⚠️  VALIDATION ISSUES:")
                    for issue in issues:
                        print(f"   - {issue}")
                    status = "⚠️  PARTIAL"
                else:
                    print(f"\n✅ VALIDATION: All checks passed!")
                    status = "✅ PASS"
                
                results_summary.append({
                    "test": scenario['name'],
                    "status": status,
                    "score": result.get('calculated_credit_score'),
                    "decision": result.get('final_decision'),
                    "issues": len(issues)
                })
                
            else:
                print(f"\n❌ FAILED:")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.text}")
                results_summary.append({
                    "test": scenario['name'],
                    "status": "❌ FAIL",
                    "score": None,
                    "decision": None,
                    "issues": 1
                })
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results_summary.append({
                "test": scenario['name'],
                "status": "❌ ERROR",
                "score": None,
                "decision": None,
                "issues": 1
            })
        
        time.sleep(0.5)  # Small delay between requests
    
    # Print summary
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"{'Test':<45} {'Status':<12} {'Score':<8} {'Decision':<12}")
    print("-" * 80)
    
    for result in results_summary:
        score_str = str(result['score']) if result['score'] else "N/A"
        decision_str = result['decision'] if result['decision'] else "N/A"
        print(f"{result['test']:<45} {result['status']:<12} {score_str:<8} {decision_str:<12}")
    
    # Calculate pass rate
    passed = sum(1 for r in results_summary if "PASS" in r['status'])
    total = len(results_summary)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{'='*80}")
    print(f"OVERALL RESULTS: {passed}/{total} tests passed ({pass_rate:.1f}%)")
    print(f"{'='*80}\n")

def get_tier_name(score):
    """Get credit tier name from score"""
    if score >= 750:
        return "Excellent"
    elif score >= 700:
        return "Very Good"
    elif score >= 650:
        return "Good"
    elif score >= 600:
        return "Fair"
    elif score >= 550:
        return "Poor"
    else:
        return "Very Poor"

if __name__ == "__main__":
    run_tests()
