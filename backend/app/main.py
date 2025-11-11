from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import uuid

from app.schemas import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    ErrorResponse
)
from app.database import init_db, close_db, get_db
from app.orchestrator import process_loan_application
from app.models import LoanApplication, ApplicationStatus, AgentExecutionLog
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
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization skipped (not configured): {e}")
        logger.info("API will run in Groq-only mode without database persistence")
    yield
    # Shutdown
    logger.info("Shutting down...")
    try:
        await close_db()
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
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
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
    application: LoanApplicationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a loan application for processing.
    
    This endpoint:
    1. Validates application data
    2. Executes LangGraph orchestrator with all AI agents
    3. Saves results to Neon DB
    4. Returns aggregated results
    
    Args:
        application: LoanApplicationRequest object containing all application details
        db: Database session (injected)
        
    Returns:
        LoanApplicationResponse with submission status and application ID
        
    Raises:
        HTTPException: If validation fails or processing error occurs
    """
    try:
        # Log the incoming application
        logger.info(f"Received loan application for: {application.full_name}")
        logger.info(f"Applicant ID: {application.applicant_id}")
        logger.info(f"Loan Amount: ${application.loan_amount_requested:,.2f}")
        logger.info(f"Loan Purpose: {application.loan_purpose}")
        
        # Generate unique application ID
        application_id = f"LA-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Validate business rules (pre-processing)
        validate_business_rules(application)
        
        # Convert application to dict for orchestrator
        application_data = application.model_dump()
        
        # Create database record
        db_application = LoanApplication(
            application_id=application_id,
            applicant_id=application.applicant_id,
            full_name=application.full_name,
            date_of_birth=application.date_of_birth,
            phone_number=application.phone_number,
            email=application.email,
            address=application.address,
            credit_history_length_months=application.credit_history_length_months,
            number_of_credit_accounts=application.number_of_credit_accounts,
            credit_mix=application.credit_mix.model_dump(),
            credit_utilization_percent=application.credit_utilization_percent,
            recent_credit_inquiries_6m=application.recent_credit_inquiries_6m,
            repayment_history=application.repayment_history.model_dump(),
            employment_status=application.employment_status.value,
            employment_duration_months=application.employment_duration_months,
            monthly_income=application.monthly_income,
            income_verified=application.income_verified,
            loan_amount_requested=application.loan_amount_requested,
            loan_purpose=application.loan_purpose,
            loan_tenure_months=application.loan_tenure_months,
            loan_to_value_ratio_percent=application.loan_to_value_ratio_percent,
            bank_lender=application.bank_lender,
            days_past_due=application.days_past_due,
            existing_debts=application.existing_debts,
            risk_notes=application.risk_notes,
            status=ApplicationStatus.IN_PROGRESS
        )
        
        db.add(db_application)
        await db.commit()
        await db.refresh(db_application)
        
        logger.info(f"Application {application_id} saved to database")
        
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
        
        # Update database record with agent results
        db_application.credit_scoring_result = credit_scoring_result.get("output") if credit_scoring_result else None
        db_application.loan_decision_result = loan_decision_result.get("output") if loan_decision_result else None
        db_application.verification_result = verification_result.get("output") if verification_result else None
        db_application.risk_monitoring_result = risk_monitoring_result.get("output") if risk_monitoring_result else None
        
        # Update aggregated fields
        db_application.calculated_credit_score = workflow_result.get("calculated_credit_score")
        db_application.final_decision = workflow_result.get("final_decision")
        db_application.risk_level = workflow_result.get("risk_level")
        db_application.approved_amount = workflow_result.get("approved_amount")
        db_application.interest_rate = workflow_result.get("interest_rate")
        
        # Update status
        if workflow_result.get("workflow_status") == "completed":
            if workflow_result.get("final_decision") == "approved":
                db_application.status = ApplicationStatus.APPROVED
            elif workflow_result.get("final_decision") == "rejected":
                db_application.status = ApplicationStatus.REJECTED
            else:
                db_application.status = ApplicationStatus.UNDER_REVIEW
        else:
            db_application.status = ApplicationStatus.UNDER_REVIEW
        
        db_application.processing_time_seconds = workflow_result.get("total_processing_time")
        db_application.processed_at = datetime.now()
        
        # Save agent execution logs
        for agent_name in ["credit_scoring", "loan_decision", "verification", "risk_monitoring"]:
            agent_result = workflow_result.get(f"{agent_name}_result")
            if agent_result:
                log_entry = AgentExecutionLog(
                    application_id=application_id,
                    agent_name=agent_name,
                    agent_input={"application_data": application_data},
                    agent_output=agent_result.get("output"),
                    execution_time_seconds=agent_result.get("execution_time"),
                    status=agent_result.get("status"),
                    error_message=agent_result.get("error")
                )
                db.add(log_entry)
        
        await db.commit()
        await db.refresh(db_application)
        
        logger.info(f"Application {application_id} processed and saved successfully")
        
        # Return success response
        return LoanApplicationResponse(
            status="success",
            message=f"Loan application processed successfully. Decision: {db_application.final_decision}",
            application_id=application_id,
            applicant_id=application.applicant_id,
            final_decision=db_application.final_decision,
            calculated_credit_score=db_application.calculated_credit_score,
            risk_level=db_application.risk_level,
            approved_amount=db_application.approved_amount,
            interest_rate=db_application.interest_rate
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "An unexpected error occurred while processing your application",
                "details": str(e) if settings.DEBUG else None
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
