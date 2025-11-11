from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
from datetime import datetime
import uuid

from app.schemas import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    ErrorResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Loan Processing AI Agent API",
    description="API for processing loan applications with AI-powered evaluation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URL
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
async def submit_loan_application(application: LoanApplicationRequest):
    """
    Submit a loan application for processing.
    
    This endpoint accepts loan application data, validates it against the schema,
    and processes the application through the AI agent.
    
    Args:
        application: LoanApplicationRequest object containing all application details
        
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
        
        # TODO: Add your business logic here:
        # 1. Save application to database
        # 2. Perform credit risk assessment using AI agent
        # 3. Calculate risk score
        # 4. Determine approval/rejection
        # 5. Send notifications
        
        # Validate business rules
        validate_business_rules(application)
        
        # Log successful submission
        logger.info(f"Application {application_id} submitted successfully")
        
        # Return success response
        return LoanApplicationResponse(
            status="success",
            message="Loan application submitted successfully and is being processed",
            application_id=application_id,
            applicant_id=application.applicant_id
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
        logger.error(f"Unexpected error processing application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "An unexpected error occurred while processing your application",
                "details": str(e) if app.debug else None
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
