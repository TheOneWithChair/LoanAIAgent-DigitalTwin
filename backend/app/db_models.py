"""
Database Models for Loan Processing System
Using Tortoise ORM with Neon PostgreSQL
"""
from tortoise import fields
from tortoise.models import Model
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    CONDITIONAL = "conditional"


class AgentStatus(str, Enum):
    """Agent execution status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class LoanApplication(Model):
    """
    Main loan application model
    Stores applicant information and application status
    """
    # Primary Key
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Applicant Information
    applicant_id = fields.CharField(max_length=100, index=True, description="Unique applicant identifier")
    full_name = fields.CharField(max_length=255, description="Full name of applicant")
    email = fields.CharField(max_length=255, index=True, description="Email address")
    phone_number = fields.CharField(max_length=50, description="Contact phone number")
    address = fields.TextField(null=True, description="Residential address")
    
    # Application Status
    application_status = fields.CharEnumField(
        ApplicationStatus,
        default=ApplicationStatus.IN_PROGRESS,
        index=True,
        description="Current status of the application"
    )
    
    # Loan Details
    loan_amount_requested = fields.DecimalField(max_digits=15, decimal_places=2, description="Requested loan amount")
    loan_purpose = fields.CharField(max_length=100, description="Purpose of the loan")
    loan_tenure_months = fields.IntField(description="Loan tenure in months")
    
    # Credit Information
    credit_history_length_months = fields.IntField(description="Credit history length in months")
    number_of_credit_accounts = fields.IntField(description="Total number of credit accounts")
    credit_utilization_percent = fields.FloatField(description="Credit utilization percentage")
    recent_credit_inquiries = fields.IntField(default=0, description="Recent credit inquiries")
    
    # Employment & Income
    employment_status = fields.CharField(max_length=50, description="Employment status")
    employment_duration_months = fields.IntField(description="Employment duration in months")
    monthly_income = fields.DecimalField(max_digits=15, decimal_places=2, description="Monthly income")
    income_verified = fields.BooleanField(default=False, description="Whether income is verified")
    
    # Decision Results (populated after processing)
    calculated_credit_score = fields.IntField(null=True, description="Calculated credit score")
    final_decision = fields.CharField(max_length=50, null=True, description="Final loan decision")
    approved_amount = fields.DecimalField(max_digits=15, decimal_places=2, null=True, description="Approved loan amount")
    interest_rate = fields.FloatField(null=True, description="Interest rate offered")
    risk_level = fields.CharField(max_length=20, null=True, description="Risk level assessment")
    
    # Processing Metadata
    processing_time_seconds = fields.FloatField(null=True, description="Total processing time")
    workflow_status = fields.CharField(max_length=50, default="pending", description="Workflow execution status")
    
    # Additional Data (stored as JSON)
    credit_mix = fields.JSONField(null=True, description="Credit mix details")
    repayment_history = fields.JSONField(null=True, description="Repayment history details")
    additional_metadata = fields.JSONField(null=True, description="Additional application metadata")
    
    # Timestamps
    submitted_at = fields.DatetimeField(auto_now_add=True, description="Application submission timestamp")
    updated_at = fields.DatetimeField(auto_now=True, description="Last update timestamp")
    processed_at = fields.DatetimeField(null=True, description="Processing completion timestamp")
    
    class Meta:
        table = "loan_applications"
        indexes = [
            ("applicant_id", "submitted_at"),
            ("application_status", "submitted_at"),
            ("email",),
        ]
        ordering = ["-submitted_at"]
    
    def __str__(self):
        return f"LoanApplication({self.applicant_id} - {self.full_name} - {self.application_status})"
    
    async def get_all_agent_results(self):
        """Get all agent results for this application"""
        return await AgentResult.filter(loan_application=self).all()
    
    async def get_analytics(self):
        """Get analytics for this application"""
        return await ApplicationAnalytics.filter(loan_application=self).first()


class AgentResult(Model):
    """
    Agent execution results model
    Stores individual agent outputs and execution metadata
    """
    # Primary Key
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Foreign Key to LoanApplication
    loan_application = fields.ForeignKeyField(
        "models.LoanApplication",
        related_name="agent_results",
        on_delete=fields.CASCADE,
        description="Related loan application"
    )
    
    # Agent Information
    agent_name = fields.CharField(max_length=100, index=True, description="Name of the AI agent")
    status = fields.CharEnumField(
        AgentStatus,
        default=AgentStatus.PENDING,
        index=True,
        description="Agent execution status"
    )
    
    # Agent Output
    output = fields.JSONField(null=True, description="Agent output data (JSON)")
    error_message = fields.TextField(null=True, description="Error message if agent failed")
    
    # Execution Metadata
    execution_time = fields.FloatField(null=True, description="Execution time in seconds")
    timestamp = fields.DatetimeField(auto_now_add=True, description="Execution timestamp")
    
    # Additional Context
    agent_input = fields.JSONField(null=True, description="Input data sent to agent")
    agent_version = fields.CharField(max_length=50, null=True, description="Agent version")
    
    class Meta:
        table = "agent_results"
        indexes = [
            ("loan_application", "agent_name"),
            ("status", "timestamp"),
        ]
        ordering = ["timestamp"]
    
    def __str__(self):
        return f"AgentResult({self.agent_name} - {self.status} - {self.timestamp})"


class ApplicationAnalytics(Model):
    """
    Application analytics model
    Stores calculated metrics and analytics for loan applications
    """
    # Primary Key
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Foreign Key to LoanApplication (One-to-One)
    loan_application = fields.OneToOneField(
        "models.LoanApplication",
        related_name="analytics",
        on_delete=fields.CASCADE,
        description="Related loan application"
    )
    
    # Credit Metrics
    credit_score = fields.IntField(null=True, description="Calculated credit score (300-850)")
    credit_tier = fields.CharField(max_length=50, null=True, description="Credit tier (Excellent/Good/Fair/Poor)")
    
    # Risk Assessment
    risk_level = fields.CharEnumField(
        RiskLevel,
        null=True,
        index=True,
        description="Risk level assessment"
    )
    risk_score = fields.FloatField(null=True, description="Numeric risk score (0-100)")
    
    # Approval Metrics
    approval_probability = fields.FloatField(
        null=True,
        description="Probability of approval (0.0 - 1.0)"
    )
    recommended_amount = fields.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        description="Recommended loan amount"
    )
    recommended_interest_rate = fields.FloatField(
        null=True,
        description="Recommended interest rate"
    )
    
    # DTI and Financial Ratios
    debt_to_income_ratio = fields.FloatField(null=True, description="Debt-to-income ratio")
    loan_to_income_ratio = fields.FloatField(null=True, description="Loan-to-income ratio")
    
    # Detailed Breakdown (stored as JSON)
    credit_score_breakdown = fields.JSONField(null=True, description="Detailed credit score breakdown")
    risk_factors = fields.JSONField(null=True, description="List of risk factors")
    approval_factors = fields.JSONField(null=True, description="Factors influencing approval")
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, description="Analytics creation timestamp")
    updated_at = fields.DatetimeField(auto_now=True, description="Last update timestamp")
    
    class Meta:
        table = "application_analytics"
        indexes = [
            ("risk_level", "credit_score"),
            ("approval_probability",),
        ]
    
    def __str__(self):
        return f"ApplicationAnalytics(Score: {self.credit_score}, Risk: {self.risk_level}, Prob: {self.approval_probability})"


class AuditLog(Model):
    """
    Audit log model for tracking all changes and actions
    """
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Related Application (optional)
    loan_application = fields.ForeignKeyField(
        "models.LoanApplication",
        related_name="audit_logs",
        null=True,
        on_delete=fields.SET_NULL
    )
    
    # Action Details
    action = fields.CharField(max_length=100, index=True, description="Action performed")
    entity_type = fields.CharField(max_length=100, description="Type of entity (e.g., LoanApplication)")
    entity_id = fields.CharField(max_length=100, description="ID of the affected entity")
    
    # Change Details
    old_value = fields.JSONField(null=True, description="Previous value")
    new_value = fields.JSONField(null=True, description="New value")
    
    # User/System Context
    performed_by = fields.CharField(max_length=100, default="system", description="Who performed the action")
    ip_address = fields.CharField(max_length=45, null=True, description="IP address")
    
    # Timestamp
    timestamp = fields.DatetimeField(auto_now_add=True, index=True, description="Action timestamp")
    
    class Meta:
        table = "audit_logs"
        indexes = [
            ("action", "timestamp"),
            ("entity_type", "entity_id"),
        ]
        ordering = ["-timestamp"]
    
    def __str__(self):
        return f"AuditLog({self.action} - {self.entity_type} - {self.timestamp})"
