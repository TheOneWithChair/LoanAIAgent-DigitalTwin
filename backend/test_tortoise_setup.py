"""
Test Script for Tortoise ORM Setup
Verifies database connection, model creation, and CRUD operations
"""
import asyncio
import logging
from datetime import datetime
from uuid import uuid4

from app.tortoise_config import init_database, close_database, health_check, get_database_stats
from app.tortoise_crud import (
    create_loan_application,
    get_loan_application,
    save_agent_result,
    save_analytics,
    save_complete_loan_result,
    query_applications_with_filters,
    get_loan_applications_by_applicant
)
from app.db_models import ApplicationStatus, AgentStatus, RiskLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Test 1: Database Connection"""
    logger.info("\n========== TEST 1: Database Connection ==========")
    
    try:
        await init_database(generate_schemas=True, safe=True)
        logger.info("✅ Database initialized successfully")
        
        status = await health_check()
        logger.info(f"✅ Health check: {status}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def test_create_loan_application():
    """Test 2: Create Loan Application"""
    logger.info("\n========== TEST 2: Create Loan Application ==========")
    
    try:
        application = await create_loan_application(
            applicant_id=f"TEST_{uuid4().hex[:8]}",
            full_name="John Doe Test",
            email="john.test@example.com",
            phone_number="+1234567890",
            address="123 Test Street, Test City, TS 12345",
            loan_amount_requested=50000.0,
            loan_purpose="home_improvement",
            loan_tenure_months=60,
            credit_history_length_months=36,
            number_of_credit_accounts=5,
            credit_utilization_percent=30.0,
            recent_credit_inquiries=1,
            employment_status="employed",
            employment_duration_months=36,
            monthly_income=6666.67,
            income_verified=True,
            credit_mix=["credit_card", "auto_loan", "mortgage"],
            repayment_history=[
                {"month": "2024-01", "status": "on_time", "amount": 500},
                {"month": "2024-02", "status": "on_time", "amount": 500},
                {"month": "2024-03", "status": "late", "amount": 500}
            ]
        )
        
        logger.info(f"✅ Created loan application: {application.id}")
        logger.info(f"   Applicant: {application.full_name}")
        logger.info(f"   Status: {application.application_status}")
        logger.info(f"   Requested: ${application.loan_amount_requested:,.2f}")
        
        return application
        
    except Exception as e:
        logger.error(f"❌ Failed to create loan application: {e}")
        return None


async def test_save_agent_results(application_id):
    """Test 3: Save Agent Results"""
    logger.info("\n========== TEST 3: Save Agent Results ==========")
    
    try:
        # Save credit scoring agent result
        credit_result = await save_agent_result(
            loan_application_id=application_id,
            agent_name="credit_scoring",
            status=AgentStatus.SUCCESS,
            output={
                "credit_score": 720,
                "credit_tier": "Good",
                "breakdown": {
                    "payment_history": 280,
                    "credit_age": 95,
                    "utilization": 85,
                    "credit_mix": 70,
                    "inquiries": 50
                }
            },
            agent_input={
                "total_payments": 100,
                "late_payments": 2,
                "utilization": 30.0
            },
            execution_time=0.523,
            agent_version="1.0"
        )
        logger.info(f"✅ Saved credit_scoring result: {credit_result.id}")
        
        # Save risk assessment agent result
        risk_result = await save_agent_result(
            loan_application_id=application_id,
            agent_name="risk_assessment",
            status=AgentStatus.SUCCESS,
            output={
                "risk_level": "medium",
                "risk_score": 45.5,
                "approval_probability": 0.85,
                "risk_factors": {
                    "high_utilization": False,
                    "recent_inquiries": False,
                    "short_credit_history": False
                }
            },
            agent_input={
                "credit_score": 720,
                "dti_ratio": 25.5
            },
            execution_time=0.312,
            agent_version="1.0"
        )
        logger.info(f"✅ Saved risk_assessment result: {risk_result.id}")
        
        # Save loan structuring agent result
        loan_result = await save_agent_result(
            loan_application_id=application_id,
            agent_name="loan_structuring",
            status=AgentStatus.SUCCESS,
            output={
                "approved_amount": 45000.0,
                "interest_rate": 7.5,
                "loan_term_months": 60,
                "monthly_payment": 900.0
            },
            agent_input={
                "requested_amount": 50000.0,
                "risk_level": "medium"
            },
            execution_time=0.234,
            agent_version="1.0"
        )
        logger.info(f"✅ Saved loan_structuring result: {loan_result.id}")
        
        # Save loan decision agent result
        decision_result = await save_agent_result(
            loan_application_id=application_id,
            agent_name="loan_decision",
            status=AgentStatus.SUCCESS,
            output={
                "decision": "approved",
                "rationale": "Good credit history with stable income",
                "conditions": ["Proof of income required", "Property appraisal needed"]
            },
            agent_input={
                "credit_score": 720,
                "risk_level": "medium",
                "approved_amount": 45000.0
            },
            execution_time=0.189,
            agent_version="1.0"
        )
        logger.info(f"✅ Saved loan_decision result: {decision_result.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save agent results: {e}")
        return False


async def test_save_analytics(application_id):
    """Test 4: Save Analytics"""
    logger.info("\n========== TEST 4: Save Analytics ==========")
    
    try:
        analytics = await save_analytics(
            loan_application_id=application_id,
            credit_score=720,
            credit_tier="Good",
            risk_level=RiskLevel.MEDIUM,
            risk_score=45.5,
            approval_probability=0.85,
            recommended_amount=45000.0,
            recommended_interest_rate=7.5,
            dti_ratio=25.5,
            front_end_dti=22.0,
            back_end_dti=28.0,
            credit_score_breakdown={
                "payment_history": 280,
                "credit_age": 95,
                "utilization": 85,
                "credit_mix": 70,
                "inquiries": 50
            },
            risk_factors={
                "high_utilization": False,
                "recent_inquiries": False,
                "short_credit_history": False,
                "high_dti": False
            },
            decision_factors={
                "primary": "good_credit_history",
                "secondary": "stable_income",
                "concerns": ["slightly_high_utilization"]
            }
        )
        
        logger.info(f"✅ Saved analytics: {analytics.id}")
        logger.info(f"   Credit Score: {analytics.credit_score}")
        logger.info(f"   Credit Tier: {analytics.credit_tier}")
        logger.info(f"   Risk Level: {analytics.risk_level}")
        logger.info(f"   Approval Probability: {analytics.approval_probability * 100}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save analytics: {e}")
        return False


async def test_get_application_with_relations(application_id):
    """Test 5: Get Application with Related Data"""
    logger.info("\n========== TEST 5: Get Application with Relations ==========")
    
    try:
        application = await get_loan_application(
            application_id=application_id,
            prefetch_related=True
        )
        
        if not application:
            logger.error(f"❌ Application {application_id} not found")
            return False
        
        logger.info(f"✅ Retrieved application: {application.id}")
        logger.info(f"   Applicant: {application.full_name}")
        logger.info(f"   Status: {application.application_status}")
        
        # Check agent results
        logger.info(f"   Agent Results: {len(application.agent_results)}")
        for result in application.agent_results:
            logger.info(f"      - {result.agent_name}: {result.status}")
        
        # Check analytics
        if hasattr(application, 'analytics') and application.analytics:
            logger.info(f"   Analytics:")
            logger.info(f"      - Credit Score: {application.analytics.credit_score}")
            logger.info(f"      - Risk Level: {application.analytics.risk_level}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to get application: {e}")
        return False


async def test_complete_loan_result():
    """Test 6: Save Complete Loan Result (All-in-One)"""
    logger.info("\n========== TEST 6: Save Complete Loan Result ==========")
    
    try:
        # First create a new application
        application = await create_loan_application(
            applicant_id=f"TEST_COMPLETE_{uuid4().hex[:8]}",
            full_name="Jane Smith Test",
            email="jane.test@example.com",
            phone_number="+1987654321",
            address="456 Complete Avenue, Test City, TS 67890",
            loan_amount_requested=75000.0,
            loan_purpose="debt_consolidation",
            loan_tenure_months=84,
            credit_history_length_months=72,
            number_of_credit_accounts=8,
            credit_utilization_percent=15.0,
            recent_credit_inquiries=0,
            employment_status="employed",
            employment_duration_months=60,
            monthly_income=8333.33,
            income_verified=True,
            credit_mix=["credit_card", "auto_loan", "mortgage", "personal_loan"],
            repayment_history=[{"month": f"2024-{i:02d}", "status": "on_time"} for i in range(1, 7)]
        )
        
        logger.info(f"✅ Created application: {application.id}")
        
        # Save complete result in one transaction
        updated_application = await save_complete_loan_result(
            application_id=application.id,
            final_decision="approved",
            approved_amount=70000.0,
            interest_rate=6.5,
            credit_score=780,
            credit_tier="Very Good",
            risk_level=RiskLevel.LOW,
            risk_score=25.0,
            approval_probability=0.95,
            agent_results=[
                {
                    "agent_name": "credit_scoring",
                    "output": {"credit_score": 780, "credit_tier": "Very Good"},
                    "input": {"applicant_id": application.applicant_id},
                    "execution_time": 0.5
                },
                {
                    "agent_name": "risk_assessment",
                    "output": {"risk_level": "low", "risk_score": 25.0},
                    "input": {"credit_score": 780},
                    "execution_time": 0.3
                },
                {
                    "agent_name": "loan_structuring",
                    "output": {"approved_amount": 70000.0, "interest_rate": 6.5},
                    "input": {"requested_amount": 75000.0},
                    "execution_time": 0.4
                },
                {
                    "agent_name": "loan_decision",
                    "output": {"decision": "approved", "rationale": "Excellent credit"},
                    "input": {"risk_level": "low"},
                    "execution_time": 0.2
                }
            ],
            rejection_reasons=None,
            conditions=["Final income verification", "Sign loan agreement"],
            credit_score_breakdown={"payment_history": 300, "credit_age": 120},
            risk_factors={"none": True},
            decision_factors={"primary": "excellent_credit", "secondary": "low_risk"},
            performed_by="test_system"
        )
        
        logger.info(f"✅ Saved complete loan result")
        logger.info(f"   Final Decision: {updated_application.final_decision}")
        logger.info(f"   Approved Amount: ${updated_application.approved_amount:,.2f}")
        logger.info(f"   Interest Rate: {updated_application.interest_rate}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save complete result: {e}")
        return False


async def test_query_applications():
    """Test 7: Query Applications with Filters"""
    logger.info("\n========== TEST 7: Query Applications ==========")
    
    try:
        # Query approved applications
        approved_apps = await query_applications_with_filters(
            status=ApplicationStatus.APPROVED,
            min_amount=10000.0,
            limit=10
        )
        logger.info(f"✅ Found {len(approved_apps)} approved applications")
        
        # Query in-progress applications
        in_progress_apps = await query_applications_with_filters(
            status=ApplicationStatus.IN_PROGRESS,
            limit=10
        )
        logger.info(f"✅ Found {len(in_progress_apps)} in-progress applications")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to query applications: {e}")
        return False


async def test_database_stats():
    """Test 8: Get Database Statistics"""
    logger.info("\n========== TEST 8: Database Statistics ==========")
    
    try:
        stats = await get_database_stats()
        logger.info("✅ Database Statistics:")
        logger.info(f"   Total Applications: {stats.get('total_applications', 0)}")
        logger.info(f"   Approved: {stats.get('approved_applications', 0)}")
        logger.info(f"   Rejected: {stats.get('rejected_applications', 0)}")
        logger.info(f"   In Progress: {stats.get('in_progress_applications', 0)}")
        logger.info(f"   Agent Results: {stats.get('total_agent_results', 0)}")
        logger.info(f"   Analytics Records: {stats.get('total_analytics_records', 0)}")
        logger.info(f"   Audit Logs: {stats.get('total_audit_logs', 0)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to get statistics: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "="*60)
    logger.info("TORTOISE ORM SETUP - COMPREHENSIVE TEST SUITE")
    logger.info("="*60)
    
    results = {}
    
    # Test 1: Database Connection
    results['connection'] = await test_database_connection()
    
    if not results['connection']:
        logger.error("\n❌ DATABASE CONNECTION FAILED - Aborting remaining tests")
        logger.error("Please check your DATABASE_URL environment variable")
        return
    
    # Test 2: Create Application
    application = await test_create_loan_application()
    results['create'] = application is not None
    
    if not application:
        logger.error("\n❌ CREATE APPLICATION FAILED - Aborting remaining tests")
        return
    
    application_id = application.id
    
    # Test 3: Save Agent Results
    results['agent_results'] = await test_save_agent_results(application_id)
    
    # Test 4: Save Analytics
    results['analytics'] = await test_save_analytics(application_id)
    
    # Test 5: Get Application with Relations
    results['get_relations'] = await test_get_application_with_relations(application_id)
    
    # Test 6: Complete Loan Result
    results['complete_result'] = await test_complete_loan_result()
    
    # Test 7: Query Applications
    results['query'] = await test_query_applications()
    
    # Test 8: Database Stats
    results['stats'] = await test_database_stats()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name.upper()}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED! Tortoise ORM setup is working correctly.")
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
    
    # Cleanup
    await close_database()
    logger.info("\n✅ Database connections closed")


if __name__ == "__main__":
    # Set up environment
    import os
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        logger.warning("⚠️  DATABASE_URL not set!")
        logger.warning("Please set DATABASE_URL environment variable:")
        logger.warning("  export DATABASE_URL='postgresql://user:pass@host/db'")
        logger.warning("\nOr create a .env file with:")
        logger.warning("  DATABASE_URL=postgresql://user:pass@host/db")
        exit(1)
    
    # Run tests
    asyncio.run(run_all_tests())
