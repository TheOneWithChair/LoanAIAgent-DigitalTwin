from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import uuid
import time

from app.schemas import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    ErrorResponse
)
from app.tortoise_config import init_database, close_database, health_check
from app.tortoise_crud import create_loan_application, save_agent_result, save_analytics, save_complete_loan_result
from app.db_models import ApplicationStatus, AgentStatus, RiskLevel
from app.orchestrator import process_loan_application
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting up Loan Processing AI Agent API")
    try:
        await init_database(generate_schemas=True, safe=True)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization skipped (not configured): {e}")
        logger.info("API will run in Groq-only mode without database persistence")
    yield
    # Shutdown
    logger.info("Shutting down...")
    try:
        await close_database()
    except:
        pass
    logger.info("Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title="Loan Processing AI Agent API",
    description="API for processing loan applications with AI-powered evaluation using LangGraph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "online",
        "service": "Loan Processing AI Agent API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check_endpoint():
    """Health check endpoint with database status"""
    db_status = await health_check()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status
    }


@app.post(
    "/submit_loan_application",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Loan application submitted successfully",
            "model": LoanApplicationResponse
        },
        400: {
            "description": "Validation error",
            "model": ErrorResponse
        },
        422: {
            "description": "Unprocessable entity",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def submit_loan_application(
    application: LoanApplicationRequest
):
    """
    Submit a loan application for processing.
    
    This endpoint:
    1. Validates application data
    2. Saves to Tortoise ORM database
    3. Executes LangGraph orchestrator with all AI agents
    4. Saves agent results and analytics
    5. Returns aggregated results
    
    Args:
        application: LoanApplicationRequest object containing all application details
        
    Returns:
        LoanApplicationResponse with submission status and application ID
        
    Raises:
        HTTPException: If validation fails or processing error occurs
    """
    start_time = time.time()
    db_application = None
    application_id = None
    
    try:
        # Log the incoming application
        logger.info(f"Received loan application for: {application.full_name}")
        logger.info(f"Applicant ID: {application.applicant_id}")
        logger.info(f"Loan Amount: ₹{application.loan_amount_requested:,.2f}")
        logger.info(f"Loan Purpose: {application.loan_purpose}")
        
        # Validate business rules (pre-processing)
        validate_business_rules(application)
        
        # Create database record with Tortoise ORM
        try:
            db_application = await create_loan_application(
                applicant_id=application.applicant_id,
                full_name=application.full_name,
                email=application.email,
                phone_number=application.phone_number,
                address=application.address,
                loan_amount_requested=float(application.loan_amount_requested),
                loan_purpose=application.loan_purpose,
                loan_tenure_months=application.loan_tenure_months,
                credit_history_length_months=application.credit_history_length_months,
                number_of_credit_accounts=application.number_of_credit_accounts,
                credit_utilization_percent=float(application.credit_utilization_percent),
                recent_credit_inquiries=application.recent_credit_inquiries_6m,
                employment_status=application.employment_status.value,
                employment_duration_months=application.employment_duration_months,
                monthly_income=float(application.monthly_income),
                income_verified=application.income_verified,
                credit_mix=application.credit_mix.model_dump() if hasattr(application.credit_mix, 'model_dump') else application.credit_mix,
                repayment_history=application.repayment_history.model_dump() if hasattr(application.repayment_history, 'model_dump') else application.repayment_history
            )
            
            application_id = str(db_application.id)
            logger.info(f"Application {application_id} saved to database")
            
        except Exception as db_error:
            logger.error(f"Database save failed: {db_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "error",
                    "message": "Failed to save application to database",
                    "details": str(db_error)
                }
            )
        
        # Convert application to dict for orchestrator
        application_data = application.model_dump()
        
        # Execute LangGraph orchestrator with all agents
        logger.info(f"[{application_id}] Starting AI agent orchestration")
        workflow_result = await process_loan_application(
            application_id=application_id,
            applicant_id=application.applicant_id,
            application_data=application_data
        )
        
        # Extract results from workflow
        credit_scoring_result = workflow_result.get("credit_scoring_result")
        loan_decision_result = workflow_result.get("loan_decision_result")
        verification_result = workflow_result.get("verification_result")
        risk_monitoring_result = workflow_result.get("risk_monitoring_result")
        
        # Save agent results to database
        try:
            # Save credit scoring agent result
            if credit_scoring_result:
                await save_agent_result(
                    loan_application_id=db_application.id,
                    agent_name="credit_scoring",
                    status=AgentStatus.SUCCESS if credit_scoring_result.get("status") == "success" else AgentStatus.FAILED,
                    output=credit_scoring_result.get("output", {}),
                    agent_input={"application_data": application_data},
                    execution_time=credit_scoring_result.get("execution_time"),
                    error_message=credit_scoring_result.get("error"),
                    agent_version="1.0"
                )
            
            # Save loan decision agent result
            if loan_decision_result:
                await save_agent_result(
                    loan_application_id=db_application.id,
                    agent_name="loan_decision",
                    status=AgentStatus.SUCCESS if loan_decision_result.get("status") == "success" else AgentStatus.FAILED,
                    output=loan_decision_result.get("output", {}),
                    agent_input={"credit_score": workflow_result.get("calculated_credit_score")},
                    execution_time=loan_decision_result.get("execution_time"),
                    error_message=loan_decision_result.get("error"),
                    agent_version="1.0"
                )
            
            # Save verification agent result
            if verification_result:
                await save_agent_result(
                    loan_application_id=db_application.id,
                    agent_name="verification",
                    status=AgentStatus.SUCCESS if verification_result.get("status") == "success" else AgentStatus.FAILED,
                    output=verification_result.get("output", {}),
                    agent_input={"applicant_id": application.applicant_id},
                    execution_time=verification_result.get("execution_time"),
                    error_message=verification_result.get("error"),
                    agent_version="1.0"
                )
            
            # Save risk monitoring agent result
            if risk_monitoring_result:
                await save_agent_result(
                    loan_application_id=db_application.id,
                    agent_name="risk_monitoring",
                    status=AgentStatus.SUCCESS if risk_monitoring_result.get("status") == "success" else AgentStatus.FAILED,
                    output=risk_monitoring_result.get("output", {}),
                    agent_input={"risk_level": workflow_result.get("risk_level")},
                    execution_time=risk_monitoring_result.get("execution_time"),
                    error_message=risk_monitoring_result.get("error"),
                    agent_version="1.0"
                )
            
            logger.info(f"All agent results saved for application {application_id}")
            
        except Exception as agent_save_error:
            logger.error(f"Failed to save agent results: {agent_save_error}", exc_info=True)
            # Continue processing even if agent result save fails
        
        # Extract aggregated values
        calculated_credit_score = workflow_result.get("calculated_credit_score", 0)
        final_decision = workflow_result.get("final_decision", "under_review")
        risk_level_str = workflow_result.get("risk_level", "medium")
        approved_amount = workflow_result.get("approved_amount", 0.0)
        interest_rate = workflow_result.get("interest_rate")
        
        # Map risk level string to enum
        risk_level_map = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "very_high": RiskLevel.VERY_HIGH
        }
        risk_level_enum = risk_level_map.get(risk_level_str.lower(), RiskLevel.MEDIUM)
        
        # Extract credit tier from credit scoring result
        credit_tier = "Unknown"
        if credit_scoring_result and credit_scoring_result.get("output"):
            credit_tier = credit_scoring_result["output"].get("credit_tier", "Unknown")
        
        # Extract decision rationale and conditions from loan decision result
        decision_rationale = None
        rejection_reasons = None
        conditions = None
        estimated_monthly_emi = None
        
        if loan_decision_result and loan_decision_result.get("output"):
            decision_output = loan_decision_result["output"]
            decision_rationale = decision_output.get("decision_rationale")
            rejection_reasons = decision_output.get("rejection_reasons")
            conditions = decision_output.get("conditions")
            estimated_monthly_emi = decision_output.get("estimated_monthly_emi")
        
        # Save analytics to database
        try:
            await save_analytics(
                loan_application_id=db_application.id,
                credit_score=calculated_credit_score,
                credit_tier=credit_tier,
                risk_level=risk_level_enum,
                risk_score=workflow_result.get("risk_score", 50.0),
                approval_probability=workflow_result.get("approval_probability", 0.5),
                recommended_amount=approved_amount,
                recommended_interest_rate=interest_rate or 0.0,
                dti_ratio=workflow_result.get("dti_ratio"),
                front_end_dti=workflow_result.get("front_end_dti"),
                back_end_dti=workflow_result.get("back_end_dti"),
                credit_score_breakdown=credit_scoring_result.get("output", {}).get("breakdown") if credit_scoring_result else {},
                risk_factors=risk_monitoring_result.get("output", {}).get("risk_factors") if risk_monitoring_result else {},
                decision_factors=loan_decision_result.get("output", {}).get("decision_factors") if loan_decision_result else {}
            )
            
            logger.info(f"Analytics saved for application {application_id}")
            
        except Exception as analytics_error:
            logger.error(f"Failed to save analytics: {analytics_error}", exc_info=True)
            # Continue processing even if analytics save fails
        
        # Update application status in database
        try:
            from app.tortoise_crud import update_loan_application_status
            
            # Determine status
            if final_decision.lower() == "approved":
                app_status = ApplicationStatus.APPROVED
            elif final_decision.lower() == "rejected":
                app_status = ApplicationStatus.REJECTED
            elif final_decision.lower() == "conditional":
                app_status = ApplicationStatus.CONDITIONAL
            else:
                app_status = ApplicationStatus.UNDER_REVIEW
            
            await update_loan_application_status(
                application_id=db_application.id,
                new_status=app_status,
                final_decision=final_decision,
                approved_amount=approved_amount,
                interest_rate=interest_rate,
                risk_level=risk_level_str,
                calculated_credit_score=calculated_credit_score,
                rejection_reasons=rejection_reasons if rejection_reasons else None,
                conditions=conditions if conditions else None,
                performed_by="ai_workflow"
            )
            
            logger.info(f"Application {application_id} status updated to {app_status}")
            
        except Exception as status_update_error:
            logger.error(f"Failed to update application status: {status_update_error}", exc_info=True)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Build agent outputs summary
        agent_outputs = {
            "credit_scoring": credit_scoring_result.get("output") if credit_scoring_result else None,
            "loan_decision": loan_decision_result.get("output") if loan_decision_result else None,
            "verification": verification_result.get("output") if verification_result else None,
            "risk_monitoring": risk_monitoring_result.get("output") if risk_monitoring_result else None
        }
        
        # Determine message based on decision
        if final_decision == "approved":
            message = f"Loan application approved for ₹{approved_amount:,.0f} at {interest_rate}% interest rate"
        elif final_decision == "rejected":
            reasons_text = ", ".join(rejection_reasons) if rejection_reasons else "credit criteria not met"
            message = f"Loan application rejected. Reasons: {reasons_text}"
        elif final_decision == "conditional":
            conditions_text = ", ".join(conditions) if conditions else "additional verification required"
            message = f"Loan application conditionally approved. Conditions: {conditions_text}"
        else:
            message = "Loan application is under review"
        
        logger.info(f"Application {application_id} processed successfully in {processing_time:.2f}s")
        
        return LoanApplicationResponse(
            status="success",
            message=message,
            application_id=application_id,
            applicant_id=application.applicant_id,
            final_decision=final_decision,
            calculated_credit_score=calculated_credit_score,
            credit_tier=credit_tier,
            risk_level=risk_level_str,
            approved_amount=approved_amount,
            interest_rate=interest_rate,
            estimated_monthly_emi=estimated_monthly_emi,
            decision_rationale=decision_rationale,
            rejection_reasons=rejection_reasons,
            conditions=conditions,
            agent_outputs=agent_outputs,
            processing_time_seconds=round(processing_time, 2),
            workflow_status=workflow_result.get("workflow_status", "completed")
        )
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Validation error",
                "details": e.errors()
            }
        )
    except ValueError as e:
        logger.error(f"Business rule violation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": str(e),
                "details": None
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error processing application: {str(e)}", exc_info=True)
        import traceback
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc() if settings.DEBUG else None
        }
        logger.error(f"Error details: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "An unexpected error occurred",
                "details": error_details if settings.DEBUG else None
            }
        )


def validate_business_rules(application: LoanApplicationRequest):
    """
    Validate business rules for loan application.
    
    Args:
        application: LoanApplicationRequest object
        
    Raises:
        ValueError: If any business rule is violated
    """
    # Rule 1: Debt-to-Income ratio check (simplified)
    # Assuming existing debts are included in credit accounts
    if application.monthly_income > 0:
        dti_ratio = (application.loan_amount_requested / application.loan_tenure_months) / application.monthly_income
        if dti_ratio > 0.5:  # Max 50% DTI
            logger.warning(f"High DTI ratio: {dti_ratio:.2%}")
    
    # Rule 2: Income verification requirement for large loans
    if application.loan_amount_requested > 100000 and not application.income_verified:
        raise ValueError("Income verification required for loan amounts exceeding $100,000")
    
    # Rule 3: Employment duration requirement
    if application.employment_status == "Unemployed" and application.loan_amount_requested > 10000:
        raise ValueError("Employment required for loan amounts exceeding $10,000")
    
    # Rule 4: Credit utilization warning
    if application.credit_utilization_percent > 90:
        logger.warning(f"High credit utilization: {application.credit_utilization_percent}%")
    
    # Rule 5: Too many recent inquiries
    if application.recent_credit_inquiries_6m > 6:
        logger.warning(f"High number of recent credit inquiries: {application.recent_credit_inquiries_6m}")
    
    # Rule 6: Defaults check
    if application.repayment_history.defaults > 0:
        logger.warning(f"Applicant has {application.repayment_history.defaults} default(s)")
    
    # Rule 7: Write-offs check
    if application.repayment_history.write_offs > 0:
        logger.warning(f"Applicant has {application.repayment_history.write_offs} write-off(s)")
    
    logger.info("Business rule validation completed")


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "details": exc.errors()
        }
    )


@app.get("/application/{application_id}")
async def get_application(application_id: str):
    """Get loan application details by ID"""
    try:
        from app.tortoise_crud import get_loan_application
        from uuid import UUID
        
        # Convert to UUID
        app_uuid = UUID(application_id)
        
        # Fetch application with all related data
        application = await get_loan_application(
            application_id=app_uuid,
            prefetch_related=True
        )
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {application_id} not found"
            )
        
        # Build response
        return {
            "status": "success",
            "application": {
                "application_id": str(application.id),
                "applicant_id": application.applicant_id,
                "full_name": application.full_name,
                "email": application.email,
                "phone_number": application.phone_number,
                "status": application.application_status,
                "loan_amount_requested": float(application.loan_amount_requested),
                "approved_amount": float(application.approved_amount) if application.approved_amount else None,
                "interest_rate": float(application.interest_rate) if application.interest_rate else None,
                "final_decision": application.final_decision,
                "calculated_credit_score": application.calculated_credit_score,
                "risk_level": application.risk_level,
                "submitted_at": application.submitted_at.isoformat(),
                "processed_at": application.processed_at.isoformat() if application.processed_at else None,
                "agent_results": [
                    {
                        "agent_name": result.agent_name,
                        "status": result.status,
                        "output": result.output,
                        "execution_time": float(result.execution_time) if result.execution_time else None,
                        "timestamp": result.timestamp.isoformat()
                    }
                    for result in application.agent_results
                ] if application.agent_results else [],
                "analytics": {
                    "credit_score": application.analytics.credit_score,
                    "credit_tier": application.analytics.credit_tier,
                    "risk_level": application.analytics.risk_level,
                    "risk_score": float(application.analytics.risk_score),
                    "approval_probability": float(application.analytics.approval_probability),
                    "dti_ratio": float(application.analytics.dti_ratio) if application.analytics.dti_ratio else None,
                    "credit_score_breakdown": application.analytics.credit_score_breakdown,
                    "risk_factors": application.analytics.risk_factors,
                    "decision_factors": application.analytics.decision_factors
                } if hasattr(application, 'analytics') and application.analytics else None
            }
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid application ID format"
        )
    except Exception as e:
        logger.error(f"Error fetching application: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected error occurred",
            "details": str(exc) if app.debug else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
