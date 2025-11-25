"""
FastAPI Loan Application API with Tortoise ORM
Complete implementation with POST and GET endpoints
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
import uuid
import random
import time

from tortoise import Tortoise, fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from enum import Enum


# ===================== TORTOISE ORM MODELS =====================

class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_REVIEW = "pending_review"


class AgentType(str, Enum):
    """AI Agent types"""
    CREDIT_SCORING = "credit_scoring"
    RISK_ASSESSMENT = "risk_assessment"
    VERIFICATION = "verification"
    DECISION_ENGINE = "decision_engine"


class LoanApplication(Model):
    """
    Main loan application model
    Stores all applicant and loan request information
    """
    # Primary Key - UUID
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Applicant Information
    applicant_id = fields.CharField(max_length=100, index=True)
    full_name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, index=True)
    phone_number = fields.CharField(max_length=50)
    date_of_birth = fields.DateField(null=True)
    address = fields.TextField(null=True)
    
    # Loan Details
    loan_amount_requested = fields.DecimalField(max_digits=15, decimal_places=2)
    loan_purpose = fields.CharField(max_length=100)
    loan_tenure_months = fields.IntField()
    
    # Credit Information
    credit_score = fields.IntField(null=True)
    monthly_income = fields.DecimalField(max_digits=15, decimal_places=2)
    employment_status = fields.CharField(max_length=50)
    employment_duration_months = fields.IntField()
    
    # Application Status
    status = fields.CharEnumField(
        ApplicationStatus,
        default=ApplicationStatus.SUBMITTED,
        index=True
    )
    
    # Processing Results (populated after AI agents run)
    final_decision = fields.CharField(max_length=50, null=True)
    approved_amount = fields.DecimalField(max_digits=15, decimal_places=2, null=True)
    interest_rate = fields.FloatField(null=True)
    
    # Additional Data
    additional_data = fields.JSONField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    processed_at = fields.DatetimeField(null=True)
    
    class Meta:
        table = "loan_applications"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"LoanApplication({self.id} - {self.full_name})"


class AgentResponse(Model):
    """
    AI Agent response model
    Stores individual agent execution results
    """
    # Primary Key - UUID
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Foreign Key to LoanApplication (One-to-Many)
    loan_application = fields.ForeignKeyField(
        "models.LoanApplication",
        related_name="agent_responses",
        on_delete=fields.CASCADE
    )
    
    # Agent Information
    agent_type = fields.CharEnumField(
        AgentType,
        index=True
    )
    agent_name = fields.CharField(max_length=100)
    agent_version = fields.CharField(max_length=50, default="1.0")
    
    # Agent Output
    response_data = fields.JSONField(description="Agent's response payload")
    confidence_score = fields.FloatField(null=True, description="Confidence level 0-1")
    execution_time_ms = fields.IntField(null=True, description="Execution time in milliseconds")
    
    # Status
    status = fields.CharField(max_length=50, default="success")
    error_message = fields.TextField(null=True)
    
    # Timestamp
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "agent_responses"
        ordering = ["created_at"]
    
    def __str__(self):
        return f"AgentResponse({self.agent_type} - {self.id})"


class AnalyticsSnapshot(Model):
    """
    Analytics snapshot model
    Stores calculated metrics and analytics for the application
    """
    # Primary Key - UUID
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    
    # Foreign Key to LoanApplication (One-to-One)
    loan_application = fields.OneToOneField(
        "models.LoanApplication",
        related_name="analytics_snapshot",
        on_delete=fields.CASCADE
    )
    
    # Calculated Metrics
    calculated_credit_score = fields.IntField(null=True)
    risk_score = fields.FloatField(null=True, description="Risk score 0-100")
    approval_probability = fields.FloatField(null=True, description="Probability 0-1")
    recommended_amount = fields.DecimalField(max_digits=15, decimal_places=2, null=True)
    recommended_interest_rate = fields.FloatField(null=True)
    
    # Debt Ratios
    debt_to_income_ratio = fields.FloatField(null=True)
    loan_to_income_ratio = fields.FloatField(null=True)
    
    # Risk Factors
    risk_factors = fields.JSONField(null=True, description="List of identified risk factors")
    positive_factors = fields.JSONField(null=True, description="List of positive factors")
    
    # Model Scores Breakdown
    model_scores = fields.JSONField(null=True, description="Detailed scoring breakdown")
    
    # Processing Metadata
    processing_time_seconds = fields.FloatField(null=True)
    total_agents_executed = fields.IntField(default=0)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "analytics_snapshots"
    
    def __str__(self):
        return f"AnalyticsSnapshot({self.id} - Score: {self.calculated_credit_score})"


# ===================== PYDANTIC SCHEMAS =====================

class LoanApplicationCreate(BaseModel):
    """Request schema for creating a loan application"""
    # Applicant Information
    applicant_id: str
    full_name: str
    email: EmailStr
    phone_number: str
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    
    # Loan Details
    loan_amount_requested: float = Field(..., gt=0)
    loan_purpose: str
    loan_tenure_months: int = Field(..., gt=0, le=360)
    
    # Financial Information
    monthly_income: float = Field(..., gt=0)
    employment_status: str
    employment_duration_months: int = Field(..., ge=0)
    credit_score: Optional[int] = Field(None, ge=300, le=850)
    
    # Additional Data
    additional_data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "applicant_id": "APP12345",
                "full_name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone_number": "+1-555-0123",
                "date_of_birth": "1990-05-15",
                "address": "123 Main St, New York, NY 10001",
                "loan_amount_requested": 50000.00,
                "loan_purpose": "home_improvement",
                "loan_tenure_months": 60,
                "monthly_income": 6500.00,
                "employment_status": "employed",
                "employment_duration_months": 36,
                "credit_score": 720
            }
        }


class AgentResponseOut(BaseModel):
    """Output schema for agent response"""
    id: str
    agent_type: str
    agent_name: str
    response_data: Dict[str, Any]
    confidence_score: Optional[float]
    execution_time_ms: Optional[int]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsSnapshotOut(BaseModel):
    """Output schema for analytics snapshot"""
    id: str
    calculated_credit_score: Optional[int]
    risk_score: Optional[float]
    approval_probability: Optional[float]
    recommended_amount: Optional[float]
    recommended_interest_rate: Optional[float]
    debt_to_income_ratio: Optional[float]
    risk_factors: Optional[List[str]]
    positive_factors: Optional[List[str]]
    model_scores: Optional[Dict[str, Any]]
    processing_time_seconds: Optional[float]
    total_agents_executed: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoanApplicationOut(BaseModel):
    """Output schema for loan application"""
    id: str
    applicant_id: str
    full_name: str
    email: str
    phone_number: str
    loan_amount_requested: float
    loan_purpose: str
    loan_tenure_months: int
    monthly_income: float
    employment_status: str
    status: str
    final_decision: Optional[str]
    approved_amount: Optional[float]
    interest_rate: Optional[float]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LoanApplicationResponse(BaseModel):
    """Complete response for loan application submission"""
    status: str
    message: str
    application_id: str
    current_status: str
    loan_application: LoanApplicationOut
    agent_responses: List[AgentResponseOut]
    analytics_snapshot: Optional[AnalyticsSnapshotOut]
    processing_time_seconds: float


class LoanApplicationDetailResponse(BaseModel):
    """Complete response for fetching application details"""
    status: str
    loan_application: LoanApplicationOut
    agent_responses: List[AgentResponseOut]
    analytics_snapshot: Optional[AnalyticsSnapshotOut]


# ===================== MOCK AI AGENT SIMULATORS =====================

async def simulate_credit_scoring_agent(application: LoanApplication) -> Dict[str, Any]:
    """
    Simulates credit scoring AI agent
    In production, this would call actual AI/ML model
    """
    await asyncio.sleep(0.1)  # Simulate processing time
    
    # Mock credit score calculation
    base_score = application.credit_score or 650
    income_factor = min(50, float(application.monthly_income) / 1000)
    employment_factor = min(30, application.employment_duration_months / 2)
    
    calculated_score = int(base_score + income_factor + employment_factor)
    calculated_score = max(300, min(850, calculated_score))
    
    return {
        "calculated_credit_score": calculated_score,
        "credit_tier": get_credit_tier(calculated_score),
        "score_breakdown": {
            "base_score": base_score,
            "income_adjustment": income_factor,
            "employment_adjustment": employment_factor
        },
        "factors_affecting_score": [
            "Payment history",
            "Credit utilization",
            "Length of credit history"
        ]
    }


async def simulate_risk_assessment_agent(application: LoanApplication) -> Dict[str, Any]:
    """
    Simulates risk assessment AI agent
    """
    await asyncio.sleep(0.15)  # Simulate processing time
    
    # Calculate DTI ratio
    monthly_loan_payment = float(application.loan_amount_requested) / application.loan_tenure_months
    dti_ratio = monthly_loan_payment / float(application.monthly_income)
    
    # Mock risk score (0-100, lower is better)
    risk_score = 50.0
    if dti_ratio > 0.5:
        risk_score += 30
    elif dti_ratio < 0.3:
        risk_score -= 20
    
    risk_score = max(0, min(100, risk_score))
    
    risk_factors = []
    if dti_ratio > 0.5:
        risk_factors.append("High debt-to-income ratio")
    if application.employment_duration_months < 12:
        risk_factors.append("Short employment history")
    if float(application.loan_amount_requested) > float(application.monthly_income) * 50:
        risk_factors.append("Large loan relative to income")
    
    return {
        "risk_score": risk_score,
        "risk_level": "low" if risk_score < 30 else "medium" if risk_score < 70 else "high",
        "debt_to_income_ratio": round(dti_ratio, 4),
        "loan_to_income_ratio": round(float(application.loan_amount_requested) / (float(application.monthly_income) * 12), 4),
        "risk_factors": risk_factors,
        "mitigation_suggestions": [
            "Consider longer loan tenure to reduce monthly payments",
            "Verify income documentation"
        ] if risk_factors else []
    }


async def simulate_verification_agent(application: LoanApplication) -> Dict[str, Any]:
    """
    Simulates verification AI agent
    """
    await asyncio.sleep(0.1)
    
    return {
        "identity_verified": True,
        "email_verified": True,
        "phone_verified": True,
        "employment_verified": random.choice([True, False]),
        "income_verified": random.choice([True, False]),
        "verification_score": random.uniform(0.7, 1.0),
        "documents_required": [
            "Government-issued ID",
            "Proof of income (pay stubs)",
            "Bank statements (3 months)"
        ],
        "verification_notes": "Standard verification process completed"
    }


async def simulate_decision_engine_agent(
    application: LoanApplication,
    credit_data: Dict,
    risk_data: Dict,
    verification_data: Dict
) -> Dict[str, Any]:
    """
    Simulates loan decision engine
    """
    await asyncio.sleep(0.2)
    
    credit_score = credit_data["calculated_credit_score"]
    risk_score = risk_data["risk_score"]
    dti_ratio = risk_data["debt_to_income_ratio"]
    
    # Decision logic
    if credit_score >= 700 and risk_score < 40 and dti_ratio < 0.4:
        decision = "approved"
        approved_amount = float(application.loan_amount_requested)
        interest_rate = 8.5
    elif credit_score >= 650 and risk_score < 60 and dti_ratio < 0.5:
        decision = "approved"
        approved_amount = float(application.loan_amount_requested) * 0.8
        interest_rate = 11.5
    elif credit_score >= 600:
        decision = "pending_review"
        approved_amount = float(application.loan_amount_requested) * 0.6
        interest_rate = 14.5
    else:
        decision = "rejected"
        approved_amount = 0.0
        interest_rate = None
    
    return {
        "final_decision": decision,
        "approved_amount": approved_amount,
        "interest_rate": interest_rate,
        "decision_rationale": f"Based on credit score of {credit_score}, risk score of {risk_score:.1f}, and DTI ratio of {dti_ratio:.2%}",
        "conditions": [
            "Income verification required",
            "Employment confirmation needed"
        ] if decision == "pending_review" else [],
        "rejection_reasons": [
            "Credit score below minimum threshold",
            "High risk profile"
        ] if decision == "rejected" else [],
        "approval_probability": 0.85 if decision == "approved" else 0.5 if decision == "pending_review" else 0.1
    }


def get_credit_tier(score: int) -> str:
    """Determine credit tier from score"""
    if score >= 800:
        return "Excellent"
    elif score >= 740:
        return "Very Good"
    elif score >= 670:
        return "Good"
    elif score >= 580:
        return "Fair"
    else:
        return "Poor"


# ===================== FASTAPI APPLICATION =====================

import asyncio

app = FastAPI(
    title="Loan Application API with Tortoise ORM",
    description="Complete loan processing system with AI agent simulation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== API ENDPOINTS =====================

@app.post(
    "/loan-applications",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit New Loan Application",
    description="Creates a new loan application and triggers AI agent processing"
)
async def create_loan_application(application_data: LoanApplicationCreate):
    """
    POST /loan-applications
    
    Creates a new loan application, runs AI agents, and returns complete results.
    
    **Process:**
    1. Creates LoanApplication record with UUID
    2. Triggers 4 AI agents (Credit Scoring, Risk Assessment, Verification, Decision Engine)
    3. Stores AgentResponse records for each agent
    4. Creates AnalyticsSnapshot with aggregated metrics
    5. Returns complete application data with all relationships
    
    **Returns:**
    - application_id: Unique UUID for the application
    - current_status: Current processing status
    - agent_responses: Array of all agent execution results
    - analytics_snapshot: Calculated metrics and recommendations
    """
    start_time = time.time()
    
    try:
        # Step 1: Create LoanApplication
        loan_application = await LoanApplication.create(
            applicant_id=application_data.applicant_id,
            full_name=application_data.full_name,
            email=application_data.email,
            phone_number=application_data.phone_number,
            date_of_birth=application_data.date_of_birth,
            address=application_data.address,
            loan_amount_requested=application_data.loan_amount_requested,
            loan_purpose=application_data.loan_purpose,
            loan_tenure_months=application_data.loan_tenure_months,
            credit_score=application_data.credit_score,
            monthly_income=application_data.monthly_income,
            employment_status=application_data.employment_status,
            employment_duration_months=application_data.employment_duration_months,
            additional_data=application_data.additional_data,
            status=ApplicationStatus.PROCESSING
        )
        
        # Step 2: Run AI Agents (simulated)
        # Agent 1: Credit Scoring
        credit_data = await simulate_credit_scoring_agent(loan_application)
        credit_agent_start = time.time()
        await AgentResponse.create(
            loan_application=loan_application,
            agent_type=AgentType.CREDIT_SCORING,
            agent_name="Credit Scoring Agent",
            response_data=credit_data,
            confidence_score=0.92,
            execution_time_ms=int((time.time() - credit_agent_start) * 1000),
            status="success"
        )
        
        # Agent 2: Risk Assessment
        risk_data = await simulate_risk_assessment_agent(loan_application)
        risk_agent_start = time.time()
        await AgentResponse.create(
            loan_application=loan_application,
            agent_type=AgentType.RISK_ASSESSMENT,
            agent_name="Risk Assessment Agent",
            response_data=risk_data,
            confidence_score=0.88,
            execution_time_ms=int((time.time() - risk_agent_start) * 1000),
            status="success"
        )
        
        # Agent 3: Verification
        verification_data = await simulate_verification_agent(loan_application)
        verification_agent_start = time.time()
        await AgentResponse.create(
            loan_application=loan_application,
            agent_type=AgentType.VERIFICATION,
            agent_name="Verification Agent",
            response_data=verification_data,
            confidence_score=0.95,
            execution_time_ms=int((time.time() - verification_agent_start) * 1000),
            status="success"
        )
        
        # Agent 4: Decision Engine
        decision_data = await simulate_decision_engine_agent(
            loan_application,
            credit_data,
            risk_data,
            verification_data
        )
        decision_agent_start = time.time()
        await AgentResponse.create(
            loan_application=loan_application,
            agent_type=AgentType.DECISION_ENGINE,
            agent_name="Decision Engine Agent",
            response_data=decision_data,
            confidence_score=0.90,
            execution_time_ms=int((time.time() - decision_agent_start) * 1000),
            status="success"
        )
        
        # Step 3: Create Analytics Snapshot
        processing_time = time.time() - start_time
        
        analytics_snapshot = await AnalyticsSnapshot.create(
            loan_application=loan_application,
            calculated_credit_score=credit_data["calculated_credit_score"],
            risk_score=risk_data["risk_score"],
            approval_probability=decision_data["approval_probability"],
            recommended_amount=decision_data["approved_amount"],
            recommended_interest_rate=decision_data["interest_rate"],
            debt_to_income_ratio=risk_data["debt_to_income_ratio"],
            loan_to_income_ratio=risk_data["loan_to_income_ratio"],
            risk_factors=risk_data["risk_factors"],
            positive_factors=["Stable employment", "Good credit history"] if credit_data["calculated_credit_score"] > 700 else [],
            model_scores={
                "credit_score": credit_data["calculated_credit_score"],
                "risk_score": risk_data["risk_score"],
                "verification_score": verification_data["verification_score"]
            },
            processing_time_seconds=processing_time,
            total_agents_executed=4
        )
        
        # Step 4: Update LoanApplication with final decision
        loan_application.final_decision = decision_data["final_decision"]
        loan_application.approved_amount = decision_data["approved_amount"]
        loan_application.interest_rate = decision_data["interest_rate"]
        loan_application.status = ApplicationStatus.COMPLETED
        loan_application.processed_at = datetime.utcnow()
        await loan_application.save()
        
        # Step 5: Fetch all related data for response
        await loan_application.fetch_related("agent_responses", "analytics_snapshot")
        
        # Step 6: Build response
        agent_responses_out = [
            AgentResponseOut(
                id=str(agent.id),
                agent_type=agent.agent_type,
                agent_name=agent.agent_name,
                response_data=agent.response_data,
                confidence_score=agent.confidence_score,
                execution_time_ms=agent.execution_time_ms,
                status=agent.status,
                created_at=agent.created_at
            )
            for agent in loan_application.agent_responses
        ]
        
        analytics_out = AnalyticsSnapshotOut(
            id=str(analytics_snapshot.id),
            calculated_credit_score=analytics_snapshot.calculated_credit_score,
            risk_score=analytics_snapshot.risk_score,
            approval_probability=analytics_snapshot.approval_probability,
            recommended_amount=float(analytics_snapshot.recommended_amount) if analytics_snapshot.recommended_amount else None,
            recommended_interest_rate=analytics_snapshot.recommended_interest_rate,
            debt_to_income_ratio=analytics_snapshot.debt_to_income_ratio,
            risk_factors=analytics_snapshot.risk_factors,
            positive_factors=analytics_snapshot.positive_factors,
            model_scores=analytics_snapshot.model_scores,
            processing_time_seconds=analytics_snapshot.processing_time_seconds,
            total_agents_executed=analytics_snapshot.total_agents_executed,
            created_at=analytics_snapshot.created_at
        )
        
        loan_application_out = LoanApplicationOut(
            id=str(loan_application.id),
            applicant_id=loan_application.applicant_id,
            full_name=loan_application.full_name,
            email=loan_application.email,
            phone_number=loan_application.phone_number,
            loan_amount_requested=float(loan_application.loan_amount_requested),
            loan_purpose=loan_application.loan_purpose,
            loan_tenure_months=loan_application.loan_tenure_months,
            monthly_income=float(loan_application.monthly_income),
            employment_status=loan_application.employment_status,
            status=loan_application.status,
            final_decision=loan_application.final_decision,
            approved_amount=float(loan_application.approved_amount) if loan_application.approved_amount else None,
            interest_rate=loan_application.interest_rate,
            created_at=loan_application.created_at,
            processed_at=loan_application.processed_at
        )
        
        return LoanApplicationResponse(
            status="success",
            message=f"Loan application processed successfully. Decision: {decision_data['final_decision']}",
            application_id=str(loan_application.id),
            current_status=loan_application.status,
            loan_application=loan_application_out,
            agent_responses=agent_responses_out,
            analytics_snapshot=analytics_out,
            processing_time_seconds=round(processing_time, 3)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process loan application: {str(e)}"
        )


@app.get(
    "/loan-applications/{application_id}",
    response_model=LoanApplicationDetailResponse,
    summary="Get Loan Application Details",
    description="Fetches complete loan application with all agent responses and analytics"
)
async def get_loan_application(application_id: str):
    """
    GET /loan-applications/{application_id}
    
    Retrieves a loan application by UUID with all related data.
    
    **Parameters:**
    - application_id: UUID of the loan application
    
    **Returns:**
    - Complete loan application details
    - All agent responses (credit scoring, risk assessment, verification, decision)
    - Analytics snapshot with calculated metrics
    
    **Errors:**
    - 400: Invalid UUID format
    - 404: Application not found
    """
    try:
        # Validate UUID format
        try:
            app_uuid = UUID(application_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application ID format. Must be a valid UUID."
            )
        
        # Fetch application with all relationships
        loan_application = await LoanApplication.get_or_none(id=app_uuid).prefetch_related(
            "agent_responses",
            "analytics_snapshot"
        )
        
        if not loan_application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Loan application with ID {application_id} not found"
            )
        
        # Build response
        agent_responses_out = [
            AgentResponseOut(
                id=str(agent.id),
                agent_type=agent.agent_type,
                agent_name=agent.agent_name,
                response_data=agent.response_data,
                confidence_score=agent.confidence_score,
                execution_time_ms=agent.execution_time_ms,
                status=agent.status,
                created_at=agent.created_at
            )
            for agent in loan_application.agent_responses
        ]
        
        analytics_out = None
        if hasattr(loan_application, 'analytics_snapshot') and loan_application.analytics_snapshot:
            analytics = loan_application.analytics_snapshot
            analytics_out = AnalyticsSnapshotOut(
                id=str(analytics.id),
                calculated_credit_score=analytics.calculated_credit_score,
                risk_score=analytics.risk_score,
                approval_probability=analytics.approval_probability,
                recommended_amount=float(analytics.recommended_amount) if analytics.recommended_amount else None,
                recommended_interest_rate=analytics.recommended_interest_rate,
                debt_to_income_ratio=analytics.debt_to_income_ratio,
                risk_factors=analytics.risk_factors,
                positive_factors=analytics.positive_factors,
                model_scores=analytics.model_scores,
                processing_time_seconds=analytics.processing_time_seconds,
                total_agents_executed=analytics.total_agents_executed,
                created_at=analytics.created_at
            )
        
        loan_application_out = LoanApplicationOut(
            id=str(loan_application.id),
            applicant_id=loan_application.applicant_id,
            full_name=loan_application.full_name,
            email=loan_application.email,
            phone_number=loan_application.phone_number,
            loan_amount_requested=float(loan_application.loan_amount_requested),
            loan_purpose=loan_application.loan_purpose,
            loan_tenure_months=loan_application.loan_tenure_months,
            monthly_income=float(loan_application.monthly_income),
            employment_status=loan_application.employment_status,
            status=loan_application.status,
            final_decision=loan_application.final_decision,
            approved_amount=float(loan_application.approved_amount) if loan_application.approved_amount else None,
            interest_rate=loan_application.interest_rate,
            created_at=loan_application.created_at,
            processed_at=loan_application.processed_at
        )
        
        return LoanApplicationDetailResponse(
            status="success",
            loan_application=loan_application_out,
            agent_responses=agent_responses_out,
            analytics_snapshot=analytics_out
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch loan application: {str(e)}"
        )


@app.get("/", summary="Root Endpoint")
async def root():
    """Root endpoint with API information"""
    return {
        "status": "online",
        "service": "Loan Application API",
        "version": "1.0.0",
        "endpoints": {
            "submit_application": "POST /loan-applications",
            "get_application": "GET /loan-applications/{application_id}",
            "documentation": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await LoanApplication.all().count()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ===================== DATABASE INITIALIZATION =====================

# Register Tortoise with FastAPI
register_tortoise(
    app,
    db_url="sqlite://./loan_application.db",  # Change to PostgreSQL in production
    modules={"models": ["__main__"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


# ===================== RUN APPLICATION =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "loan_api_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
