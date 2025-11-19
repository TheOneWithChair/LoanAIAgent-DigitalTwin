"""
Test Database Integration
Verify that application data is saved correctly to Tortoise ORM database
"""
import asyncio
import logging
from uuid import UUID

from app.tortoise_config import init_database, close_database
from app.tortoise_crud import (
    get_loan_application,
    get_loan_applications_by_applicant,
    query_applications_with_filters
)
from app.db_models import ApplicationStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_integration():
    """Test database integration after submitting an application"""
    
    try:
        # Initialize database
        await init_database(generate_schemas=True, safe=True)
        logger.info("✅ Database initialized")
        
        # Get all applications
        all_apps = await query_applications_with_filters(limit=10)
        logger.info(f"\n📊 Total applications in database: {len(all_apps)}")
        
        if len(all_apps) == 0:
            logger.warning("⚠️  No applications found. Please submit an application through the API first.")
            logger.info("Run: python test_comprehensive_response.py")
            return
        
        # Show latest application
        latest_app = all_apps[0]
        logger.info(f"\n📋 Latest Application:")
        logger.info(f"   ID: {latest_app.id}")
        logger.info(f"   Applicant: {latest_app.full_name}")
        logger.info(f"   Email: {latest_app.email}")
        logger.info(f"   Status: {latest_app.application_status}")
        logger.info(f"   Loan Amount: ₹{latest_app.loan_amount_requested:,.2f}")
        logger.info(f"   Submitted: {latest_app.submitted_at}")
        
        # Fetch with related data
        logger.info(f"\n🔍 Fetching application with related data...")
        app_with_relations = await get_loan_application(
            application_id=latest_app.id,
            prefetch_related=True
        )
        
        if app_with_relations:
            # Check agent results
            logger.info(f"\n🤖 Agent Results: {len(app_with_relations.agent_results)}")
            for result in app_with_relations.agent_results:
                logger.info(f"   ✓ {result.agent_name}: {result.status}")
                logger.info(f"      Execution time: {result.execution_time}s")
                if result.output:
                    logger.info(f"      Output keys: {list(result.output.keys())}")
            
            # Check analytics
            if hasattr(app_with_relations, 'analytics') and app_with_relations.analytics:
                logger.info(f"\n📈 Analytics:")
                logger.info(f"   Credit Score: {app_with_relations.analytics.credit_score}")
                logger.info(f"   Credit Tier: {app_with_relations.analytics.credit_tier}")
                logger.info(f"   Risk Level: {app_with_relations.analytics.risk_level}")
                logger.info(f"   Risk Score: {app_with_relations.analytics.risk_score}")
                logger.info(f"   Approval Probability: {app_with_relations.analytics.approval_probability * 100:.1f}%")
            else:
                logger.warning("   ⚠️  No analytics found")
            
            # Check decision results
            logger.info(f"\n✅ Decision Results:")
            logger.info(f"   Final Decision: {app_with_relations.final_decision}")
            logger.info(f"   Approved Amount: ₹{app_with_relations.approved_amount:,.2f}" if app_with_relations.approved_amount else "   Approved Amount: N/A")
            logger.info(f"   Interest Rate: {app_with_relations.interest_rate}%" if app_with_relations.interest_rate else "   Interest Rate: N/A")
            logger.info(f"   Risk Level: {app_with_relations.risk_level}")
            
            # Verify data completeness
            logger.info(f"\n✔️  Data Completeness Check:")
            checks = {
                "Application saved": True,
                "Agent results saved": len(app_with_relations.agent_results) > 0,
                "Analytics saved": hasattr(app_with_relations, 'analytics') and app_with_relations.analytics is not None,
                "Decision recorded": app_with_relations.final_decision is not None,
                "Status updated": app_with_relations.application_status != ApplicationStatus.IN_PROGRESS
            }
            
            for check, passed in checks.items():
                status_icon = "✅" if passed else "❌"
                logger.info(f"   {status_icon} {check}")
            
            # Summary
            passed_checks = sum(1 for v in checks.values() if v)
            total_checks = len(checks)
            
            logger.info(f"\n📊 Integration Status: {passed_checks}/{total_checks} checks passed")
            
            if passed_checks == total_checks:
                logger.info("🎉 All data is being saved correctly!")
            else:
                logger.warning("⚠️  Some data may not be saved. Check the logs above.")
        
        # Close database
        await close_database()
        logger.info("\n✅ Database closed")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        await close_database()


if __name__ == "__main__":
    asyncio.run(test_database_integration())
