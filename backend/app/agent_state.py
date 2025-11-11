# LangGraph State Management for Loan Processing Orchestrator

from typing import TypedDict, Optional, Dict, Any, List
from datetime import datetime


class AgentResult(TypedDict):
    """Individual agent execution result"""
    agent_name: str
    status: str  # "success", "failed", "timeout"
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time: float
    timestamp: str


class LoanProcessingState(TypedDict):
    """
    State object that flows through the LangGraph workflow.
    Contains all data needed by agents and accumulates results.
    """
    # Application identifiers
    application_id: str
    applicant_id: str
    
    # Input application data
    application_data: Dict[str, Any]
    
    # Agent execution results
    credit_scoring_result: Optional[AgentResult]
    loan_decision_result: Optional[AgentResult]
    verification_result: Optional[AgentResult]
    risk_monitoring_result: Optional[AgentResult]
    
    # Aggregated outputs
    calculated_credit_score: Optional[int]
    final_decision: Optional[str]  # "approved", "rejected", "under_review"
    risk_level: Optional[str]  # "low", "medium", "high"
    approved_amount: Optional[float]
    interest_rate: Optional[float]
    rejection_reasons: Optional[List[str]]
    
    # Processing metadata
    workflow_status: str  # "pending", "in_progress", "completed", "failed"
    current_step: str
    errors: List[str]
    started_at: str
    completed_at: Optional[str]
    total_processing_time: Optional[float]


def create_initial_state(
    application_id: str,
    applicant_id: str,
    application_data: Dict[str, Any]
) -> LoanProcessingState:
    """
    Create initial state for LangGraph workflow.
    
    Args:
        application_id: Unique application identifier
        applicant_id: Applicant identifier
        application_data: Complete loan application data
        
    Returns:
        LoanProcessingState with initialized values
    """
    return LoanProcessingState(
        application_id=application_id,
        applicant_id=applicant_id,
        application_data=application_data,
        credit_scoring_result=None,
        loan_decision_result=None,
        verification_result=None,
        risk_monitoring_result=None,
        calculated_credit_score=None,
        final_decision=None,
        risk_level=None,
        approved_amount=None,
        interest_rate=None,
        rejection_reasons=None,
        workflow_status="pending",
        current_step="initialized",
        errors=[],
        started_at=datetime.now().isoformat(),
        completed_at=None,
        total_processing_time=None,
    )


def update_agent_result(
    state: LoanProcessingState,
    agent_name: str,
    result: AgentResult
) -> LoanProcessingState:
    """
    Update state with agent execution result.
    
    Args:
        state: Current workflow state
        agent_name: Name of the agent that executed
        result: Agent execution result
        
    Returns:
        Updated state
    """
    # Map agent name to state field
    result_field = f"{agent_name}_result"
    
    # Update the appropriate field
    if result_field in state:
        state[result_field] = result
    
    # Update current step
    state["current_step"] = agent_name
    
    # Add errors if any
    if result.get("status") == "failed" and result.get("error"):
        state["errors"].append(f"{agent_name}: {result['error']}")
    
    return state


def finalize_state(state: LoanProcessingState) -> LoanProcessingState:
    """
    Finalize state after all agents have executed.
    
    Args:
        state: Current workflow state
        
    Returns:
        Finalized state with completion metadata
    """
    state["completed_at"] = datetime.now().isoformat()
    state["workflow_status"] = "completed" if not state["errors"] else "failed"
    
    # Calculate total processing time
    if state["started_at"] and state["completed_at"]:
        start = datetime.fromisoformat(state["started_at"])
        end = datetime.fromisoformat(state["completed_at"])
        state["total_processing_time"] = (end - start).total_seconds()
    
    return state
