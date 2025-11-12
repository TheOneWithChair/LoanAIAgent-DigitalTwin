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
        
        # Improved credit scoring algorithm (more realistic)
        
        # Base score 
        base_score = 350  # Increased from 300
        
        # Credit history length (up to +120 points, diminishing returns)
        history_months = app_data.get("credit_history_length_months", 0)
        if history_months >= 84:  # 7+ years
            history_score = 120
        elif history_months >= 60:  # 5+ years
            history_score = 90
        elif history_months >= 36:  # 3+ years
            history_score = 60
        elif history_months >= 24:  # 2+ years
            history_score = 40
        else:
            history_score = history_months  # Linear for < 2 years
        
        # Payment history (critical factor - up to +280 points)
        repayment = app_data.get("repayment_history", {})
        on_time = repayment.get("on_time_payments", 0)
        late = repayment.get("late_payments", 0)
        defaults = repayment.get("defaults", 0)
        writeoffs = repayment.get("write_offs", 0)
        
        total_payments = on_time + late
        if total_payments > 0:
            payment_rate = on_time / total_payments
            # Base payment score - rewards high on-time rate
            payment_score = payment_rate * 280
            
            # Moderate penalties for late payments (context-aware)
            # Penalty should be proportional to the severity relative to total history
            if late == 0:
                late_penalty = 0
            elif total_payments >= 70:  # Extensive history - more forgiving
                if late <= 2:
                    late_penalty = late * 12  # -12 per late (reduced from 15)
                elif late <= 4:
                    late_penalty = 24 + (late - 2) * 18
                else:
                    late_penalty = 60 + (late - 4) * 22
            elif total_payments >= 40:  # Moderate history
                if late <= 2:
                    late_penalty = late * 18  # -18 per late (reduced from 20)
                elif late <= 4:
                    late_penalty = 36 + (late - 2) * 25
                else:
                    late_penalty = 86 + (late - 4) * 30
            else:  # Limited history - more impact
                if late <= 2:
                    late_penalty = late * 22  # -22 per late (reduced from 25)
                elif late <= 4:
                    late_penalty = 44 + (late - 2) * 30
                else:
                    late_penalty = 104 + (late - 4) * 35
            
            payment_score -= late_penalty
        else:
            payment_score = 0
        
        # Credit utilization (up to +60, significant penalties for high usage)
        utilization = app_data.get("credit_utilization_percent", 0)
        if utilization < 10:
            utilization_score = 60
        elif utilization < 30:
            utilization_score = 50
        elif utilization < 50:
            utilization_score = 30
        elif utilization < 70:
            utilization_score = 0
        elif utilization < 85:
            utilization_score = -20
        else:
            utilization_score = -40
        
        # Credit inquiries (indicates credit shopping - moderate impact)
        inquiries = app_data.get("recent_credit_inquiries_6m", 0)
        if inquiries == 0:
            inquiry_penalty = 0
        elif inquiries <= 2:
            inquiry_penalty = inquiries * 3  # -3 per inquiry (minimal)
        elif inquiries <= 4:
            inquiry_penalty = 6 + (inquiries - 2) * 8  # -8 per additional
        elif inquiries <= 6:
            inquiry_penalty = 22 + (inquiries - 4) * 12
        else:
            inquiry_penalty = 46 + (inquiries - 6) * 15
        
        # Defaults and write-offs (critical red flags)
        default_penalty = defaults * 100 + writeoffs * 150
        
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
        
        # Determine credit tier (Indian credit scoring standard)
        if calculated_score >= 750:
            credit_tier = "Excellent"
        elif calculated_score >= 700:
            credit_tier = "Very Good"
        elif calculated_score >= 650:
            credit_tier = "Good"
        elif calculated_score >= 600:
            credit_tier = "Fair"
        elif calculated_score >= 550:
            credit_tier = "Poor"
        else:
            credit_tier = "Very Poor"
        
        # Build result with detailed breakdown
        output = {
            "calculated_credit_score": calculated_score,
            "credit_tier": credit_tier,
            "credit_score_breakdown": {
                "base_score": 350,  # Updated
                "credit_history_score": int(history_score),
                "payment_history_score": int(payment_score),
                "credit_utilization_score": int(utilization_score),
                "inquiry_penalty": int(inquiry_penalty),
                "default_penalty": int(default_penalty)
            },
            "credit_score_factors": [
                f"Credit history: {history_months} months (+{int(history_score)} points)",
                f"Payment history: {on_time} on-time, {late} late ({payment_rate*100:.1f}% on-time, +{int(payment_score)} points)" if total_payments > 0 else "No payment history",
                f"Credit utilization: {utilization:.1f}% ({'Good' if utilization < 30 else 'High'}, {int(utilization_score):+d} points)",
                f"Recent inquiries: {inquiries} (-{int(inquiry_penalty)} points)",
                f"Defaults: {defaults}, Write-offs: {writeoffs} (-{int(default_penalty)} points)"
            ],
            "credit_score_rationale": f"Credit score of {calculated_score} ({credit_tier}) calculated using payment history ({payment_rate*100:.1f}% on-time), credit utilization ({utilization:.1f}%), and {history_months} months of credit history. {'Late payments detected.' if late > 0 else 'Perfect payment record.'}"
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
        conditional = False
        
        # Credit score threshold (more realistic)
        if credit_score < 550:
            rejection_reasons.append("Credit score below minimum threshold (550)")
            approved = False
        elif credit_score < 650:
            # Conditional approval for Fair/Poor credit (550-649)
            conditional = True
        
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
            if conditional:
                final_decision = "conditional"
                # Reduce approved amount for conditional cases
                approved_amount = loan_requested * 0.85  # 85% of requested
            else:
                final_decision = "approved"
                approved_amount = loan_requested
            
            # Realistic interest rates based on credit tier (Indian market)
            if credit_score >= 750:
                interest_rate = 8.5  # Excellent credit
            elif credit_score >= 700:
                interest_rate = 9.5  # Very good credit
            elif credit_score >= 650:
                interest_rate = 11.0  # Good credit
            elif credit_score >= 600:
                interest_rate = 13.0  # Fair credit
            elif credit_score >= 550:
                interest_rate = 15.5  # Poor credit - conditional approval
            else:
                interest_rate = 18.0  # Very poor - shouldn't reach here
            
            # Adjust for self-employed (slightly higher risk)
            if employment_status == "Self-employed":
                interest_rate += 0.5
            
            conditions = []
            if conditional:
                conditions.append(f"Approved amount reduced to ₹{approved_amount:,.0f} (85% of requested)")
                conditions.append("Requires co-applicant or additional collateral")
                conditions.append("Higher interest rate due to credit score below 650")
            
            conditions.extend([
                "Income verification required",
                "Valid identity documents required",
                "Bank statements for last 6 months required"
            ])
            
            decision_rationale = f"Application {'conditionally approved' if conditional else 'approved'} based on credit score ({credit_score}), income (₹{monthly_income:.0f}/month), and DTI ratio ({dti_ratio:.1%})"
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
