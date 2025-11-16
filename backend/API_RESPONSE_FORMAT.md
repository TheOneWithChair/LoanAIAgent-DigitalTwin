# Standard API Response Format

## All Standard Response Fields Implemented ✅

### 1. Core Response Fields (Always Present)

```json
{
  "status": "success", // success or error
  "message": "Short summary of result", // Human-readable message
  "application_id": "LA-20251116-A1B2C3D4", // Unique application ID
  "applicant_id": "APP001" // Applicant identifier
}
```

### 2. Decision Fields (Always Present)

```json
{
  "final_decision": "approved", // approved/rejected/conditional
  "calculated_credit_score": 750, // Score from 300-850
  "credit_tier": "Excellent", // Tier label
  "risk_level": "low" // low/medium/high
}
```

### 3. Financial Terms (Present if Approved/Conditional)

```json
{
  "approved_amount": 1200000.0, // May differ from requested
  "interest_rate": 9.5, // Interest rate in %
  "estimated_monthly_emi": 15234.5 // Monthly payment estimate
}
```

### 4. Decision Explanation (Context-dependent)

```json
{
  "decision_rationale": "Application approved based on excellent credit score...",
  "rejection_reasons": ["Credit score below minimum", "High DTI ratio"], // If rejected
  "conditions": ["Income verification required", "Collateral needed"] // If conditional
}
```

### 5. Agent Outputs (Detailed Breakdown)

```json
{
  "agent_outputs": {
    "credit_scoring": {
      "calculated_credit_score": 750,
      "credit_tier": "Excellent",
      "credit_score_breakdown": {
        "base_score": 390,
        "credit_history_score": 85,
        "payment_history_score": 235,
        "credit_utilization_score": 50,
        "inquiry_penalty": 6,
        "default_penalty": 0
      },
      "credit_score_factors": [
        "Credit history: 72 months (+85 points)",
        "Payment history: 70 on-time, 1 late (98.6% on-time, +229 points)"
      ],
      "credit_score_rationale": "Detailed explanation..."
    },
    "loan_decision": {
      "final_decision": "approved",
      "approved_amount": 1200000.0,
      "interest_rate": 9.5,
      "estimated_monthly_emi": 15234.5,
      "debt_to_income_ratio": 0.32,
      "conditions": ["Income verification required"],
      "decision_rationale": "Application approved based on..."
    },
    "verification": {
      "verification_status": "verified",
      "verified_fields": ["email", "phone", "income"],
      "pending_verifications": [],
      "verification_notes": "All documents verified"
    },
    "risk_monitoring": {
      "risk_level": "low",
      "risk_score": 15,
      "risk_factors": ["Stable employment", "Good payment history"],
      "monitoring_recommendations": ["Annual review recommended"]
    }
  }
}
```

### 6. Processing Metadata

```json
{
  "processing_time_seconds": 2.45,
  "workflow_status": "completed"
}
```

## Complete Example Response

### Approved Application:

```json
{
  "status": "success",
  "message": "Loan application approved for ₹1,200,000 at 9.5% interest rate",
  "application_id": "LA-20251116-A1B2C3D4",
  "applicant_id": "TEST001",
  "final_decision": "approved",
  "calculated_credit_score": 750,
  "credit_tier": "Excellent",
  "risk_level": "low",
  "approved_amount": 1200000.0,
  "interest_rate": 9.5,
  "estimated_monthly_emi": 15234.5,
  "decision_rationale": "Application approved based on excellent credit score (750), low DTI ratio (32%), and 6 years of credit history with 98.6% on-time payments",
  "rejection_reasons": null,
  "conditions": [
    "Income verification required",
    "Valid identity documents required",
    "Bank statements for last 6 months required"
  ],
  "agent_outputs": {
    "credit_scoring": {
      /* detailed breakdown */
    },
    "loan_decision": {
      /* detailed breakdown */
    },
    "verification": {
      /* detailed breakdown */
    },
    "risk_monitoring": {
      /* detailed breakdown */
    }
  },
  "processing_time_seconds": 2.45,
  "workflow_status": "completed"
}
```

### Rejected Application:

```json
{
  "status": "success",
  "message": "Loan application rejected. See rejection_reasons for details",
  "application_id": "LA-20251116-B2C3D4E5",
  "applicant_id": "TEST002",
  "final_decision": "rejected",
  "calculated_credit_score": 485,
  "credit_tier": "Very Poor",
  "risk_level": "high",
  "approved_amount": 0.0,
  "interest_rate": null,
  "estimated_monthly_emi": null,
  "decision_rationale": "Application rejected: Credit score below minimum threshold (550); High debt-to-income ratio (65%)",
  "rejection_reasons": [
    "Credit score below minimum threshold (550)",
    "High debt-to-income ratio (65%)"
  ],
  "conditions": null,
  "agent_outputs": {
    "credit_scoring": {
      /* detailed breakdown */
    },
    "loan_decision": {
      /* detailed breakdown */
    },
    "verification": {
      /* detailed breakdown */
    },
    "risk_monitoring": {
      /* detailed breakdown */
    }
  },
  "processing_time_seconds": 1.85,
  "workflow_status": "completed"
}
```

### Conditional Approval:

```json
{
  "status": "success",
  "message": "Loan application conditionally approved. See conditions for requirements",
  "application_id": "LA-20251116-C3D4E5F6",
  "applicant_id": "TEST003",
  "final_decision": "conditional",
  "calculated_credit_score": 620,
  "credit_tier": "Fair",
  "risk_level": "medium",
  "approved_amount": 425000.0,
  "interest_rate": 13.0,
  "estimated_monthly_emi": 9845.3,
  "decision_rationale": "Application conditionally approved based on credit score (620), income (₹55,000/month), and DTI ratio (42%)",
  "rejection_reasons": null,
  "conditions": [
    "Approved amount reduced to ₹425,000 (85% of requested)",
    "Requires co-applicant or additional collateral",
    "Higher interest rate due to credit score below 650",
    "Income verification required",
    "Valid identity documents required",
    "Bank statements for last 6 months required"
  ],
  "agent_outputs": {
    "credit_scoring": {
      /* detailed breakdown */
    },
    "loan_decision": {
      /* detailed breakdown */
    },
    "verification": {
      /* detailed breakdown */
    },
    "risk_monitoring": {
      /* detailed breakdown */
    }
  },
  "processing_time_seconds": 2.15,
  "workflow_status": "completed"
}
```

## Testing

Run the comprehensive test to see all fields:

```bash
python test_comprehensive_response.py
```

## API Documentation

Full API documentation with all response fields is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Field Guarantees

### Always Present:

- `status`, `message`, `application_id`, `applicant_id`
- `final_decision`, `risk_level`
- `agent_outputs` (object with 4 agent results)
- `processing_time_seconds`, `workflow_status`

### Conditionally Present:

- `calculated_credit_score`, `credit_tier` (if scoring completed)
- `approved_amount`, `interest_rate`, `estimated_monthly_emi` (if approved/conditional)
- `decision_rationale` (if decision made)
- `rejection_reasons` (if rejected)
- `conditions` (if approved/conditional)

### Optional/Nullable:

All conditional fields can be `null` if not applicable.

---

**✅ All requested standard response fields are now implemented!**
