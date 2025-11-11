# LangGraph Orchestrator and AI Agents for Loan Processing

from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional
import logging
import time
import asyncio
from datetime import datetime

from app.agent_state import (
    LoanProcessingState,
    AgentResult,
    update_agent_result,
    finalize_state
)
from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# LLM Initialization (Groq ONLY)
# ============================================================================

def get_llm():
    """
    Get Groq LLM instance.
    This system uses ONLY Groq API with Llama 3.3 70B model.
    
    Returns:
        ChatGroq instance
    
    Raises:
        ValueError: If GROQ_API_KEY is not configured
    """
    if not settings.GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is required. Please set it in your .env file.\n"
            "Get your free API key from: https://console.groq.com/keys"
        )
    
    try:
        from langchain_groq import ChatGroq
        logger.info(f"Initializing Groq LLM with model: {settings.GROQ_MODEL}")
        return ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=0.1,
            max_tokens=2048
        )
    except Exception as e:
        logger.error(f"Error initializing Groq LLM: {e}")
        raise


# ============================================================================
# AI Agent Functions
# ============================================================================

async def credit_scoring_agent(state: LoanProcessingState) -> LoanProcessingState:
    """
    Credit Scoring Agent: Analyzes credit history and calculates credit score.
    
    Inputs from state:
        - credit_history_length_months
        - number_of_credit_accounts
        - credit_utilization_percent
        - repayment_history
        - recent_credit_inquiries_6m
        
    Outputs:
        - calculated_credit_score (300-850)
        - credit_score_factors (list of contributing factors)
        - credit_score_rationale (explanation)
    """
    start_time = time.time()
    logger.info(f"[{state['application_id']}] Starting Credit Scoring Agent")
    
    try:
        # Extract relevant data
        app_data = state["application_data"]
        
        # TODO: Replace with actual AI model call (OpenAI, Anthropic, etc.)
        # For now, using a simplified calculation
        
        # Base score calculation (simplified)
        base_score = 500
        
        # Credit history length (up to +100 points)
        history_months = app_data.get("credit_history_length_months", 0)
        history_score = min(100, (history_months / 120) * 100)
        
        # Payment history (up to +200 points)
        repayment = app_data.get("repayment_history", {})
        total_payments = repayment.get("on_time_payments", 0) + repayment.get("late_payments", 0)
        if total_payments > 0:
            payment_rate = repayment.get("on_time_payments", 0) / total_payments
            payment_score = payment_rate * 200
        else:
            payment_score = 0
        
        # Credit utilization (up to +50 points, penalty for high utilization)
        utilization = app_data.get("credit_utilization_percent", 0)
        if utilization < 30:
            utilization_score = 50
        elif utilization < 50:
            utilization_score = 30
        elif utilization < 75:
            utilization_score = 10
        else:
            utilization_score = -20
        
        # Credit inquiries (penalty for many inquiries)
        inquiries = app_data.get("recent_credit_inquiries_6m", 0)
        inquiry_penalty = min(50, inquiries * 10)
        
        # Defaults and write-offs (severe penalties)
        defaults = repayment.get("defaults", 0)
        writeoffs = repayment.get("write_offs", 0)
        default_penalty = defaults * 50 + writeoffs * 100
        
        # Calculate final score
        calculated_score = int(
            base_score + 
            history_score + 
            payment_score + 
            utilization_score - 
            inquiry_penalty - 
            default_penalty
        )
        
        # Clamp to valid range
        calculated_score = max(300, min(850, calculated_score))
        
        # Determine credit tier
        if calculated_score >= 750:
            credit_tier = "Excellent"
        elif calculated_score >= 700:
            credit_tier = "Good"
        elif calculated_score >= 650:
            credit_tier = "Fair"
        elif calculated_score >= 600:
            credit_tier = "Poor"
        else:
            credit_tier = "Very Poor"
        
        # Build result
        output = {
            "calculated_credit_score": calculated_score,
            "credit_tier": credit_tier,
            "credit_score_factors": [
                f"Credit history: {history_months} months",
                f"Payment history: {payment_rate*100:.1f}% on-time" if total_payments > 0 else "No payment history",
                f"Credit utilization: {utilization:.1f}%",
                f"Recent inquiries: {inquiries}",
                f"Defaults: {defaults}",
                f"Write-offs: {writeoffs}"
            ],
            "credit_score_rationale": f"Credit score of {calculated_score} ({credit_tier}) based on payment history, credit utilization, and account age."
        }
        
        # Update state
        state["calculated_credit_score"] = calculated_score
        
        execution_time = time.time() - start_time
        result = AgentResult(
            agent_name="credit_scoring",
            status="success",
            output=output,
            error=None,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"[{state['application_id']}] Credit Scoring completed: {calculated_score} ({credit_tier})")
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{state['application_id']}] Credit Scoring Agent failed: {e}")
        result = AgentResult(
            agent_name="credit_scoring",
            status="failed",
            output=None,
            error=str(e),
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
    
    return update_agent_result(state, "credit_scoring", result)


async def loan_decision_agent(state: LoanProcessingState) -> LoanProcessingState:
    """
    Loan Decision Agent: Makes lending decision based on all available data.
    
    Inputs from state:
        - calculated_credit_score
        - loan_amount_requested
        - monthly_income
        - employment_status
        - existing_debts
        
    Outputs:
        - final_decision ("approved", "rejected", "under_review")
        - approved_amount
        - interest_rate
        - decision_rationale
        - conditions (list of conditions if approved)
    """
    start_time = time.time()
    logger.info(f"[{state['application_id']}] Starting Loan Decision Agent")
    
    try:
        app_data = state["application_data"]
        credit_score = state.get("calculated_credit_score", 0)
        
        # Extract key factors
        loan_requested = app_data.get("loan_amount_requested", 0)
        monthly_income = app_data.get("monthly_income", 0)
        employment_status = app_data.get("employment_status", "")
        loan_tenure = app_data.get("loan_tenure_months", 0)
        
        # Calculate DTI ratio
        if loan_tenure > 0 and monthly_income > 0:
            monthly_payment = loan_requested / loan_tenure
            dti_ratio = monthly_payment / monthly_income
        else:
            dti_ratio = 1.0
        
        # Decision logic
        rejection_reasons = []
        approved = True
        
        # Credit score threshold
        if credit_score < 600:
            rejection_reasons.append("Credit score below minimum threshold (600)")
            approved = False
        
        # Employment check
        if employment_status == "Unemployed":
            rejection_reasons.append("Unemployed applicants not eligible")
            approved = False
        
        # DTI ratio check
        if dti_ratio > settings.MAX_DTI_RATIO:
            rejection_reasons.append(f"DTI ratio ({dti_ratio:.1%}) exceeds maximum ({settings.MAX_DTI_RATIO:.1%})")
            approved = False
        
        # Determine decision and terms
        if approved:
            final_decision = "approved"
            approved_amount = loan_requested
            
            # Interest rate based on credit score
            if credit_score >= 750:
                interest_rate = 3.5
            elif credit_score >= 700:
                interest_rate = 5.5
            elif credit_score >= 650:
                interest_rate = 7.5
            else:
                interest_rate = 10.5
            
            conditions = [
                "Income verification required",
                "Collateral may be required for amounts over $100,000"
            ]
            decision_rationale = f"Application approved based on credit score ({credit_score}), income ({monthly_income:.0f}/month), and DTI ratio ({dti_ratio:.1%})"
        else:
            final_decision = "rejected"
            approved_amount = 0.0
            interest_rate = None
            conditions = []
            decision_rationale = "Application rejected: " + "; ".join(rejection_reasons)
        
        # Build output
        output = {
            "final_decision": final_decision,
            "approved_amount": approved_amount,
            "interest_rate": interest_rate,
            "decision_rationale": decision_rationale,
            "rejection_reasons": rejection_reasons if not approved else None,
            "conditions": conditions if approved else None,
            "dti_ratio": dti_ratio
        }
        
        # Update state
        state["final_decision"] = final_decision
        state["approved_amount"] = approved_amount
        state["interest_rate"] = interest_rate
        state["rejection_reasons"] = rejection_reasons if rejection_reasons else None
        
        execution_time = time.time() - start_time
        result = AgentResult(
            agent_name="loan_decision",
            status="success",
            output=output,
            error=None,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"[{state['application_id']}] Loan Decision completed: {final_decision}")
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{state['application_id']}] Loan Decision Agent failed: {e}")
        result = AgentResult(
            agent_name="loan_decision",
            status="failed",
            output=None,
            error=str(e),
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
    
    return update_agent_result(state, "loan_decision", result)


async def verification_agent(state: LoanProcessingState) -> LoanProcessingState:
    """
    Verification Agent: Verifies applicant information and documents.
    
    Inputs from state:
        - email
        - phone_number
        - income_verified
        - employment_status
        
    Outputs:
        - verification_status ("verified", "pending", "failed")
        - verified_fields (list of verified fields)
        - pending_verifications (list of fields needing verification)
        - verification_notes
    """
    start_time = time.time()
    logger.info(f"[{state['application_id']}] Starting Verification Agent")
    
    try:
        app_data = state["application_data"]
        
        # Check verification status of various fields
        verified_fields = []
        pending_verifications = []
        
        # Email verification (simulated)
        email = app_data.get("email", "")
        if email and "@" in email:
            verified_fields.append("email")
        else:
            pending_verifications.append("email")
        
        # Phone verification (simulated)
        phone = app_data.get("phone_number", "")
        if phone and len(phone) >= 10:
            verified_fields.append("phone")
        else:
            pending_verifications.append("phone")
        
        # Income verification
        income_verified = app_data.get("income_verified", False)
        if income_verified:
            verified_fields.append("income")
        else:
            pending_verifications.append("income")
        
        # Employment verification
        employment_status = app_data.get("employment_status", "")
        if employment_status in ["Employed", "Self-employed"]:
            verified_fields.append("employment")
        
        # Determine overall status
        if len(pending_verifications) == 0:
            verification_status = "verified"
        elif len(verified_fields) > 0:
            verification_status = "pending"
        else:
            verification_status = "failed"
        
        output = {
            "verification_status": verification_status,
            "verified_fields": verified_fields,
            "pending_verifications": pending_verifications,
            "verification_notes": f"Verified {len(verified_fields)} fields, {len(pending_verifications)} pending"
        }
        
        execution_time = time.time() - start_time
        result = AgentResult(
            agent_name="verification",
            status="success",
            output=output,
            error=None,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"[{state['application_id']}] Verification completed: {verification_status}")
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{state['application_id']}] Verification Agent failed: {e}")
        result = AgentResult(
            agent_name="verification",
            status="failed",
            output=None,
            error=str(e),
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
    
    return update_agent_result(state, "verification", result)


async def risk_monitoring_agent(state: LoanProcessingState) -> LoanProcessingState:
    """
    Risk Monitoring Agent: Assesses overall risk level.
    
    Inputs from state:
        - calculated_credit_score
        - final_decision
        - repayment_history (defaults, write-offs)
        - credit_utilization_percent
        
    Outputs:
        - risk_level ("low", "medium", "high")
        - risk_score (0-100)
        - risk_factors (list of risk factors)
        - recommended_actions (list of mitigation steps)
    """
    start_time = time.time()
    logger.info(f"[{state['application_id']}] Starting Risk Monitoring Agent")
    
    try:
        app_data = state["application_data"]
        credit_score = state.get("calculated_credit_score", 0)
        
        # Calculate risk score (0-100, where 100 is highest risk)
        risk_score = 0
        risk_factors = []
        
        # Credit score risk
        if credit_score < 600:
            risk_score += 40
            risk_factors.append("Low credit score")
        elif credit_score < 650:
            risk_score += 25
            risk_factors.append("Below-average credit score")
        elif credit_score < 700:
            risk_score += 10
        
        # Credit utilization risk
        utilization = app_data.get("credit_utilization_percent", 0)
        if utilization > 80:
            risk_score += 20
            risk_factors.append("High credit utilization")
        elif utilization > 50:
            risk_score += 10
        
        # Payment history risk
        repayment = app_data.get("repayment_history", {})
        defaults = repayment.get("defaults", 0)
        writeoffs = repayment.get("write_offs", 0)
        
        if writeoffs > 0:
            risk_score += 30
            risk_factors.append(f"{writeoffs} loan write-off(s)")
        if defaults > 0:
            risk_score += 20
            risk_factors.append(f"{defaults} default(s)")
        
        late_payments = repayment.get("late_payments", 0)
        if late_payments > 5:
            risk_score += 15
            risk_factors.append(f"{late_payments} late payments")
        
        # Recent inquiries risk
        inquiries = app_data.get("recent_credit_inquiries_6m", 0)
        if inquiries > 6:
            risk_score += 10
            risk_factors.append("Multiple recent credit inquiries")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Recommended actions
        recommended_actions = []
        if risk_level == "high":
            recommended_actions.extend([
                "Require additional collateral",
                "Consider co-signer requirement",
                "Implement enhanced monitoring"
            ])
        elif risk_level == "medium":
            recommended_actions.extend([
                "Regular payment monitoring",
                "Consider payment protection insurance"
            ])
        else:
            recommended_actions.append("Standard monitoring protocol")
        
        output = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommended_actions": recommended_actions
        }
        
        # Update state
        state["risk_level"] = risk_level
        
        execution_time = time.time() - start_time
        result = AgentResult(
            agent_name="risk_monitoring",
            status="success",
            output=output,
            error=None,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"[{state['application_id']}] Risk Monitoring completed: {risk_level} risk")
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{state['application_id']}] Risk Monitoring Agent failed: {e}")
        result = AgentResult(
            agent_name="risk_monitoring",
            status="failed",
            output=None,
            error=str(e),
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
    
    return update_agent_result(state, "risk_monitoring", result)


# ============================================================================
# LangGraph Orchestrator
# ============================================================================

def create_loan_processing_workflow() -> StateGraph:
    """
    Create LangGraph workflow for loan processing.
    
    Workflow sequence:
        1. Credit Scoring Agent
        2. Loan Decision Agent
        3. Verification Agent
        4. Risk Monitoring Agent
        5. Finalization
    """
    # Create the graph
    workflow = StateGraph(LoanProcessingState)
    
    # Add nodes (agents)
    workflow.add_node("credit_scoring", credit_scoring_agent)
    workflow.add_node("loan_decision", loan_decision_agent)
    workflow.add_node("verification", verification_agent)
    workflow.add_node("risk_monitoring", risk_monitoring_agent)
    
    # Define the flow
    workflow.set_entry_point("credit_scoring")
    workflow.add_edge("credit_scoring", "loan_decision")
    workflow.add_edge("loan_decision", "verification")
    workflow.add_edge("verification", "risk_monitoring")
    workflow.add_edge("risk_monitoring", END)
    
    # Compile the graph
    return workflow.compile()


# Global workflow instance
loan_processing_graph = create_loan_processing_workflow()


async def process_loan_application(
    application_id: str,
    applicant_id: str,
    application_data: Dict[str, Any]
) -> LoanProcessingState:
    """
    Execute the complete loan processing workflow.
    
    Args:
        application_id: Unique application identifier
        applicant_id: Applicant identifier
        application_data: Complete loan application data
        
    Returns:
        Final state with all agent results
    """
    from app.agent_state import create_initial_state
    
    logger.info(f"[{application_id}] Starting loan processing workflow")
    
    # Create initial state
    initial_state = create_initial_state(
        application_id=application_id,
        applicant_id=applicant_id,
        application_data=application_data
    )
    
    initial_state["workflow_status"] = "in_progress"
    
    try:
        # Execute the workflow
        final_state = await loan_processing_graph.ainvoke(initial_state)
        
        # Finalize the state
        final_state = finalize_state(final_state)
        
        logger.info(f"[{application_id}] Workflow completed successfully")
        return final_state
        
    except Exception as e:
        logger.error(f"[{application_id}] Workflow failed: {e}")
        initial_state["workflow_status"] = "failed"
        initial_state["errors"].append(f"Workflow execution failed: {str(e)}")
        return finalize_state(initial_state)
