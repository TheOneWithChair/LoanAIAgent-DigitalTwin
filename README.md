# 🏦 Loan AI Agent - Digital Twin# Loan Processing AI Agent - Digital Twin

An intelligent loan processing system powered by **LangGraph AI agents** that automates credit scoring, risk assessment, and loan decision-making.A full-stack loan processing application with AI-powered evaluation capabilities.

---## Project Structure

## 🌟 Features```

LoanAIAgent-DigitalTwin/

### 🤖 Multi-Agent AI System├── backend/ # FastAPI backend server

- **Credit Scoring Agent**: Analyzes credit history, payment patterns, and credit utilization│ ├── app/

- **Loan Decision Agent**: Makes approval decisions based on DTI, credit score, and risk factors│ │ ├── **init**.py

- **Verification Agent**: Validates employment, income, and identity documentation│ │ ├── main.py # FastAPI application and endpoints

- **Risk Monitoring Agent**: Continuous risk assessment and fraud detection│ │ └── schemas.py # Pydantic models for validation

│ ├── requirements.txt # Python dependencies

### 🏗️ Modern Architecture│ ├── .env.example # Environment variables template

- **LangGraph Orchestration**: Sequential agent workflow with state management│ ├── start_server.bat # Windows startup script

- **Async Database**: PostgreSQL (Neon) with SQLAlchemy async ORM│ └── README.md # Backend documentation

- **RESTful API**: FastAPI with automatic OpenAPI documentation│

- **Type Safety**: Pydantic models throughout the stack└── frontend/ # Next.js frontend application

- **Responsive UI**: Next.js 15 with Tailwind CSS ├── src/

  │ └── app/

### 📊 Key Capabilities │ ├── page.tsx # Home/landing page

- Real-time loan application processing │ ├── application/

- Comprehensive credit profile analysis │ │ └── page.tsx # Loan application form

- Employment and income verification │ ├── layout.tsx # Root layout

- Automated risk assessment │ └── globals.css # Global styles

- Agent execution logging and monitoring ├── package.json

- Database persistence with audit trail └── next.config.ts

```

---

## Features

## 🏛️ System Architecture

### Frontend (Next.js)

```

┌──────────────────────────────────────────────────────────────┐- ✅ Modern, responsive UI with Tailwind CSS

│ Frontend (Next.js) │- ✅ Comprehensive loan application form

│ ┌────────────────────────────────────────────────────────┐ │- ✅ Real-time form validation

│ │ Loan Application Form │ │- ✅ Loading states and error handling

│ │ • Personal Information • Credit Profile │ │- ✅ Success/error notifications

│ │ • Employment Details • Loan Requirements │ │- ✅ TypeScript for type safety

│ └────────────────────────────────────────────────────────┘ │

└────────────────────────┬─────────────────────────────────────┘### Backend (FastAPI)

                         │ HTTP POST

                         ▼- ✅ RESTful API endpoints

┌──────────────────────────────────────────────────────────────┐- ✅ Pydantic schema validation

│ Backend (FastAPI) │- ✅ CORS enabled for frontend communication

│ ┌────────────────────────────────────────────────────────┐ │- ✅ Comprehensive error handling

│ │ POST /submit_loan_application │ │- ✅ Business rule validation

│ │ 1. Validate with Pydantic │ │- ✅ Auto-generated API documentation (Swagger/ReDoc)

│ │ 2. Save to database │ │- ✅ Structured logging

│ │ 3. Call LangGraph orchestrator │ │

│ │ 4. Update with agent results │ │## Getting Started

│ └────────────────────────────────────────────────────────┘ │

└────────────────────────┬─────────────────────────────────────┘### Prerequisites

                         │

                         ▼- **Node.js** 18+ (for frontend)

┌──────────────────────────────────────────────────────────────┐- **Python** 3.11+ (for backend)

│ LangGraph Agent Orchestrator │- **npm** or **yarn** (for frontend package management)

│ │- **pip** (for Python package management)

│ ┌──────────────────┐ ┌──────────────────┐ │

│ │ Credit Scoring │──────▶│ Loan Decision │ │### Backend Setup

│ │ Agent │ │ Agent │ │

│ └──────────────────┘ └──────────────────┘ │1. Navigate to the backend directory:

│ │ │ │

│ ▼ ▼ │ ```bash

│ ┌──────────────────┐ ┌──────────────────┐ │ cd backend

│ │ Verification │──────▶│ Risk Monitoring │ │ ```

│ │ Agent │ │ Agent │ │

│ └──────────────────┘ └──────────────────┘ │2. Create a virtual environment:

│ │ │

└─────────────────────────────────────┼─────────────────────────┘ ```bash

                                      ▼   python -m venv venv

                    ┌──────────────────────────────┐   ```

                    │   PostgreSQL (Neon DB)       │

                    │  • loan_applications         │3. Activate the virtual environment:

                    │  • agent_execution_logs      │

                    └──────────────────────────────┘   ```bash

````# Windows (cmd)

   venv\Scripts\activate.bat

---

   # Windows (PowerShell)

## 📁 Project Structure   venv\Scripts\Activate.ps1



```   # Linux/Mac

LoanAIAgent-DigitalTwin/   source venv/bin/activate

│   ```

├── frontend/                    # Next.js 15 Frontend

│   ├── src/4. Install dependencies:

│   │   └── app/

│   │       ├── layout.tsx       # Root layout   ```bash

│   │       ├── page.tsx         # Landing page   pip install -r requirements.txt

│   │       └── application/   ```

│   │           └── page.tsx     # Loan application form

│   ├── package.json5. Start the server:

│   └── tailwind.config.ts

│   ```bash

├── backend/                     # FastAPI Backend   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

│   ├── app/   ```

│   │   ├── main.py             # FastAPI app entry point

│   │   ├── schemas.py          # Pydantic models   Or use the provided script (Windows):

│   │   ├── config.py           # Settings management

│   │   ├── database.py         # Async SQLAlchemy setup   ```bash

│   │   ├── models.py           # ORM models   start_server.bat

│   │   ├── orchestrator.py     # LangGraph workflow   ```

│   │   └── agent_state.py      # State definitions

│   │The backend will be available at:

│   ├── setup_database.py       # DB initialization script

│   ├── test_api.ps1            # PowerShell API test- **API**: http://localhost:8000

│   ├── requirements-agents.txt # Python dependencies- **API Docs (Swagger)**: http://localhost:8000/docs

│   ├── .env.example            # Environment template- **ReDoc**: http://localhost:8000/redoc

│   └── AGENTS_README.md        # Agent documentation

│### Frontend Setup

├── DEPLOYMENT.md               # Deployment guide

└── README.md                   # This file1. Navigate to the frontend directory:

````

```bash

---   cd frontend

```

## 🚀 Quick Start

2. Install dependencies:

### Prerequisites

````bash

- Python 3.10+   npm install

- Node.js 18+   ```

- PostgreSQL (or [Neon](https://neon.tech) account)

3. Start the development server:

### 1. Clone Repository   ```bash

npm run dev

```bash   ```

git clone <repository-url>

cd LoanAIAgent-DigitalTwinThe frontend will be available at: http://localhost:3000

````

## API Endpoints

### 2. Setup Backend

### `POST /submit_loan_application`

```````bash

cd backendSubmit a new loan application.



# Create virtual environment**Request Body:**

python -m venv venv

.\venv\Scripts\activate  # Windows```json

source venv/bin/activate # Mac/Linux{

  "applicant_id": "APP001",

# Install dependencies  "full_name": "John Doe",

pip install -r requirements-agents.txt  "date_of_birth": "1990-01-15",

  "phone_number": "+1-555-0100",

# Configure environment  "email": "john.doe@example.com",

cp .env.example .env  "address": "123 Main St, New York, NY 10001",

# Edit .env with your DATABASE_URL and OPENAI_API_KEY  "credit_history_length_months": 60,

  "number_of_credit_accounts": 5,

# Initialize database  "credit_mix": {

python setup_database.py    "secured_loans": 1,

    "unsecured_loans": 4

# Start server  },

python -m uvicorn app.main:app --reload  "credit_utilization_percent": 35.5,

```  "recent_credit_inquiries_6m": 2,

  "repayment_history": {

Backend runs at: **http://localhost:8000**    "on_time_payments": 48,

    "late_payments": 2,

### 3. Setup Frontend    "defaults": 0,

    "write_offs": 0

```bash  },

cd frontend  "employment_status": "Employed",

  "employment_duration_months": 36,

# Install dependencies  "monthly_income": 5000.0,

npm install  "income_verified": true,

  "loan_amount_requested": 50000.0,

# Start development server  "loan_purpose": "home",

npm run dev  "loan_tenure_months": 60,

```  "loan_to_value_ratio_percent": 80.0

}

Frontend runs at: **http://localhost:3000**```



---**Response:**



## 🔧 Configuration```json

{

### Backend Environment Variables  "status": "success",

  "message": "Loan application submitted successfully and is being processed",

Create `backend/.env`:  "application_id": "LA-20251111-ABC123",

  "applicant_id": "APP001"

```env}

# Database (Neon)```

DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech/db?sslmode=require

### `GET /`

# AI APIs

OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxHealth check and API information.

ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx  # Optional

### `GET /health`

# API Configuration

CORS_ORIGINS=["http://localhost:3000"]Simple health check endpoint.



# Business Rules## Testing

MAX_DTI_RATIO=0.50

MIN_CREDIT_SCORE_FOR_APPROVAL=680### Test with cURL

AGENT_TIMEOUT_SECONDS=30

``````bash

curl -X POST "http://localhost:8000/submit_loan_application" \

### Frontend Environment Variables  -H "Content-Type: application/json" \

  -d @backend/test_application.json

Create `frontend/.env.local`:```



```env### Test with the Frontend

NEXT_PUBLIC_API_URL=http://localhost:8000

```1. Start both backend and frontend servers

2. Navigate to http://localhost:3000

---3. Click "Apply Now"

4. Fill out the loan application form

## 📊 Database Schema5. Submit and check the response



### `loan_applications` Table## Business Rules



| Column | Type | Description |The backend validates the following business rules:

|--------|------|-------------|

| id | UUID | Primary key |- Income verification required for loans > $100,000

| application_id | VARCHAR(50) | Business ID (LA-YYYYMMDD-XXXXX) |- Employment required for loans > $10,000 (if unemployed)

| status | VARCHAR(50) | processing_started, completed, failed |- Debt-to-Income ratio warnings

| applicant_data | JSONB | Full application data |- High credit utilization warnings (>90%)

| credit_score_result | JSONB | Credit scoring agent output |- Multiple credit inquiry warnings (>6 in 6 months)

| loan_decision_result | JSONB | Loan decision agent output |- Defaults and write-offs logging

| verification_result | JSONB | Verification agent output |

| risk_monitoring_result | JSONB | Risk monitoring agent output |## Technology Stack

| final_decision | VARCHAR(50) | approved, denied, review_required |

| approved_amount | DECIMAL(12,2) | Approved loan amount |### Frontend

| interest_rate | DECIMAL(5,2) | Annual interest rate |

| created_at | TIMESTAMP | Record creation time |- **Next.js 15** - React framework

| updated_at | TIMESTAMP | Last update time |- **React 19** - UI library

- **TypeScript** - Type safety

### `agent_execution_logs` Table- **Tailwind CSS** - Styling



| Column | Type | Description |### Backend

|--------|------|-------------|

| id | UUID | Primary key |- **FastAPI** - Modern Python web framework

| application_id | VARCHAR(50) | Links to loan application |- **Pydantic** - Data validation

| agent_name | VARCHAR(100) | Agent identifier |- **Uvicorn** - ASGI server

| status | VARCHAR(50) | success, error, timeout |- **Python 3.11+** - Programming language

| execution_time_seconds | FLOAT | Duration |

| error_message | TEXT | Error details (if any) |## Development

| created_at | TIMESTAMP | Execution time |

### Frontend Development

---

```bash

## 🤖 Agent Workflowcd frontend

npm run dev      # Start development server

### 1. Credit Scoring Agentnpm run build    # Build for production

```npm run start    # Start production server

Input:  Credit history, payment patterns, utilizationnpm run lint     # Run linter

Output: Credit score (300-850), risk factors, recommendations```

```````

### Backend Development

### 2. Loan Decision Agent

````bash

Input:  Credit score, DTI ratio, loan amount, incomecd backend

Output: Decision (approved/denied), approved amount, interest rate# With virtual environment activated

```uvicorn app.main:app --reload  # Start with auto-reload

python -m pytest               # Run tests (when added)

### 3. Verification Agent```

```

Input:  Employment status, income, SSN, documents## Future Enhancements

Output: Verification status, confidence level, flagged items

```- [ ] Database integration (PostgreSQL/MongoDB)

- [ ] AI agent for credit risk assessment

### 4. Risk Monitoring Agent- [ ] User authentication and authorization

```- [ ] Application status tracking

Input:  All previous agent results- [ ] Email/SMS notifications

Output: Risk level (low/medium/high), fraud indicators, monitoring plan- [ ] Admin dashboard

```- [ ] Payment processing integration

- [ ] Document upload functionality

---- [ ] Credit score API integration

- [ ] Machine learning model for loan approval

## 🧪 Testing

## Contributing

### Test Backend API

1. Fork the repository

```bash2. Create a feature branch

# Using PowerShell (Windows)3. Make your changes

cd backend4. Test thoroughly

powershell -File test_api.ps15. Submit a pull request



# Using curl (Mac/Linux)## License

curl -X POST http://localhost:8000/submit_loan_application \

  -H "Content-Type: application/json" \[Your License Here]

  -d @test_payload.json

```## Support



### Test FrontendFor questions or issues, please open an issue on the GitHub repository.


1. Navigate to http://localhost:3000
2. Click "Apply for Loan"
3. Fill out the form with test data
4. Submit and verify success

### View API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📚 API Reference

### POST `/submit_loan_application`

Submit a new loan application for AI processing.

**Response:**
```json
{
  "application_id": "LA-20251111-ABC123",
  "status": "completed",
  "message": "Application processed successfully",
  "final_decision": "approved",
  "calculated_credit_score": 720,
  "risk_level": "medium",
  "approved_amount": 45000.00,
  "interest_rate": 5.25,
  "processing_time_seconds": 2.47
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## 🔐 Security

- ✅ HTTPS/TLS encryption in production
- ✅ Environment-based configuration
- ✅ Input validation with Pydantic
- ✅ SQL injection protection (ORM)
- ✅ CORS configuration
- ✅ Audit logging via agent_execution_logs

---

## 🛠️ Tech Stack

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **React 19**: UI library

### Backend
- **FastAPI 0.115**: Modern async Python framework
- **Pydantic 2.9**: Data validation
- **SQLAlchemy 2.0**: Async ORM
- **LangGraph 0.2**: AI agent orchestration
- **LangChain 0.3**: AI framework integration

### Database
- **PostgreSQL**: Relational database
- **Neon**: Serverless Postgres
- **asyncpg**: Async database driver

### AI/ML
- **OpenAI API**: GPT models
- **Anthropic API**: Claude models (optional)
- **LangGraph**: Multi-agent workflow management

---

## 📖 Documentation

- **[AGENTS_README.md](backend/AGENTS_README.md)**: Detailed agent architecture and workflow
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete deployment guide with cloud platforms
- **API Docs**: http://localhost:8000/docs (when server is running)

---

## 🗺️ Roadmap

### Phase 1: Core Features ✅
- [x] Loan application form
- [x] FastAPI backend with validation
- [x] LangGraph agent orchestration
- [x] Database integration with Neon
- [x] Comprehensive documentation

### Phase 2: Enhanced AI 🚧
- [ ] Integrate real OpenAI/Claude models
- [ ] Add document OCR for verification
- [ ] Implement fraud detection ML model
- [ ] Add explainable AI for loan decisions

### Phase 3: Advanced Features 📋
- [ ] Real-time application status tracking
- [ ] Email/SMS notifications
- [ ] Admin dashboard with analytics
- [ ] Credit bureau API integration
- [ ] Document upload functionality

### Phase 4: Enterprise 📋
- [ ] Role-based access control (RBAC)
- [ ] Multi-tenant support
- [ ] Compliance reporting (FCRA, ECOA)
- [ ] Mobile app (React Native)
- [ ] White-label customization

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **LangChain Team**: For the amazing LangGraph framework
- **FastAPI**: For the modern Python web framework
- **Neon**: For serverless PostgreSQL hosting
- **Vercel**: For Next.js and deployment platform

---

## 📞 Support

- **Documentation**: See `AGENTS_README.md` and `DEPLOYMENT.md`
- **API Docs**: http://localhost:8000/docs
- **Issues**: Open an issue on GitHub for bug reports or feature requests

---

<div align="center">

**Built with ❤️ using LangGraph, FastAPI, and Next.js**

[⬆ Back to Top](#-loan-ai-agent---digital-twin)

</div>
````
