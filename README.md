# Loan Processing AI Agent - Digital Twin

A full-stack loan processing application with AI-powered evaluation capabilities.

## Project Structure

```
LoanAIAgent-DigitalTwin/
├── backend/                 # FastAPI backend server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application and endpoints
│   │   └── schemas.py      # Pydantic models for validation
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   ├── start_server.bat    # Windows startup script
│   └── README.md           # Backend documentation
│
└── frontend/               # Next.js frontend application
    ├── src/
    │   └── app/
    │       ├── page.tsx            # Home/landing page
    │       ├── application/
    │       │   └── page.tsx        # Loan application form
    │       ├── layout.tsx          # Root layout
    │       └── globals.css         # Global styles
    ├── package.json
    └── next.config.ts
```

## Features

### Frontend (Next.js)
- ✅ Modern, responsive UI with Tailwind CSS
- ✅ Comprehensive loan application form
- ✅ Real-time form validation
- ✅ Loading states and error handling
- ✅ Success/error notifications
- ✅ TypeScript for type safety

### Backend (FastAPI)
- ✅ RESTful API endpoints
- ✅ Pydantic schema validation
- ✅ CORS enabled for frontend communication
- ✅ Comprehensive error handling
- ✅ Business rule validation
- ✅ Auto-generated API documentation (Swagger/ReDoc)
- ✅ Structured logging

## Getting Started

### Prerequisites
- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **npm** or **yarn** (for frontend package management)
- **pip** (for Python package management)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # Windows (cmd)
   venv\Scripts\activate.bat
   
   # Windows (PowerShell)
   venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or use the provided script (Windows):
   ```bash
   start_server.bat
   ```

The backend will be available at:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at: http://localhost:3000

## API Endpoints

### `POST /submit_loan_application`
Submit a new loan application.

**Request Body:**
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
  "loan_to_value_ratio_percent": 80.0
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Loan application submitted successfully and is being processed",
  "application_id": "LA-20251111-ABC123",
  "applicant_id": "APP001"
}
```

### `GET /`
Health check and API information.

### `GET /health`
Simple health check endpoint.

## Testing

### Test with cURL
```bash
curl -X POST "http://localhost:8000/submit_loan_application" \
  -H "Content-Type: application/json" \
  -d @backend/test_application.json
```

### Test with the Frontend
1. Start both backend and frontend servers
2. Navigate to http://localhost:3000
3. Click "Apply Now"
4. Fill out the loan application form
5. Submit and check the response

## Business Rules

The backend validates the following business rules:
- Income verification required for loans > $100,000
- Employment required for loans > $10,000 (if unemployed)
- Debt-to-Income ratio warnings
- High credit utilization warnings (>90%)
- Multiple credit inquiry warnings (>6 in 6 months)
- Defaults and write-offs logging

## Technology Stack

### Frontend
- **Next.js 15** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Python 3.11+** - Programming language

## Development

### Frontend Development
```bash
cd frontend
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run linter
```

### Backend Development
```bash
cd backend
# With virtual environment activated
uvicorn app.main:app --reload  # Start with auto-reload
python -m pytest               # Run tests (when added)
```

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] AI agent for credit risk assessment
- [ ] User authentication and authorization
- [ ] Application status tracking
- [ ] Email/SMS notifications
- [ ] Admin dashboard
- [ ] Payment processing integration
- [ ] Document upload functionality
- [ ] Credit score API integration
- [ ] Machine learning model for loan approval

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Your License Here]

## Support

For questions or issues, please open an issue on the GitHub repository.
