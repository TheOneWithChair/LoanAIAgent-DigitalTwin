"""
Example: Integrating Tortoise ORM with FastAPI Loan Application
Shows how to use the Tortoise CRUD operations in the main.py endpoints
"""
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from typing import Dict, Any
import time
import logging
from uuid import UUID

from app.schemas import LoanApplicationRequest, LoanApplicationResponse
from app.tortoise_config import lifespan_handler, health_check
from app.tortoise_crud import (
    create_loan_application,
    get_loan_application,
    save_complete_loan_result,
    get_loan_applications_by_applicant,
    query_applications_with_filters
)
from app.db_models import ApplicationStatus, RiskLevel, AgentStatus

# Import your existing workflow
from app.workflow import run_loan_application_workflow

logger = logging.getLogger(__name__)


# Create FastAPI app with Tortoise lifespan handler
app = FastAPI(
    title="Loan Processing API with Tortoise ORM",
    version="2.0",
    lifespan=lifespan_handler  # This handles database init/cleanup
)


@app.get("/health")
async def health_check_endpoint():
    """Health check endpoint including database status"""
    db_status = await health_check()
    return {
        "status": "healthy",
        "database": db_status
    }


@app.post("/loan/apply", response_model=LoanApplicationResponse)
async def apply_for_loan_with_database(request: LoanApplicationRequest):
    """
    Process loan application and save to database
    
    This example shows how to:
    1. Create loan application in database
    2. Run the AI agent workflow
    3. Save complete results (analytics, agent outputs)
    4. Return comprehensive response
    """
    start_time = time.time()
    
    try:
        # Step 1: Create loan application in database
        logger.info(f"Creating loan application for {request.applicant_id}")
        
        application = await create_loan_application(
            applicant_id=request.applicant_id,
            full_name=request.full_name,
            email=request.email,
            phone_number=request.phone_number,
            address=request.address,
            requested_amount=request.requested_amount,
            loan_purpose=request.loan_purpose,
            annual_income=request.annual_income,
            credit_score=request.credit_score,
            employment_status=request.employment_status,
            employment_duration_months=request.employment_duration_months,
            existing_debts=request.existing_debts,
            monthly_debt_payments=request.monthly_debt_payments,
            total_payments=request.total_payments,
            late_payments=request.late_payments,
            utilization=request.utilization,
            credit_inquiries=request.credit_inquiries,
            credit_mix=request.credit_mix,
            repayment_history=request.repayment_history
        )
        
        application_id = application.id
        logger.info(f"Created application with ID: {application_id}")
        
        # Step 2: Prepare input for workflow
        workflow_input = {
            "applicant_id": request.applicant_id,
            "full_name": request.full_name,
            "email": request.email,
            "phone_number": request.phone_number,
            "address": request.address,
            "requested_amount": request.requested_amount,
            "loan_purpose": request.loan_purpose,
            "annual_income": request.annual_income,
            "credit_score": request.credit_score,
            "employment_status": request.employment_status,
            "employment_duration_months": request.employment_duration_months,
            "existing_debts": request.existing_debts,
            "monthly_debt_payments": request.monthly_debt_payments,
            "total_payments": request.total_payments,
            "late_payments": request.late_payments,
            "utilization": request.utilization,
            "credit_inquiries": request.credit_inquiries,
            "credit_mix": request.credit_mix,
            "repayment_history": request.repayment_history,
        }
        
        # Step 3: Run AI agent workflow
        logger.info("Running AI agent workflow...")
        result = await run_loan_application_workflow(workflow_input)
        
        # Step 4: Extract results from workflow
        credit_data = result.get("credit_scoring", {})
        risk_data = result.get("risk_assessment", {})
        loan_data = result.get("loan_structuring", {})
        decision_data = result.get("loan_decision", {})
        
        # Extract values with defaults
        calculated_credit_score = credit_data.get("credit_score", 0)
        credit_tier = credit_data.get("credit_tier", "Unknown")
        risk_level_str = risk_data.get("risk_level", "medium")
        risk_score = risk_data.get("risk_score", 50.0)
        approval_probability = risk_data.get("approval_probability", 0.5)
        
        # Map risk level string to enum
        risk_level_map = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "very_high": RiskLevel.VERY_HIGH
        }
        risk_level = risk_level_map.get(risk_level_str.lower(), RiskLevel.MEDIUM)
        
        final_decision = decision_data.get("decision", "pending")
        approved_amount = loan_data.get("approved_amount", request.requested_amount)
        interest_rate = loan_data.get("interest_rate", 0.0)
        rejection_reasons = decision_data.get("rejection_reasons", [])
        conditions = decision_data.get("conditions", [])
        
        # Prepare agent results for saving
        agent_results = [
            {
                "agent_name": "credit_scoring",
                "output": credit_data,
                "input": {"applicant_id": request.applicant_id},
                "execution_time": 0.5
            },
            {
                "agent_name": "risk_assessment",
                "output": risk_data,
                "input": {"credit_score": calculated_credit_score},
                "execution_time": 0.3
            },
            {
                "agent_name": "loan_structuring",
                "output": loan_data,
                "input": {"requested_amount": request.requested_amount},
                "execution_time": 0.4
            },
            {
                "agent_name": "loan_decision",
                "output": decision_data,
                "input": {"risk_level": risk_level_str},
                "execution_time": 0.2
            }
        ]
        
        # Step 5: Save complete results to database
        logger.info("Saving complete results to database...")
        
        updated_application = await save_complete_loan_result(
            application_id=application_id,
            final_decision=final_decision,
            approved_amount=approved_amount,
            interest_rate=interest_rate,
            credit_score=calculated_credit_score,
            credit_tier=credit_tier,
            risk_level=risk_level,
            risk_score=risk_score,
            approval_probability=approval_probability,
            agent_results=agent_results,
            rejection_reasons=rejection_reasons if rejection_reasons else None,
            conditions=conditions if conditions else None,
            credit_score_breakdown=credit_data.get("breakdown", {}),
            risk_factors=risk_data.get("factors", {}),
            decision_factors=decision_data.get("decision_factors", {}),
            performed_by="ai_workflow"
        )
        
        processing_time = time.time() - start_time
        
        # Step 6: Build comprehensive response
        # Generate context-appropriate message
        if final_decision.lower() == "approved":
            message = f"Congratulations! Your loan application has been approved for ${approved_amount:,.2f} at {interest_rate}% interest rate."
        elif final_decision.lower() == "rejected":
            reasons_text = ", ".join(rejection_reasons) if rejection_reasons else "credit criteria not met"
            message = f"We regret to inform you that your loan application has been rejected. Reasons: {reasons_text}"
        else:
            conditions_text = ", ".join(conditions) if conditions else "additional verification"
            message = f"Your loan application requires additional review. Conditions: {conditions_text}"
        
        # Calculate estimated monthly EMI
        if approved_amount > 0 and interest_rate > 0:
            loan_term_months = 60  # Default 5 years
            monthly_rate = (interest_rate / 100) / 12
            estimated_monthly_emi = (
                approved_amount * monthly_rate * ((1 + monthly_rate) ** loan_term_months)
            ) / (((1 + monthly_rate) ** loan_term_months) - 1)
        else:
            estimated_monthly_emi = 0.0
        
        # Build agent outputs dictionary
        agent_outputs = {
            "credit_scoring": credit_data,
            "risk_assessment": risk_data,
            "loan_structuring": loan_data,
            "loan_decision": decision_data
        }
        
        # Build decision rationale
        decision_rationale = decision_data.get(
            "rationale",
            f"Based on credit score of {calculated_credit_score}, risk level {risk_level_str}, and DTI analysis."
        )
        
        # Step 7: Return comprehensive response
        return LoanApplicationResponse(
            status="success",
            message=message,
            application_id=str(application_id),
            applicant_id=request.applicant_id,
            final_decision=final_decision,
            calculated_credit_score=calculated_credit_score,
            credit_tier=credit_tier,
            risk_level=risk_level_str,
            approved_amount=approved_amount,
            interest_rate=interest_rate,
            estimated_monthly_emi=round(estimated_monthly_emi, 2),
            decision_rationale=decision_rationale,
            rejection_reasons=rejection_reasons if rejection_reasons else None,
            conditions=conditions if conditions else None,
            agent_outputs=agent_outputs,
            processing_time_seconds=round(processing_time, 2),
            workflow_status="completed"
        )
        
    except Exception as e:
        logger.error(f"Error processing loan application: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process loan application: {str(e)}"
        )


@app.get("/loan/application/{application_id}")
async def get_application_details(application_id: str):
    """
    Get loan application details with all related data
    
    Example:
        GET /loan/application/550e8400-e29b-41d4-a716-446655440000
    """
    try:
        # Convert string to UUID
        app_uuid = UUID(application_id)
        
        # Fetch with all related data
        application = await get_loan_application(
            application_id=app_uuid,
            prefetch_related=True
        )
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found"
            )
        
        # Build response with all data
        response = {
            "application_id": str(application.id),
            "applicant_id": application.applicant_id,
            "full_name": application.full_name,
            "email": application.email,
            "status": application.application_status,
            "requested_amount": application.requested_amount,
            "approved_amount": application.approved_amount,
            "interest_rate": application.interest_rate,
            "final_decision": application.final_decision,
            "credit_score": application.credit_score,
            "risk_level": application.risk_level,
            "submitted_at": application.submitted_at.isoformat(),
            "processed_at": application.processed_at.isoformat() if application.processed_at else None,
            "agent_results": [
                {
                    "agent_name": result.agent_name,
                    "status": result.status,
                    "output": result.output,
                    "execution_time": result.execution_time
                }
                for result in application.agent_results
            ] if application.agent_results else [],
            "analytics": {
                "credit_score": application.analytics.credit_score,
                "credit_tier": application.analytics.credit_tier,
                "risk_level": application.analytics.risk_level,
                "risk_score": application.analytics.risk_score,
                "approval_probability": application.analytics.approval_probability,
                "dti_ratio": application.analytics.dti_ratio
            } if hasattr(application, 'analytics') and application.analytics else None
        }
        
        return response
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid application ID format"
        )
    except Exception as e:
        logger.error(f"Error fetching application details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/loan/applicant/{applicant_id}/applications")
async def get_applicant_applications(applicant_id: str):
    """
    Get all applications for a specific applicant
    
    Example:
        GET /loan/applicant/APP123456/applications
    """
    try:
        applications = await get_loan_applications_by_applicant(
            applicant_id=applicant_id,
            include_related=True
        )
        
        return {
            "applicant_id": applicant_id,
            "total_applications": len(applications),
            "applications": [
                {
                    "application_id": str(app.id),
                    "status": app.application_status,
                    "requested_amount": app.requested_amount,
                    "final_decision": app.final_decision,
                    "submitted_at": app.submitted_at.isoformat()
                }
                for app in applications
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching applicant applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/loan/applications/search")
async def search_applications(
    status: str = None,
    risk_level: str = None,
    min_amount: float = None,
    max_amount: float = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Search loan applications with filters
    
    Example:
        GET /loan/applications/search?status=approved&min_amount=10000&limit=50
    """
    try:
        # Map string parameters to enums
        status_enum = ApplicationStatus(status) if status else None
        risk_level_enum = RiskLevel(risk_level) if risk_level else None
        
        applications = await query_applications_with_filters(
            status=status_enum,
            risk_level=risk_level_enum,
            min_amount=min_amount,
            max_amount=max_amount,
            limit=limit,
            offset=offset
        )
        
        return {
            "total": len(applications),
            "limit": limit,
            "offset": offset,
            "applications": [
                {
                    "application_id": str(app.id),
                    "applicant_id": app.applicant_id,
                    "full_name": app.full_name,
                    "status": app.application_status,
                    "requested_amount": app.requested_amount,
                    "approved_amount": app.approved_amount,
                    "risk_level": app.risk_level,
                    "submitted_at": app.submitted_at.isoformat()
                }
                for app in applications
            ]
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter value: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error searching applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Additional utility endpoints

@app.get("/loan/stats")
async def get_loan_statistics():
    """Get loan application statistics"""
    from app.tortoise_config import get_database_stats
    
    try:
        stats = await get_database_stats()
        return {
            "status": "success",
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
