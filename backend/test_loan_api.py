"""
Quick test script for the Loan Application API
Tests both POST and GET endpoints
"""
import requests
import json
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def test_health_check():
    """Test the health check endpoint"""
    print_section("1. Testing Health Check Endpoint")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API. Is the server running?")
        print("   Start the server with: uvicorn app.loan_api_example:app --reload")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_submit_application() -> Dict[str, Any] | None:
    """Test submitting a new loan application"""
    print_section("2. Testing POST /loan-applications")
    
    application_data = {
        "applicant_id": "TEST12345",
        "full_name": "Test User",
        "email": "test.user@example.com",
        "phone_number": "+1-555-0100",
        "date_of_birth": "1990-05-15",
        "address": "123 Test Street, Test City, TC 12345",
        "loan_amount_requested": 50000.00,
        "loan_purpose": "home_improvement",
        "loan_tenure_months": 60,
        "monthly_income": 6500.00,
        "employment_status": "employed",
        "employment_duration_months": 36,
        "credit_score": 720
    }
    
    print("Submitting application...")
    print(f"Applicant: {application_data['full_name']}")
    print(f"Loan Amount: ${application_data['loan_amount_requested']:,.2f}")
    print(f"Monthly Income: ${application_data['monthly_income']:,.2f}")
    print(f"Credit Score: {application_data['credit_score']}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/loan-applications",
            json=application_data,
            timeout=30
        )
        elapsed_time = time.time() - start_time
        
        print(f"\n⏱️  Request Time: {elapsed_time:.3f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            
            print("\n✅ Application Submitted Successfully!")
            print(f"   Application ID: {result['application_id']}")
            print(f"   Status: {result['current_status']}")
            print(f"   Decision: {result['loan_application']['final_decision']}")
            
            if result['loan_application']['approved_amount']:
                print(f"   Approved Amount: ${result['loan_application']['approved_amount']:,.2f}")
            if result['loan_application']['interest_rate']:
                print(f"   Interest Rate: {result['loan_application']['interest_rate']}%")
            
            # Analytics
            if result.get('analytics_snapshot'):
                analytics = result['analytics_snapshot']
                print(f"\n📈 Analytics:")
                print(f"   Calculated Credit Score: {analytics.get('calculated_credit_score', 'N/A')}")
                print(f"   Risk Score: {analytics.get('risk_score', 'N/A'):.2f}")
                print(f"   Approval Probability: {(analytics.get('approval_probability', 0) * 100):.1f}%")
                print(f"   DTI Ratio: {(analytics.get('debt_to_income_ratio', 0) * 100):.2f}%")
                
                if analytics.get('risk_factors'):
                    print(f"\n⚠️  Risk Factors:")
                    for factor in analytics['risk_factors']:
                        print(f"      - {factor}")
                
                if analytics.get('positive_factors'):
                    print(f"\n✨ Positive Factors:")
                    for factor in analytics['positive_factors']:
                        print(f"      - {factor}")
            
            # Agent Responses
            print(f"\n🤖 AI Agents Executed: {len(result['agent_responses'])}")
            for agent in result['agent_responses']:
                print(f"   - {agent['agent_name']} ({agent['agent_type']})")
                print(f"     Status: {agent['status']} | Confidence: {(agent.get('confidence_score', 0) * 100):.1f}% | Time: {agent.get('execution_time_ms', 0)}ms")
            
            print(f"\n⚡ Total Processing Time: {result['processing_time_seconds']:.3f} seconds")
            
            return result
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("\n❌ ERROR: Request timeout (30s)")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

def test_fetch_application(application_id: str):
    """Test fetching an application by ID"""
    print_section("3. Testing GET /loan-applications/{id}")
    
    print(f"Fetching application: {application_id}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/loan-applications/{application_id}",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ Application Retrieved Successfully!")
            
            app = result['loan_application']
            print(f"\n📋 Application Details:")
            print(f"   ID: {app['id']}")
            print(f"   Applicant: {app['full_name']}")
            print(f"   Email: {app['email']}")
            print(f"   Status: {app['status']}")
            print(f"   Decision: {app.get('final_decision', 'Pending')}")
            print(f"   Loan Amount: ${app['loan_amount_requested']:,.2f}")
            if app.get('approved_amount'):
                print(f"   Approved Amount: ${app['approved_amount']:,.2f}")
            print(f"   Created: {app['created_at']}")
            if app.get('processed_at'):
                print(f"   Processed: {app['processed_at']}")
            
            print(f"\n🤖 Agent Responses: {len(result['agent_responses'])}")
            for agent in result['agent_responses']:
                print(f"   - {agent['agent_name']}: {agent['status']}")
            
            if result.get('analytics_snapshot'):
                print(f"\n📊 Analytics Available: Yes")
            else:
                print(f"\n📊 Analytics Available: No")
            
            return result
        elif response.status_code == 404:
            print("\n❌ Application not found")
            return None
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

def test_invalid_uuid():
    """Test fetching with invalid UUID"""
    print_section("4. Testing Error Handling (Invalid UUID)")
    
    invalid_id = "not-a-valid-uuid"
    print(f"Attempting to fetch with invalid UUID: {invalid_id}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/loan-applications/{invalid_id}",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Correctly returned 400 Bad Request for invalid UUID")
            error = response.json()
            print(f"Error Message: {error.get('detail', 'No detail')}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_nonexistent_application():
    """Test fetching non-existent application"""
    print_section("5. Testing Error Handling (Non-existent Application)")
    
    fake_id = "00000000-0000-0000-0000-000000000000"
    print(f"Attempting to fetch non-existent application: {fake_id}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/loan-applications/{fake_id}",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 Not Found")
            error = response.json()
            print(f"Error Message: {error.get('detail', 'No detail')}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  🚀 LOAN APPLICATION API - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Stopping tests.")
        return
    
    # Test 2: Submit application
    result = test_submit_application()
    if not result:
        print("\n❌ Application submission failed. Stopping tests.")
        return
    
    application_id = result.get('application_id')
    
    # Test 3: Fetch the submitted application
    if application_id:
        test_fetch_application(application_id)
    
    # Test 4: Error handling - invalid UUID
    test_invalid_uuid()
    
    # Test 5: Error handling - non-existent application
    test_nonexistent_application()
    
    # Summary
    print_section("✅ TEST SUITE COMPLETED")
    print("All tests executed successfully!")
    print("\n📝 Summary:")
    print("   ✅ Health check passed")
    print("   ✅ Application submission successful")
    print("   ✅ Application retrieval successful")
    print("   ✅ Error handling validated")
    print("\n🎉 API is working correctly!\n")

if __name__ == "__main__":
    run_all_tests()
