# Loan Processing AI Agent - Backend

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python -m app.main
```

The API will be available at:

- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST /submit_loan_application

Submit a new loan application with validated data.

**Request Body**: JSON object matching the LoanApplicationRequest schema

**Response**: LoanApplicationResponse with application ID and status

### GET /

Health check and API information

### GET /health

Simple health check endpoint

## Environment Variables

Create a `.env` file in the backend directory with:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database (for future use)
# DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Testing the API

### Using cURL

```bash
curl -X POST "http://localhost:8000/submit_loan_application" \
  -H "Content-Type: application/json" \
  -d @test_application.json
```

### Using Python requests

```python
import requests

data = {
    "applicant_id": "APP001",
    "full_name": "John Doe",
    "date_of_birth": "1990-01-15",
    # ... rest of the fields
}

response = requests.post(
    "http://localhost:8000/submit_loan_application",
    json=data
)
print(response.json())
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── schemas.py       # Pydantic models
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Next Steps

1. Add database integration (PostgreSQL/MongoDB)
2. Implement AI agent for credit risk assessment
3. Add authentication and authorization
4. Implement application status tracking
5. Add email/SMS notifications
6. Create admin dashboard endpoints
