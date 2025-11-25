// =====================================================
// FRONTEND INTEGRATION EXAMPLES
// Complete TypeScript/JavaScript code for consuming the API
// =====================================================

// =====================================================
// TYPE DEFINITIONS
// =====================================================

interface LoanApplicationRequest {
  applicant_id: string;
  full_name: string;
  email: string;
  phone_number: string;
  date_of_birth?: string; // YYYY-MM-DD format
  address?: string;
  loan_amount_requested: number;
  loan_purpose: string;
  loan_tenure_months: number;
  monthly_income: number;
  employment_status: string;
  employment_duration_months: number;
  credit_score?: number;
  additional_data?: Record<string, any>;
}

interface AgentResponse {
  id: string;
  agent_type: string;
  agent_name: string;
  response_data: Record<string, any>;
  confidence_score?: number;
  execution_time_ms?: number;
  status: string;
  created_at: string;
}

interface AnalyticsSnapshot {
  id: string;
  calculated_credit_score?: number;
  risk_score?: number;
  approval_probability?: number;
  recommended_amount?: number;
  recommended_interest_rate?: number;
  debt_to_income_ratio?: number;
  risk_factors?: string[];
  positive_factors?: string[];
  model_scores?: Record<string, any>;
  processing_time_seconds?: number;
  total_agents_executed: number;
  created_at: string;
}

interface LoanApplication {
  id: string;
  applicant_id: string;
  full_name: string;
  email: string;
  phone_number: string;
  loan_amount_requested: number;
  loan_purpose: string;
  loan_tenure_months: number;
  monthly_income: number;
  employment_status: string;
  status: string;
  final_decision?: string;
  approved_amount?: number;
  interest_rate?: number;
  created_at: string;
  processed_at?: string;
}

interface LoanApplicationResponse {
  status: string;
  message: string;
  application_id: string;
  current_status: string;
  loan_application: LoanApplication;
  agent_responses: AgentResponse[];
  analytics_snapshot?: AnalyticsSnapshot;
  processing_time_seconds: number;
}

interface LoanApplicationDetailResponse {
  status: string;
  loan_application: LoanApplication;
  agent_responses: AgentResponse[];
  analytics_snapshot?: AnalyticsSnapshot;
}

interface ApiError {
  detail: string;
}

// =====================================================
// OPTION 1: NATIVE FETCH API
// =====================================================

const API_BASE_URL = "http://localhost:8000";

/**
 * Submit a new loan application using fetch
 */
async function submitLoanApplication(
  applicationData: LoanApplicationRequest
): Promise<LoanApplicationResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/loan-applications`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(applicationData),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    const data: LoanApplicationResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Error submitting loan application:", error);
    throw error;
  }
}

/**
 * Fetch loan application details by UUID using fetch
 */
async function fetchLoanApplication(
  applicationId: string
): Promise<LoanApplicationDetailResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/loan-applications/${applicationId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    const data: LoanApplicationDetailResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching loan application:", error);
    throw error;
  }
}

// =====================================================
// OPTION 2: AXIOS
// =====================================================

import axios, { AxiosError } from "axios";

const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds
});

/**
 * Submit a new loan application using axios
 */
async function submitLoanApplicationAxios(
  applicationData: LoanApplicationRequest
): Promise<LoanApplicationResponse> {
  try {
    const response = await axiosClient.post<LoanApplicationResponse>(
      "/loan-applications",
      applicationData
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      console.error(
        "Axios error:",
        axiosError.response?.data?.detail || axiosError.message
      );
      throw new Error(
        axiosError.response?.data?.detail || "Failed to submit application"
      );
    }
    throw error;
  }
}

/**
 * Fetch loan application details by UUID using axios
 */
async function fetchLoanApplicationAxios(
  applicationId: string
): Promise<LoanApplicationDetailResponse> {
  try {
    const response = await axiosClient.get<LoanApplicationDetailResponse>(
      `/loan-applications/${applicationId}`
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;
      console.error(
        "Axios error:",
        axiosError.response?.data?.detail || axiosError.message
      );
      throw new Error(
        axiosError.response?.data?.detail || "Failed to fetch application"
      );
    }
    throw error;
  }
}

// =====================================================
// REACT COMPONENT EXAMPLE (with TypeScript)
// =====================================================

import React, { useState, FormEvent } from "react";

export default function LoanApplicationForm() {
  const [formData, setFormData] = useState<LoanApplicationRequest>({
    applicant_id: "",
    full_name: "",
    email: "",
    phone_number: "",
    date_of_birth: "",
    address: "",
    loan_amount_requested: 0,
    loan_purpose: "",
    loan_tenure_months: 0,
    monthly_income: 0,
    employment_status: "",
    employment_duration_months: 0,
    credit_score: undefined,
  });

  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<LoanApplicationResponse | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      // Submit the application
      const result = await submitLoanApplication(formData);
      setResponse(result);

      // Show success message
      alert(
        `Application submitted successfully! Application ID: ${result.application_id}`
      );

      // Optionally fetch full details
      const details = await fetchLoanApplication(result.application_id);
      console.log("Application details:", details);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name.includes("amount") ||
        name.includes("income") ||
        name.includes("months") ||
        name.includes("score")
          ? parseFloat(value) || 0
          : value,
    }));
  };

  return (
    <div className="loan-application-form">
      <h1>Loan Application</h1>

      <form onSubmit={handleSubmit}>
        {/* Applicant Information */}
        <section>
          <h2>Applicant Information</h2>

          <input
            type="text"
            name="applicant_id"
            placeholder="Applicant ID"
            value={formData.applicant_id}
            onChange={handleInputChange}
            required
          />

          <input
            type="text"
            name="full_name"
            placeholder="Full Name"
            value={formData.full_name}
            onChange={handleInputChange}
            required
          />

          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleInputChange}
            required
          />

          <input
            type="tel"
            name="phone_number"
            placeholder="Phone Number"
            value={formData.phone_number}
            onChange={handleInputChange}
            required
          />

          <input
            type="date"
            name="date_of_birth"
            placeholder="Date of Birth"
            value={formData.date_of_birth}
            onChange={handleInputChange}
          />

          <input
            type="text"
            name="address"
            placeholder="Address"
            value={formData.address}
            onChange={handleInputChange}
          />
        </section>

        {/* Loan Details */}
        <section>
          <h2>Loan Details</h2>

          <input
            type="number"
            name="loan_amount_requested"
            placeholder="Loan Amount Requested"
            value={formData.loan_amount_requested || ""}
            onChange={handleInputChange}
            required
            min="0"
            step="0.01"
          />

          <input
            type="text"
            name="loan_purpose"
            placeholder="Loan Purpose"
            value={formData.loan_purpose}
            onChange={handleInputChange}
            required
          />

          <input
            type="number"
            name="loan_tenure_months"
            placeholder="Loan Tenure (Months)"
            value={formData.loan_tenure_months || ""}
            onChange={handleInputChange}
            required
            min="1"
            max="360"
          />
        </section>

        {/* Financial Information */}
        <section>
          <h2>Financial Information</h2>

          <input
            type="number"
            name="monthly_income"
            placeholder="Monthly Income"
            value={formData.monthly_income || ""}
            onChange={handleInputChange}
            required
            min="0"
            step="0.01"
          />

          <select
            name="employment_status"
            value={formData.employment_status}
            onChange={handleInputChange}
            required
          >
            <option value="">Select Employment Status</option>
            <option value="employed">Employed</option>
            <option value="self_employed">Self-Employed</option>
            <option value="unemployed">Unemployed</option>
            <option value="retired">Retired</option>
          </select>

          <input
            type="number"
            name="employment_duration_months"
            placeholder="Employment Duration (Months)"
            value={formData.employment_duration_months || ""}
            onChange={handleInputChange}
            required
            min="0"
          />

          <input
            type="number"
            name="credit_score"
            placeholder="Credit Score (Optional)"
            value={formData.credit_score || ""}
            onChange={handleInputChange}
            min="300"
            max="850"
          />
        </section>

        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Submit Application"}
        </button>
      </form>

      {/* Display Response */}
      {response && (
        <div className="response-section">
          <h2>Application Result</h2>
          <div className="result-summary">
            <p>
              <strong>Application ID:</strong> {response.application_id}
            </p>
            <p>
              <strong>Status:</strong> {response.current_status}
            </p>
            <p>
              <strong>Decision:</strong>{" "}
              {response.loan_application.final_decision}
            </p>
            {response.loan_application.approved_amount && (
              <p>
                <strong>Approved Amount:</strong> $
                {response.loan_application.approved_amount.toFixed(2)}
              </p>
            )}
            {response.loan_application.interest_rate && (
              <p>
                <strong>Interest Rate:</strong>{" "}
                {response.loan_application.interest_rate}%
              </p>
            )}
            <p>
              <strong>Processing Time:</strong>{" "}
              {response.processing_time_seconds}s
            </p>
          </div>

          {/* Analytics */}
          {response.analytics_snapshot && (
            <div className="analytics-section">
              <h3>Analytics</h3>
              <p>
                <strong>Credit Score:</strong>{" "}
                {response.analytics_snapshot.calculated_credit_score}
              </p>
              <p>
                <strong>Risk Score:</strong>{" "}
                {response.analytics_snapshot.risk_score?.toFixed(2)}
              </p>
              <p>
                <strong>Approval Probability:</strong>{" "}
                {(
                  (response.analytics_snapshot.approval_probability || 0) * 100
                ).toFixed(1)}
                %
              </p>
              <p>
                <strong>DTI Ratio:</strong>{" "}
                {(
                  (response.analytics_snapshot.debt_to_income_ratio || 0) * 100
                ).toFixed(2)}
                %
              </p>

              {response.analytics_snapshot.risk_factors &&
                response.analytics_snapshot.risk_factors.length > 0 && (
                  <div>
                    <strong>Risk Factors:</strong>
                    <ul>
                      {response.analytics_snapshot.risk_factors.map(
                        (factor, idx) => (
                          <li key={idx}>{factor}</li>
                        )
                      )}
                    </ul>
                  </div>
                )}
            </div>
          )}

          {/* Agent Responses */}
          <div className="agents-section">
            <h3>Agent Responses</h3>
            {response.agent_responses.map((agent) => (
              <div key={agent.id} className="agent-response">
                <h4>{agent.agent_name}</h4>
                <p>
                  <strong>Type:</strong> {agent.agent_type}
                </p>
                <p>
                  <strong>Status:</strong> {agent.status}
                </p>
                <p>
                  <strong>Confidence:</strong>{" "}
                  {((agent.confidence_score || 0) * 100).toFixed(1)}%
                </p>
                <p>
                  <strong>Execution Time:</strong> {agent.execution_time_ms}ms
                </p>
                <details>
                  <summary>Response Data</summary>
                  <pre>{JSON.stringify(agent.response_data, null, 2)}</pre>
                </details>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Display Error */}
      {error && (
        <div className="error-section">
          <h2>Error</h2>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}

// =====================================================
// USAGE EXAMPLES
// =====================================================

// Example 1: Submit application and get immediate response
async function example1_SubmitApplication() {
  const applicationData: LoanApplicationRequest = {
    applicant_id: "APP12345",
    full_name: "John Doe",
    email: "john.doe@example.com",
    phone_number: "+1-555-0100",
    date_of_birth: "1985-03-15",
    address: "456 Elm Street, Los Angeles, CA 90001",
    loan_amount_requested: 75000,
    loan_purpose: "home_purchase",
    loan_tenure_months: 240,
    monthly_income: 8500,
    employment_status: "employed",
    employment_duration_months: 60,
    credit_score: 750,
  };

  try {
    const response = await submitLoanApplication(applicationData);

    console.log("Application submitted successfully!");
    console.log("Application ID:", response.application_id);
    console.log("Decision:", response.loan_application.final_decision);
    console.log("Approved Amount:", response.loan_application.approved_amount);
    console.log("Interest Rate:", response.loan_application.interest_rate);

    // Process agent responses
    response.agent_responses.forEach((agent) => {
      console.log(`${agent.agent_name}:`, agent.response_data);
    });

    // Check analytics
    if (response.analytics_snapshot) {
      console.log(
        "Credit Score:",
        response.analytics_snapshot.calculated_credit_score
      );
      console.log("Risk Score:", response.analytics_snapshot.risk_score);
      console.log(
        "Approval Probability:",
        response.analytics_snapshot.approval_probability
      );
    }

    return response;
  } catch (error) {
    console.error("Failed to submit application:", error);
    throw error;
  }
}

// Example 2: Fetch application details later
async function example2_FetchApplicationDetails(applicationId: string) {
  try {
    const details = await fetchLoanApplication(applicationId);

    console.log("Application Details:");
    console.log("Applicant:", details.loan_application.full_name);
    console.log("Status:", details.loan_application.status);
    console.log("Decision:", details.loan_application.final_decision);

    // Check if analytics exists
    if (details.analytics_snapshot) {
      console.log("Risk Assessment:", {
        credit_score: details.analytics_snapshot.calculated_credit_score,
        risk_score: details.analytics_snapshot.risk_score,
        risk_factors: details.analytics_snapshot.risk_factors,
      });
    }

    return details;
  } catch (error) {
    console.error("Failed to fetch application:", error);
    throw error;
  }
}

// Example 3: Submit and immediately fetch (two-step process)
async function example3_SubmitAndFetch() {
  // Step 1: Submit
  const submitResponse = await submitLoanApplication({
    applicant_id: "APP67890",
    full_name: "Jane Smith",
    email: "jane.smith@example.com",
    phone_number: "+1-555-0200",
    loan_amount_requested: 50000,
    loan_purpose: "debt_consolidation",
    loan_tenure_months: 60,
    monthly_income: 6500,
    employment_status: "employed",
    employment_duration_months: 36,
    credit_score: 680,
  });

  console.log("Submitted! Application ID:", submitResponse.application_id);

  // Step 2: Fetch full details
  const fullDetails = await fetchLoanApplication(submitResponse.application_id);

  console.log("Full Details Retrieved:", fullDetails);

  return fullDetails;
}

// Example 4: Error handling
async function example4_ErrorHandling() {
  try {
    // Attempt to fetch non-existent application
    await fetchLoanApplication("00000000-0000-0000-0000-000000000000");
  } catch (error) {
    if (error instanceof Error) {
      console.error("Expected error:", error.message);
      // Handle 404 or other errors appropriately
    }
  }

  try {
    // Submit invalid data
    await submitLoanApplication({
      applicant_id: "",
      full_name: "",
      email: "invalid-email",
      phone_number: "",
      loan_amount_requested: -1000, // Invalid negative amount
      loan_purpose: "",
      loan_tenure_months: 0,
      monthly_income: 0,
      employment_status: "",
      employment_duration_months: -5,
    });
  } catch (error) {
    if (error instanceof Error) {
      console.error("Validation error:", error.message);
      // Handle validation errors
    }
  }
}

// =====================================================
// EXPORT FUNCTIONS
// =====================================================

export {
  submitLoanApplication,
  fetchLoanApplication,
  submitLoanApplicationAxios,
  fetchLoanApplicationAxios,
  example1_SubmitApplication,
  example2_FetchApplicationDetails,
  example3_SubmitAndFetch,
  example4_ErrorHandling,
};

export type {
  LoanApplicationRequest,
  LoanApplicationResponse,
  LoanApplicationDetailResponse,
  AgentResponse,
  AnalyticsSnapshot,
  LoanApplication,
  ApiError,
};
