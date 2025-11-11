from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum


class EmploymentStatus(str, Enum):
    """Employment status enum"""
    EMPLOYED = "Employed"
    SELF_EMPLOYED = "Self-employed"
    UNEMPLOYED = "Unemployed"


class CreditMix(BaseModel):
    """Credit mix details"""
    secured_loans: int = Field(..., ge=0, description="Number of secured loans (home, auto)")
    unsecured_loans: int = Field(..., ge=0, description="Number of unsecured loans (personal, credit cards)")


class RepaymentHistory(BaseModel):
    """Repayment history details"""
    on_time_payments: int = Field(..., ge=0, description="Number of on-time payments")
    late_payments: int = Field(..., ge=0, description="Number of late payments")
    defaults: int = Field(..., ge=0, description="Number of defaults")
    write_offs: int = Field(..., ge=0, description="Number of written-off loans")


class LoanApplicationRequest(BaseModel):
    """Loan application request schema"""
    # Personal Details
    applicant_id: str = Field(..., description="Unique applicant identifier")
    full_name: str = Field(..., min_length=1, description="Full name of applicant")
    date_of_birth: date = Field(..., description="Date of birth")
    phone_number: str = Field(..., description="Contact phone number")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Residential address")
    
    # Credit Profile
    credit_history_length_months: int = Field(..., ge=0, description="Credit history length in months")
    number_of_credit_accounts: int = Field(..., ge=0, description="Total number of credit accounts")
    credit_mix: CreditMix = Field(..., description="Breakdown of secured and unsecured loans")
    credit_utilization_percent: float = Field(..., ge=0, le=100, description="Credit utilization percentage")
    recent_credit_inquiries_6m: int = Field(..., ge=0, description="Number of hard inquiries in last 6 months")
    repayment_history: RepaymentHistory = Field(..., description="Payment history details")
    
    # Employment and Income
    employment_status: EmploymentStatus = Field(..., description="Current employment status")
    employment_duration_months: int = Field(..., ge=0, description="Employment duration in months")
    monthly_income: float = Field(..., ge=0, description="Monthly income")
    income_verified: bool = Field(..., description="Whether income is verified")
    
    # Loan Request Details
    loan_amount_requested: float = Field(..., ge=0, description="Requested loan amount")
    loan_purpose: str = Field(..., description="Purpose of the loan")
    loan_tenure_months: int = Field(..., ge=1, description="Loan tenure in months")
    loan_to_value_ratio_percent: Optional[float] = Field(None, ge=0, le=100, description="LTV ratio for secured loans")
    
    # Optional Additional Parameters
    bank_lender: Optional[str] = Field(None, description="Bank or lender name")
    days_past_due: Optional[int] = Field(None, ge=0, description="Days past due")
    existing_debts: Optional[str] = Field(None, description="Existing debts or obligations")
    risk_notes: Optional[str] = Field(None, description="Risk notes or additional comments")

    @field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v: date) -> date:
        """Validate that applicant is at least 18 years old"""
        from datetime import datetime
        today = datetime.now().date()
        age = (today - v).days / 365.25
        if age < 18:
            raise ValueError('Applicant must be at least 18 years old')
        if age > 100:
            raise ValueError('Invalid date of birth')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "applicant_id": "APP001",
                "full_name": "John Doe",
                "date_of_birth": "1990-01-15",
                "phone_number": "+1-555-0100",
                "email": "john.doe@example.com",
                "address": "123 Main St, New York, NY 10001",
                "credit_history_length_months": 60,
                "number_of_credit_accounts": 5,
                "credit_mix": {
                    "secured_loans": 1,
                    "unsecured_loans": 4
                },
                "credit_utilization_percent": 35.5,
                "recent_credit_inquiries_6m": 2,
                "repayment_history": {
                    "on_time_payments": 48,
                    "late_payments": 2,
                    "defaults": 0,
                    "write_offs": 0
                },
                "employment_status": "Employed",
                "employment_duration_months": 36,
                "monthly_income": 5000.00,
                "income_verified": True,
                "loan_amount_requested": 50000.00,
                "loan_purpose": "home",
                "loan_tenure_months": 60,
                "loan_to_value_ratio_percent": 80.0
            }
        }


class LoanApplicationResponse(BaseModel):
    """Loan application response schema"""
    status: str = Field(..., description="Status of the submission")
    message: str = Field(..., description="Response message")
    application_id: str = Field(..., description="Unique application ID")
    applicant_id: str = Field(..., description="Applicant identifier")
    final_decision: Optional[str] = Field(None, description="Final loan decision")
    calculated_credit_score: Optional[int] = Field(None, description="Calculated credit score")
    risk_level: Optional[str] = Field(None, description="Risk level assessment")
    approved_amount: Optional[float] = Field(None, description="Approved loan amount")
    interest_rate: Optional[float] = Field(None, description="Interest rate offered")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Loan application processed successfully. Decision: approved",
                "application_id": "LA-2025-001",
                "applicant_id": "APP001",
                "final_decision": "approved",
                "calculated_credit_score": 720,
                "risk_level": "low",
                "approved_amount": 50000.00,
                "interest_rate": 5.5
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema"""
    status: str = Field(default="error", description="Status of the response")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Validation error",
                "details": {
                    "field": "email",
                    "error": "Invalid email format"
                }
            }
        }
