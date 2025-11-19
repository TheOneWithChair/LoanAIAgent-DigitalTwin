"""
CRUD Operations for Tortoise ORM Models
Provides async functions for creating, reading, updating, and deleting loan applications and related data
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import uuid

from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, IntegrityError

from app.db_models import (
    LoanApplication,
    AgentResult,
    ApplicationAnalytics,
    AuditLog,
    ApplicationStatus,
    AgentStatus,
    RiskLevel
)

logger = logging.getLogger(__name__)


# ==================== LoanApplication CRUD ====================

async def create_loan_application(
    applicant_id: str,
    full_name: str,
    email: str,
    phone_number: str,
    address: str,
    loan_amount_requested: float,
    loan_purpose: str,
    loan_tenure_months: int,
    credit_history_length_months: int,
    number_of_credit_accounts: int,
    credit_utilization_percent: float,
    employment_status: str,
    employment_duration_months: int,
    monthly_income: float,
    recent_credit_inquiries: int = 0,
    income_verified: bool = False,
    credit_mix: Optional[List[str]] = None,
    repayment_history: Optional[List[Dict]] = None,
    **kwargs
) -> LoanApplication:
    """
    Create a new loan application with transaction support
    
    Args:
        applicant_id: Unique identifier for the applicant
        full_name: Full name of the applicant
        email: Email address
        phone_number: Contact phone number
        address: Residential address
        loan_amount_requested: Loan amount requested
        loan_purpose: Purpose of the loan
        loan_tenure_months: Loan tenure in months
        credit_history_length_months: Credit history length
        number_of_credit_accounts: Number of credit accounts
        credit_utilization_percent: Credit utilization percentage
        employment_status: Employment status
        employment_duration_months: How long employed
        monthly_income: Monthly income
        recent_credit_inquiries: Number of recent credit inquiries
        income_verified: Whether income is verified
        credit_mix: List of credit types
        repayment_history: Payment history records
        **kwargs: Additional fields
    
    Returns:
        LoanApplication: Created loan application instance
    
    Raises:
        IntegrityError: If applicant_id already exists or other constraint violation
    """
    try:
        async with in_transaction() as conn:
            application = await LoanApplication.create(
                applicant_id=applicant_id,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                address=address,
                application_status=ApplicationStatus.IN_PROGRESS,
                loan_amount_requested=loan_amount_requested,
                loan_purpose=loan_purpose,
                loan_tenure_months=loan_tenure_months,
                credit_history_length_months=credit_history_length_months,
                number_of_credit_accounts=number_of_credit_accounts,
                credit_utilization_percent=credit_utilization_percent,
                recent_credit_inquiries=recent_credit_inquiries,
                employment_status=employment_status,
                employment_duration_months=employment_duration_months,
                monthly_income=monthly_income,
                income_verified=income_verified,
                credit_mix=credit_mix or [],
                repayment_history=repayment_history or [],
                submitted_at=datetime.utcnow(),
                using_db=conn
            )
            
            # Create audit log
            await AuditLog.create(
                loan_application_id=application.id,
                action="application_created",
                entity_type="LoanApplication",
                entity_id=str(application.id),
                new_value={
                    "applicant_id": applicant_id,
                    "loan_amount_requested": loan_amount_requested,
                    "status": "in_progress"
                },
                performed_by=applicant_id,
                using_db=conn
            )
            
            logger.info(f"Created loan application {application.id} for {full_name}")
            return application
            
    except IntegrityError as e:
        logger.error(f"Failed to create loan application: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating loan application: {e}")
        raise


async def get_loan_application(
    application_id: UUID,
    prefetch_related: bool = True
) -> Optional[LoanApplication]:
    """
    Get a loan application by ID with optional related data
    
    Args:
        application_id: UUID of the application
        prefetch_related: Whether to prefetch agent_results and analytics
    
    Returns:
        LoanApplication or None if not found
    """
    try:
        query = LoanApplication.get(id=application_id)
        
        if prefetch_related:
            query = query.prefetch_related("agent_results", "analytics")
        
        application = await query
        return application
        
    except DoesNotExist:
        logger.warning(f"Loan application {application_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error fetching loan application: {e}")
        raise


async def get_loan_applications_by_applicant(
    applicant_id: str,
    include_related: bool = True
) -> List[LoanApplication]:
    """
    Get all loan applications for a specific applicant
    
    Args:
        applicant_id: Applicant's unique identifier
        include_related: Whether to include agent results and analytics
    
    Returns:
        List of LoanApplication instances
    """
    try:
        query = LoanApplication.filter(applicant_id=applicant_id).order_by("-submitted_at")
        
        if include_related:
            query = query.prefetch_related("agent_results", "analytics")
        
        applications = await query
        return applications
        
    except Exception as e:
        logger.error(f"Error fetching applications for applicant {applicant_id}: {e}")
        raise


async def update_loan_application_status(
    application_id: UUID,
    new_status: ApplicationStatus,
    final_decision: Optional[str] = None,
    approved_amount: Optional[float] = None,
    interest_rate: Optional[float] = None,
    risk_level: Optional[str] = None,
    calculated_credit_score: Optional[int] = None,
    rejection_reasons: Optional[List[str]] = None,
    conditions: Optional[List[str]] = None,
    performed_by: Optional[str] = None
) -> LoanApplication:
    """
    Update loan application status and decision details
    
    Args:
        application_id: UUID of the application
        new_status: New application status
        final_decision: Decision (approved/rejected/conditional)
        approved_amount: Approved loan amount
        interest_rate: Interest rate
        risk_level: Risk assessment level
        calculated_credit_score: Calculated credit score
        rejection_reasons: Reasons for rejection
        conditions: Conditions for approval
        performed_by: Who made the update
    
    Returns:
        Updated LoanApplication instance
    """
    try:
        async with in_transaction() as conn:
            application = await LoanApplication.get(id=application_id, using_db=conn)
            
            # Store old values for audit
            old_values = {
                "status": application.application_status,
                "final_decision": application.final_decision,
                "approved_amount": application.approved_amount
            }
            
            # Update fields
            application.application_status = new_status
            if final_decision:
                application.final_decision = final_decision
            if approved_amount is not None:
                application.approved_amount = approved_amount
            if interest_rate is not None:
                application.interest_rate = interest_rate
            if risk_level:
                application.risk_level = risk_level
            if calculated_credit_score is not None:
                application.credit_score = calculated_credit_score
            if rejection_reasons:
                application.rejection_reasons = rejection_reasons
            if conditions:
                application.conditions = conditions
            
            application.processed_at = datetime.utcnow()
            await application.save(using_db=conn)
            
            # Create audit log
            await AuditLog.create(
                loan_application_id=application.id,
                action="status_updated",
                entity_type="LoanApplication",
                entity_id=str(application.id),
                old_value=old_values,
                new_value={
                    "status": new_status,
                    "final_decision": final_decision,
                    "approved_amount": approved_amount
                },
                performed_by=performed_by or "system",
                using_db=conn
            )
            
            logger.info(f"Updated loan application {application_id} status to {new_status}")
            return application
            
    except DoesNotExist:
        logger.error(f"Loan application {application_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error updating loan application: {e}")
        raise


async def delete_loan_application(application_id: UUID) -> bool:
    """
    Delete a loan application (soft delete by setting status)
    
    Args:
        application_id: UUID of the application
    
    Returns:
        bool: True if deleted successfully
    """
    try:
        application = await LoanApplication.get(id=application_id)
        application.application_status = ApplicationStatus.REJECTED
        application.final_decision = "deleted"
        await application.save()
        
        logger.info(f"Soft-deleted loan application {application_id}")
        return True
        
    except DoesNotExist:
        logger.warning(f"Cannot delete - loan application {application_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error deleting loan application: {e}")
        raise


# ==================== AgentResult CRUD ====================

async def save_agent_result(
    loan_application_id: UUID,
    agent_name: str,
    status: AgentStatus,
    output: Dict[str, Any],
    agent_input: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    execution_time: Optional[float] = None,
    agent_version: Optional[str] = "1.0"
) -> AgentResult:
    """
    Save an agent execution result
    
    Args:
        loan_application_id: UUID of the loan application
        agent_name: Name of the agent (e.g., "credit_scoring")
        status: Execution status (success/failed/pending)
        output: Agent output data
        agent_input: Input data provided to agent
        error_message: Error message if failed
        execution_time: Execution time in seconds
        agent_version: Version of the agent
    
    Returns:
        AgentResult: Created agent result instance
    """
    try:
        result = await AgentResult.create(
            loan_application_id=loan_application_id,
            agent_name=agent_name,
            status=status,
            output=output,
            agent_input=agent_input or {},
            error_message=error_message,
            execution_time=execution_time,
            agent_version=agent_version
        )
        
        logger.info(f"Saved {agent_name} agent result for application {loan_application_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error saving agent result: {e}")
        raise


async def get_agent_results_for_application(
    loan_application_id: UUID,
    agent_name: Optional[str] = None
) -> List[AgentResult]:
    """
    Get all agent results for a loan application
    
    Args:
        loan_application_id: UUID of the loan application
        agent_name: Optional filter by specific agent name
    
    Returns:
        List of AgentResult instances
    """
    try:
        query = AgentResult.filter(loan_application_id=loan_application_id).order_by("timestamp")
        
        if agent_name:
            query = query.filter(agent_name=agent_name)
        
        results = await query
        return results
        
    except Exception as e:
        logger.error(f"Error fetching agent results: {e}")
        raise


async def get_latest_agent_result(
    loan_application_id: UUID,
    agent_name: str
) -> Optional[AgentResult]:
    """
    Get the latest result for a specific agent
    
    Args:
        loan_application_id: UUID of the loan application
        agent_name: Name of the agent
    
    Returns:
        AgentResult or None if not found
    """
    try:
        result = await AgentResult.filter(
            loan_application_id=loan_application_id,
            agent_name=agent_name
        ).order_by("-timestamp").first()
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching latest agent result: {e}")
        raise


# ==================== ApplicationAnalytics CRUD ====================

async def save_analytics(
    loan_application_id: UUID,
    credit_score: int,
    credit_tier: str,
    risk_level: RiskLevel,
    risk_score: float,
    approval_probability: float,
    recommended_amount: float,
    recommended_interest_rate: float,
    dti_ratio: Optional[float] = None,
    front_end_dti: Optional[float] = None,
    back_end_dti: Optional[float] = None,
    credit_score_breakdown: Optional[Dict] = None,
    risk_factors: Optional[Dict] = None,
    decision_factors: Optional[Dict] = None
) -> ApplicationAnalytics:
    """
    Save analytics data for a loan application
    
    Args:
        loan_application_id: UUID of the loan application
        credit_score: Calculated credit score
        credit_tier: Credit tier (excellent/very good/good/fair/poor)
        risk_level: Risk level enum
        risk_score: Risk score (0-100)
        approval_probability: Probability of approval (0-1)
        recommended_amount: Recommended loan amount
        recommended_interest_rate: Recommended interest rate
        dti_ratio: Debt-to-income ratio
        front_end_dti: Front-end DTI
        back_end_dti: Back-end DTI
        credit_score_breakdown: Detailed credit score breakdown
        risk_factors: Risk factors identified
        decision_factors: Factors influencing decision
    
    Returns:
        ApplicationAnalytics: Created analytics instance
    """
    try:
        analytics = await ApplicationAnalytics.create(
            loan_application_id=loan_application_id,
            credit_score=credit_score,
            credit_tier=credit_tier,
            risk_level=risk_level,
            risk_score=risk_score,
            approval_probability=approval_probability,
            recommended_amount=recommended_amount,
            recommended_interest_rate=recommended_interest_rate,
            dti_ratio=dti_ratio,
            front_end_dti=front_end_dti,
            back_end_dti=back_end_dti,
            credit_score_breakdown=credit_score_breakdown or {},
            risk_factors=risk_factors or {},
            decision_factors=decision_factors or {}
        )
        
        logger.info(f"Saved analytics for application {loan_application_id}")
        return analytics
        
    except Exception as e:
        logger.error(f"Error saving analytics: {e}")
        raise


async def get_analytics_for_application(
    loan_application_id: UUID
) -> Optional[ApplicationAnalytics]:
    """
    Get analytics for a loan application
    
    Args:
        loan_application_id: UUID of the loan application
    
    Returns:
        ApplicationAnalytics or None if not found
    """
    try:
        analytics = await ApplicationAnalytics.get_or_none(
            loan_application_id=loan_application_id
        )
        return analytics
        
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise


async def update_analytics(
    loan_application_id: UUID,
    **update_fields
) -> ApplicationAnalytics:
    """
    Update analytics data
    
    Args:
        loan_application_id: UUID of the loan application
        **update_fields: Fields to update
    
    Returns:
        Updated ApplicationAnalytics instance
    """
    try:
        analytics = await ApplicationAnalytics.get(loan_application_id=loan_application_id)
        
        for field, value in update_fields.items():
            if hasattr(analytics, field):
                setattr(analytics, field, value)
        
        analytics.updated_at = datetime.utcnow()
        await analytics.save()
        
        logger.info(f"Updated analytics for application {loan_application_id}")
        return analytics
        
    except DoesNotExist:
        logger.error(f"Analytics not found for application {loan_application_id}")
        raise
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")
        raise


# ==================== Combined Operations ====================

async def save_complete_loan_result(
    application_id: UUID,
    final_decision: str,
    approved_amount: float,
    interest_rate: float,
    credit_score: int,
    credit_tier: str,
    risk_level: RiskLevel,
    risk_score: float,
    approval_probability: float,
    agent_results: List[Dict[str, Any]],
    rejection_reasons: Optional[List[str]] = None,
    conditions: Optional[List[str]] = None,
    credit_score_breakdown: Optional[Dict] = None,
    risk_factors: Optional[Dict] = None,
    decision_factors: Optional[Dict] = None,
    performed_by: Optional[str] = None
) -> LoanApplication:
    """
    Save complete loan processing result including status, analytics, and agent results
    This is a high-level function that updates all related tables in a transaction
    
    Args:
        application_id: UUID of the loan application
        final_decision: Decision (approved/rejected/conditional)
        approved_amount: Approved amount
        interest_rate: Interest rate
        credit_score: Calculated credit score
        credit_tier: Credit tier
        risk_level: Risk level
        risk_score: Risk score
        approval_probability: Approval probability
        agent_results: List of agent result dictionaries
        rejection_reasons: Reasons for rejection
        conditions: Approval conditions
        credit_score_breakdown: Credit score details
        risk_factors: Risk factors
        decision_factors: Decision factors
        performed_by: Who processed the application
    
    Returns:
        Updated LoanApplication instance with all related data
    """
    try:
        async with in_transaction() as conn:
            # Determine application status from decision
            if final_decision.lower() == "approved":
                status = ApplicationStatus.APPROVED
            elif final_decision.lower() == "rejected":
                status = ApplicationStatus.REJECTED
            else:
                status = ApplicationStatus.CONDITIONAL
            
            # Update application
            application = await update_loan_application_status(
                application_id=application_id,
                new_status=status,
                final_decision=final_decision,
                approved_amount=approved_amount,
                interest_rate=interest_rate,
                risk_level=risk_level.value,
                calculated_credit_score=credit_score,
                rejection_reasons=rejection_reasons,
                conditions=conditions,
                performed_by=performed_by
            )
            
            # Save analytics
            await save_analytics(
                loan_application_id=application_id,
                credit_score=credit_score,
                credit_tier=credit_tier,
                risk_level=risk_level,
                risk_score=risk_score,
                approval_probability=approval_probability,
                recommended_amount=approved_amount,
                recommended_interest_rate=interest_rate,
                credit_score_breakdown=credit_score_breakdown,
                risk_factors=risk_factors,
                decision_factors=decision_factors
            )
            
            # Save agent results
            for agent_data in agent_results:
                await save_agent_result(
                    loan_application_id=application_id,
                    agent_name=agent_data.get("agent_name"),
                    status=AgentStatus.SUCCESS,
                    output=agent_data.get("output", {}),
                    agent_input=agent_data.get("input", {}),
                    execution_time=agent_data.get("execution_time"),
                    agent_version=agent_data.get("version", "1.0")
                )
            
            logger.info(f"Saved complete loan result for application {application_id}")
            
            # Fetch and return with all related data
            final_application = await get_loan_application(
                application_id=application_id,
                prefetch_related=True
            )
            
            return final_application
            
    except Exception as e:
        logger.error(f"Error saving complete loan result: {e}")
        raise


async def query_applications_with_filters(
    status: Optional[ApplicationStatus] = None,
    risk_level: Optional[RiskLevel] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    submitted_after: Optional[datetime] = None,
    submitted_before: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[LoanApplication]:
    """
    Query loan applications with various filters
    
    Args:
        status: Filter by application status
        risk_level: Filter by risk level
        min_amount: Minimum requested amount
        max_amount: Maximum requested amount
        submitted_after: Submitted after this date
        submitted_before: Submitted before this date
        limit: Maximum number of results
        offset: Pagination offset
    
    Returns:
        List of LoanApplication instances
    """
    try:
        query = LoanApplication.all()
        
        if status:
            query = query.filter(application_status=status)
        if risk_level:
            query = query.filter(risk_level=risk_level.value)
        if min_amount:
            query = query.filter(loan_amount_requested__gte=min_amount)
        if max_amount:
            query = query.filter(loan_amount_requested__lte=max_amount)
        if submitted_after:
            query = query.filter(submitted_at__gte=submitted_after)
        if submitted_before:
            query = query.filter(submitted_at__lte=submitted_before)
        
        query = query.order_by("-submitted_at").limit(limit).offset(offset)
        query = query.prefetch_related("agent_results", "analytics")
        
        applications = await query
        return applications
        
    except Exception as e:
        logger.error(f"Error querying applications: {e}")
        raise


# Export all CRUD functions
__all__ = [
    # LoanApplication
    "create_loan_application",
    "get_loan_application",
    "get_loan_applications_by_applicant",
    "update_loan_application_status",
    "delete_loan_application",
    # AgentResult
    "save_agent_result",
    "get_agent_results_for_application",
    "get_latest_agent_result",
    # ApplicationAnalytics
    "save_analytics",
    "get_analytics_for_application",
    "update_analytics",
    # Combined operations
    "save_complete_loan_result",
    "query_applications_with_filters",
]
