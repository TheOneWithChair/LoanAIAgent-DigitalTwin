# Quick Start Guide - Loan Processing AI Agent

## ✅ Setup Complete!

Your full-stack loan processing application is now ready to use.

## 🚀 Starting the Application

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd g:\dbs\LoanAIAgent-DigitalTwin\backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Backend URLs:**

- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Step 2: Start the Frontend Server

Open another terminal and run:

```bash
cd g:\dbs\LoanAIAgent-DigitalTwin\frontend
npm run dev
```

**Frontend URL:**

- Application: http://localhost:3000

## 📝 Using the Application

1. **Open your browser** and go to http://localhost:3000
2. **Click "Apply Now"** on the home page
3. **Fill out the loan application form** with all required fields:
   - Personal Details
   - Credit Profile
   - Loan Request Details
   - Employment & Income Information
   - Additional Parameters (optional)
4. **Click "Submit Application"**
5. **View the success message** with your Application ID

## 🧪 Testing the API Directly

### Using cURL:

```bash
curl -X POST "http://localhost:8000/submit_loan_application" ^
  -H "Content-Type: application/json" ^
  -d @backend/test_application.json
```

### Using the API Docs:

1. Visit http://localhost:8000/docs
2. Click on `POST /submit_loan_application`
3. Click "Try it out"
4. Edit the request body or use the example
5. Click "Execute"
6. View the response

## 📋 What's Included

### Backend Features:

✅ FastAPI server with auto-reload
✅ Pydantic schema validation
✅ Business rule validation
✅ Error handling
✅ CORS enabled
✅ Auto-generated API documentation
✅ Logging

### Frontend Features:

✅ Modern Next.js application
✅ Responsive design (mobile-friendly)
✅ Form validation
✅ Loading states
✅ Success/error notifications
✅ TypeScript support

## 🔧 Troubleshooting

### Backend Issues:

**Issue:** ModuleNotFoundError
**Solution:** Make sure you're in the `backend` directory and the virtual environment is activated

**Issue:** Port 8000 already in use
**Solution:** Stop other processes using port 8000 or change the port:

```bash
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues:

**Issue:** Cannot connect to backend
**Solution:** Ensure the backend server is running on port 8000

**Issue:** Port 3000 already in use
**Solution:** Next.js will automatically suggest port 3001

## 📊 Sample Test Data

The backend includes a sample test file at `backend/test_application.json`:

- **Applicant:** John Doe
- **Loan Amount:** $50,000
- **Purpose:** Home
- **Tenure:** 60 months
- **Income:** $5,000/month

## 🎯 Next Steps

1. ✅ Both servers are running
2. ✅ Test the application form
3. ✅ View API documentation
4. 🔄 Customize business rules in `backend/app/main.py`
5. 🔄 Add database integration
6. 🔄 Implement AI credit scoring
7. 🔄 Add user authentication
8. 🔄 Create admin dashboard

## 📚 Additional Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Next.js Documentation:** https://nextjs.org/docs
- **Pydantic Documentation:** https://docs.pydantic.dev/
- **Tailwind CSS:** https://tailwindcss.com/docs

## 🆘 Need Help?

Check the detailed documentation in:

- `README.md` - Main project documentation
- `backend/README.md` - Backend-specific details
- API Docs at http://localhost:8000/docs

---

**Status:** ✅ Ready to use!
**Backend:** ✅ Running on port 8000
**Frontend:** ⏳ Ready to start on port 3000
