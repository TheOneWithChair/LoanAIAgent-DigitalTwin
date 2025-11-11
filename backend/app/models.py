# SQLAlchemy Models for Loan Processing System

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database import Base


class ApplicationStatus(str, enum.Enum):
    """Application status enum"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    CANCELLED = "cancelled"


class LoanApplication(Base):
    """Main loan application model"""
    __tablename__ = "loan_applications"
    
    # Primary identifiers
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(String(50), unique=True, index=True, nullable=False)
    applicant_id = Column(String(50), index=True, nullable=False)
    
    # Personal Details
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    
    # Credit Profile
    credit_history_length_months = Column(Integer, nullable=False)
    number_of_credit_accounts = Column(Integer, nullable=False)
    credit_mix = Column(JSON, nullable=False)  # {"secured_loans": 1, "unsecured_loans": 4}
    credit_utilization_percent = Column(Float, nullable=False)
    recent_credit_inquiries_6m = Column(Integer, nullable=False)
    repayment_history = Column(JSON, nullable=False)  # {"on_time_payments": 48, "late_payments": 2, ...}
    
    # Employment and Income
    employment_status = Column(String(50), nullable=False)
    employment_duration_months = Column(Integer, nullable=False)
    monthly_income = Column(Float, nullable=False)
    income_verified = Column(Boolean, nullable=False)
    
    # Loan Request Details
    loan_amount_requested = Column(Float, nullable=False)
    loan_purpose = Column(String(100), nullable=False)
    loan_tenure_months = Column(Integer, nullable=False)
    loan_to_value_ratio_percent = Column(Float, nullable=True)
    
    # Additional Parameters
    bank_lender = Column(String(255), nullable=True)
    days_past_due = Column(Integer, nullable=True)
    existing_debts = Column(Text, nullable=True)
    risk_notes = Column(Text, nullable=True)
    
    # Application Status
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    
    # Agent Results (stored as JSON)
    credit_scoring_result = Column(JSON, nullable=True)
    loan_decision_result = Column(JSON, nullable=True)
    verification_result = Column(JSON, nullable=True)
    risk_monitoring_result = Column(JSON, nullable=True)
    
    # Aggregated Results
    final_decision = Column(String(50), nullable=True)  # "approved", "rejected", "under_review"
    calculated_credit_score = Column(Integer, nullable=True)
    risk_level = Column(String(50), nullable=True)  # "low", "medium", "high"
    approved_amount = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processing metadata
    processing_time_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<LoanApplication(application_id={self.application_id}, applicant={self.full_name}, status={self.status})>"


class AgentExecutionLog(Base):
    """Log of individual agent executions"""
    __tablename__ = "agent_execution_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application_id = Column(String(50), index=True, nullable=False)
    agent_name = Column(String(100), nullable=False)
    agent_input = Column(JSON, nullable=True)
    agent_output = Column(JSON, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
    status = Column(String(50), nullable=False)  # "success", "failed", "timeout"
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<AgentExecutionLog(application_id={self.application_id}, agent={self.agent_name}, status={self.status})>"
