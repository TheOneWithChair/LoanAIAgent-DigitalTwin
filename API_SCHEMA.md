# API Schema Documentation

## Loan Application Request Schema

### Complete JSON Schema

```json
{
  "type": "object",
  "properties": {
    "applicant_id": { 
      "type": "string",
      "description": "Unique applicant identifier"
    },
    "full_name": { 
      "type": "string",
      "minLength": 1,
      "description": "Full name of applicant"
    },
    "date_of_birth": { 
      "type": "string", 
      "format": "date",
      "description": "Date of birth (YYYY-MM-DD)"
    },
    "phone_number": { 
      "type": "string",
      "description": "Contact phone number"
    },
    "email": { 
      "type": "string", 
      "format": "email",
      "description": "Email address"
    },
    "address": { 
      "type": "string",
      "description": "Residential address (optional)"
    },
    "credit_history_length_months": { 
      "type": "integer", 
      "minimum": 0,
      "description": "Credit history length in months"
    },
    "number_of_credit_accounts": { 
      "type": "integer", 
      "minimum": 0,
      "description": "Total number of credit accounts"
    },
    "credit_mix": {
      "type": "object",
      "properties": {
        "secured_loans": { 
          "type": "integer", 
          "minimum": 0,
          "description": "Number of secured loans (home, auto)"
        },
        "unsecured_loans": { 
          "type": "integer", 
          "minimum": 0,
          "description": "Number of unsecured loans (personal, credit cards)"
        }
      },
      "required": ["secured_loans", "unsecured_loans"]
    },
    "credit_utilization_percent": { 
      "type": "number", 
      "minimum": 0, 
      "maximum": 100,
      "description": "Credit utilization percentage"
    },
    "recent_credit_inquiries_6m": { 
      "type": "integer", 
      "minimum": 0,
      "description": "Number of hard inquiries in last 6 months"
    },
    "repayment_history": {
      "type": "object",
      "properties": {
        "on_time_payments": { 
          "type": "integer", 
          "minimum": 0,
          "description": "Number of on-time payments"
        },
        "late_payments": { 
          "type": "integer", 
          "minimum": 0,
          "description": "Number of late payments"
        },
        "defaults": { 
          "type": "integer", 
          "minimum": 0,
          "description": "Number of defaults"
        },
        "write_offs": { 
          "type": "integer", 
          "minimum": 0,
          "description": "Number of written-off loans"
        }
      },
      "required": ["on_time_payments", "late_payments", "defaults", "write_offs"]
    },
    "employment_status": { 
      "type": "string", 
      "enum": ["Employed", "Self-employed", "Unemployed"],
      "description": "Current employment status"
    },
    "employment_duration_months": { 
      "type": "integer", 
      "minimum": 0,
      "description": "Employment duration in months"
    },
    "monthly_income": { 
      "type": "number", 
      "minimum": 0,
      "description": "Monthly income in dollars"
    },
    "income_verified": { 
      "type": "boolean",
      "description": "Whether income is verified"
    },
    "loan_amount_requested": { 
      "type": "number", 
      "minimum": 0,
      "description": "Requested loan amount in dollars"
    },
    "loan_purpose": { 
      "type": "string",
      "description": "Purpose of the loan (personal, home, business, auto, etc.)"
    },
    "loan_tenure_months": { 
      "type": "integer", 
      "minimum": 1,
      "description": "Loan tenure in months"
    },
    "loan_to_value_ratio_percent": { 
      "type": "number", 
      "minimum": 0, 
      "maximum": 100,
      "description": "LTV ratio for secured loans (optional)"
    },
    "bank_lender": { 
      "type": "string",
      "description": "Bank or lender name (optional)"
    },
    "days_past_due": { 
      "type": "integer", 
      "minimum": 0,
      "description": "Days past due (optional)"
    },
    "existing_debts": { 
      "type": "string",
      "description": "Existing debts or obligations (optional)"
    },
    "risk_notes": { 
      "type": "string",
      "description": "Risk notes or additional comments (optional)"
    }
  },
  "required": [
    "applicant_id",
    "full_name",
    "date_of_birth",
    "phone_number",
    "email",
    "credit_history_length_months",
    "number_of_credit_accounts",
    "credit_mix",
    "credit_utilization_percent",
    "recent_credit_inquiries_6m",
    "repayment_history",
    "employment_status",
    "employment_duration_months",
    "monthly_income",
    "income_verified",
    "loan_amount_requested",
    "loan_purpose",
    "loan_tenure_months"
  ]
}
```

## Field Mapping: Frontend to Backend

| Frontend Field Name | Backend Field Name | Type | Required |
|---------------------|-------------------|------|----------|
| fullName | full_name | string | Yes |
| dateOfBirth | date_of_birth | date | Yes |
| phoneNumber | phone_number | string | Yes |
| email | email | email | Yes |
| residentialAddress | address | string | No |
| creditHistoryLength | credit_history_length_months | integer | Yes |
| numberOfCreditAccounts | number_of_credit_accounts | integer | Yes |
| securedLoansCount | credit_mix.secured_loans | integer | Yes |
| unsecuredLoansCount | credit_mix.unsecured_loans | integer | Yes |
| creditUtilization | credit_utilization_percent | float | Yes |
| hardInquiries | recent_credit_inquiries_6m | integer | Yes |
| onTimePayments | repayment_history.on_time_payments | integer | Yes |
| latePayments | repayment_history.late_payments | integer | Yes |
| defaults | repayment_history.defaults | integer | Yes |
| writtenOffLoans | repayment_history.write_offs | integer | Yes |
| employmentStatus | employment_status | enum | Yes |
| employmentDuration | employment_duration_months | integer | Yes |
| monthlyIncome | monthly_income | float | Yes |
| incomeVerified | income_verified | boolean | Yes |
| loanAmount | loan_amount_requested | float | Yes |
| loanPurpose | loan_purpose | string | Yes |
| loanTenure | loan_tenure_months | integer | Yes |
| loanToValueRatio | loan_to_value_ratio_percent | float | No |
| bankLender | bank_lender | string | No |
| daysPastDue | days_past_due | integer | No |
| existingDebts | existing_debts | string | No |
| riskNotes | risk_notes | string | No |

## Validation Rules

### Age Validation
- Applicant must be at least 18 years old
- Date of birth cannot be more than 100 years ago

### Business Rules
1. **Income Verification**: Required for loan amounts > $100,000
2. **Employment Requirement**: Employment required for loans > $10,000 (if unemployed)
3. **Credit Utilization Warning**: Logged if > 90%
4. **Credit Inquiries Warning**: Logged if > 6 in last 6 months
5. **Defaults Warning**: Logged if any defaults exist
6. **Write-offs Warning**: Logged if any write-offs exist

### Employment Status Values
- `"Employed"` - Full-time or part-time employment
- `"Self-employed"` - Self-employed or freelancer
- `"Unemployed"` - Currently unemployed

### Loan Purpose Values (Examples)
- `"personal"` - Personal loan
- `"home"` - Home/mortgage loan
- `"business"` - Business loan
- `"auto"` - Auto/vehicle loan
- `"education"` - Education loan
- `"medical"` - Medical loan
- `"other"` - Other purposes

## Response Schema

### Success Response

```json
{
  "status": "success",
  "message": "Loan application submitted successfully and is being processed",
  "application_id": "LA-20251111-ABC123",
  "applicant_id": "APP001"
}
```

### Error Response

```json
{
  "status": "error",
  "message": "Validation error",
  "details": {
    "field": "email",
    "error": "Invalid email format"
  }
}
```

## HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 201 | Created | Application submitted successfully |
| 400 | Bad Request | Validation error or business rule violation |
| 422 | Unprocessable Entity | Invalid data format |
| 500 | Internal Server Error | Server-side error |

## Example Requests

### Minimal Valid Request

```json
{
  "applicant_id": "APP123",
  "full_name": "Jane Smith",
  "date_of_birth": "1995-06-15",
  "phone_number": "+1-555-0200",
  "email": "jane.smith@example.com",
  "credit_history_length_months": 24,
  "number_of_credit_accounts": 2,
  "credit_mix": {
    "secured_loans": 0,
    "unsecured_loans": 2
  },
  "credit_utilization_percent": 30.0,
  "recent_credit_inquiries_6m": 1,
  "repayment_history": {
    "on_time_payments": 20,
    "late_payments": 0,
    "defaults": 0,
    "write_offs": 0
  },
  "employment_status": "Employed",
  "employment_duration_months": 24,
  "monthly_income": 4000.00,
  "income_verified": true,
  "loan_amount_requested": 10000.00,
  "loan_purpose": "personal",
  "loan_tenure_months": 36
}
```

### Complete Request (with Optional Fields)

```json
{
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
  "income_verified": true,
  "loan_amount_requested": 50000.00,
  "loan_purpose": "home",
  "loan_tenure_months": 60,
  "loan_to_value_ratio_percent": 80.0,
  "bank_lender": "First National Bank",
  "days_past_due": 0,
  "existing_debts": "Auto loan: $300/month, Credit cards: $200/month",
  "risk_notes": "Stable employment history, good credit score"
}
```

## Testing

### Using cURL (Windows CMD)

```cmd
curl -X POST "http://localhost:8000/submit_loan_application" ^
  -H "Content-Type: application/json" ^
  -d "{\"applicant_id\":\"APP001\",\"full_name\":\"John Doe\",\"date_of_birth\":\"1990-01-15\",\"phone_number\":\"+1-555-0100\",\"email\":\"john.doe@example.com\",\"credit_history_length_months\":60,\"number_of_credit_accounts\":5,\"credit_mix\":{\"secured_loans\":1,\"unsecured_loans\":4},\"credit_utilization_percent\":35.5,\"recent_credit_inquiries_6m\":2,\"repayment_history\":{\"on_time_payments\":48,\"late_payments\":2,\"defaults\":0,\"write_offs\":0},\"employment_status\":\"Employed\",\"employment_duration_months\":36,\"monthly_income\":5000.0,\"income_verified\":true,\"loan_amount_requested\":50000.0,\"loan_purpose\":\"home\",\"loan_tenure_months\":60}"
```

### Using Python

```python
import requests

payload = {
    "applicant_id": "APP001",
    "full_name": "John Doe",
    "date_of_birth": "1990-01-15",
    "phone_number": "+1-555-0100",
    "email": "john.doe@example.com",
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
    "loan_tenure_months": 60
}

response = requests.post(
    "http://localhost:8000/submit_loan_application",
    json=payload
)

print(response.json())
```

---

For interactive API testing, visit: http://localhost:8000/docs
