"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

interface AgentResponse {
  agent_name: string;
  status: string;
  output: any;
  execution_time_ms?: number;
  timestamp?: string;
}

interface ApplicationAnalytics {
  credit_score?: number;
  risk_level?: string;
  approval_probability?: number;
  debt_to_income_ratio?: number;
  recommended_interest_rate?: number;
  credit_tier?: string;
  risk_score?: number;
  monthly_payment?: number;
  recommended_amount?: number;
  loan_to_income_ratio?: number;
  credit_score_breakdown?: any;
  risk_factors?: any;
  approval_factors?: any;
}

interface ApplicationData {
  application_id: string;
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
  approved_loan_amount?: number;
  interest_rate?: number;
  monthly_payment?: number;
  decision_explanation?: string;
  created_at?: string;
  processed_at?: string;
  agent_responses?: AgentResponse[];
  analytics?: ApplicationAnalytics;
}

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const applicationId = searchParams.get("id");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [applicationData, setApplicationData] =
    useState<ApplicationData | null>(null);

  useEffect(() => {
    if (!applicationId) {
      setError("No application ID provided");
      setLoading(false);
      return;
    }

    fetchApplicationData();
  }, [applicationId]);

  const fetchApplicationData = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/application/${applicationId}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch application data");
      }

      const data = await response.json();
      // Extract the application object from the response
      setApplicationData(data.application || data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load application data"
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600 mb-4"></div>
          <p className="text-xl text-gray-700">
            Loading application results...
          </p>
        </div>
      </div>
    );
  }

  if (error || !applicationData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <svg
            className="h-16 w-16 text-red-500 mx-auto mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Error Loading Application
          </h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push("/application")}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Return to Application Form
          </button>
        </div>
      </div>
    );
  }

  const getDecisionColor = (decision?: string) => {
    if (!decision) return "gray";
    switch (decision.toLowerCase()) {
      case "approved":
        return "green";
      case "rejected":
        return "red";
      case "under_review":
      case "pending":
        return "yellow";
      default:
        return "gray";
    }
  };

  const getRiskColor = (risk?: string) => {
    if (!risk) return "gray";
    switch (risk.toLowerCase()) {
      case "low":
        return "green";
      case "medium":
        return "yellow";
      case "high":
      case "very_high":
        return "red";
      default:
        return "gray";
    }
  };

  const decisionColor = getDecisionColor(applicationData.final_decision);
  const riskColor = getRiskColor(applicationData.analytics?.risk_level);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Loan Application Results
              </h1>
              <p className="text-gray-600">
                Application ID:{" "}
                <span className="font-mono text-blue-600">
                  {applicationData.applicant_id}
                </span>
              </p>
            </div>
            <button
              onClick={() => router.push("/application")}
              className="text-blue-600 hover:text-blue-800 font-medium flex items-center"
            >
              <svg
                className="w-5 h-5 mr-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              New Application
            </button>
          </div>

          {/* Decision Status Banner */}
          <div
            className={`bg-${decisionColor}-50 border-2 border-${decisionColor}-200 rounded-xl p-6 mb-6`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h2
                  className="text-2xl font-bold mb-2"
                  style={{
                    color:
                      decisionColor === "green"
                        ? "#059669"
                        : decisionColor === "red"
                        ? "#DC2626"
                        : "#D97706",
                  }}
                >
                  {applicationData.final_decision
                    ? applicationData.final_decision.toUpperCase()
                    : "PENDING"}
                </h2>
                {applicationData.decision_explanation && (
                  <p className="text-gray-700">
                    {applicationData.decision_explanation}
                  </p>
                )}
              </div>
              <div className="text-right">
                {applicationData.approved_loan_amount && (
                  <div className="mb-2">
                    <p className="text-sm text-gray-600">Approved Amount</p>
                    <p className="text-2xl font-bold text-gray-900">
                      ₹{applicationData.approved_loan_amount.toLocaleString()}
                    </p>
                  </div>
                )}
                {applicationData.interest_rate && (
                  <div>
                    <p className="text-sm text-gray-600">Interest Rate</p>
                    <p className="text-xl font-bold text-gray-900">
                      {applicationData.interest_rate}%
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600 font-medium mb-1">
                Loan Amount
              </p>
              <p className="text-2xl font-bold text-blue-900">
                ₹{applicationData.loan_amount_requested.toLocaleString()}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-purple-600 font-medium mb-1">Tenure</p>
              <p className="text-2xl font-bold text-purple-900">
                {applicationData.loan_tenure_months} months
              </p>
            </div>
            <div className="bg-indigo-50 rounded-lg p-4">
              <p className="text-sm text-indigo-600 font-medium mb-1">
                Monthly Income
              </p>
              <p className="text-2xl font-bold text-indigo-900">
                ₹{applicationData.monthly_income.toLocaleString()}
              </p>
            </div>
            {applicationData.monthly_payment && (
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-green-600 font-medium mb-1">
                  Monthly Payment
                </p>
                <p className="text-2xl font-bold text-green-900">
                  ${applicationData.monthly_payment.toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Applicant Info & Analytics */}
          <div className="lg:col-span-1 space-y-6">
            {/* Applicant Information */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <svg
                  className="w-6 h-6 mr-2 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
                Applicant Information
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Full Name</p>
                  <p className="font-semibold text-gray-900">
                    {applicationData.full_name}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Applicant ID</p>
                  <p className="font-mono text-sm text-gray-900">
                    {applicationData.applicant_id}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="text-sm text-gray-900">
                    {applicationData.email}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Phone</p>
                  <p className="text-sm text-gray-900">
                    {applicationData.phone_number}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Employment Status</p>
                  <p className="font-semibold text-gray-900">
                    {applicationData.employment_status}
                  </p>
                </div>
              </div>
            </div>

            {/* Analytics Dashboard */}
            {applicationData.analytics && (
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <svg
                    className="w-6 h-6 mr-2 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                  Analytics
                </h3>
                <div className="space-y-4">
                  {applicationData.analytics.credit_score && (
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <p className="text-sm text-gray-600">Credit Score</p>
                        <p className="text-lg font-bold text-gray-900">
                          {applicationData.analytics.credit_score}
                        </p>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{
                            width: `${
                              (applicationData.analytics.credit_score / 850) *
                              100
                            }%`,
                          }}
                        ></div>
                      </div>
                      {applicationData.analytics.credit_tier && (
                        <p className="text-xs text-gray-500 mt-1">
                          {applicationData.analytics.credit_tier}
                        </p>
                      )}
                    </div>
                  )}

                  {applicationData.analytics.risk_level && (
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Risk Level</p>
                      <div
                        className={`inline-block px-3 py-1 rounded-full text-sm font-semibold bg-${riskColor}-100 text-${riskColor}-800`}
                      >
                        {applicationData.analytics.risk_level.toUpperCase()}
                      </div>
                      {applicationData.analytics.risk_score !== undefined && (
                        <p className="text-xs text-gray-500 mt-1">
                          Risk Score:{" "}
                          {applicationData.analytics.risk_score.toFixed(2)}
                        </p>
                      )}
                    </div>
                  )}

                  {applicationData.analytics.approval_probability !==
                    undefined && (
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <p className="text-sm text-gray-600">
                          Approval Probability
                        </p>
                        <p className="text-lg font-bold text-gray-900">
                          {(
                            applicationData.analytics.approval_probability * 100
                          ).toFixed(1)}
                          %
                        </p>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full transition-all"
                          style={{
                            width: `${
                              applicationData.analytics.approval_probability *
                              100
                            }%`,
                          }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {applicationData.analytics.debt_to_income_ratio !==
                    undefined && (
                    <div>
                      <div className="flex justify-between items-center">
                        <p className="text-sm text-gray-600">
                          Debt-to-Income Ratio
                        </p>
                        <p className="text-lg font-bold text-gray-900">
                          {(
                            applicationData.analytics.debt_to_income_ratio * 100
                          ).toFixed(2)}
                          %
                        </p>
                      </div>
                    </div>
                  )}

                  {applicationData.analytics.recommended_interest_rate && (
                    <div>
                      <div className="flex justify-between items-center">
                        <p className="text-sm text-gray-600">
                          Recommended Rate
                        </p>
                        <p className="text-lg font-bold text-gray-900">
                          {applicationData.analytics.recommended_interest_rate}%
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Agent Responses */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                <svg
                  className="w-6 h-6 mr-2 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
                AI Agent Processing Results
              </h3>

              {applicationData.agent_responses &&
              applicationData.agent_responses.length > 0 ? (
                <div className="space-y-4">
                  {applicationData.agent_responses.map((agent, index) => (
                    <div
                      key={index}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center">
                          <div className="bg-blue-100 rounded-full p-2 mr-3">
                            <svg
                              className="w-5 h-5 text-blue-600"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                              />
                            </svg>
                          </div>
                          <div>
                            <h4 className="font-bold text-gray-900">
                              {agent.agent_name}
                            </h4>
                            <p className="text-xs text-gray-500">
                              Status:{" "}
                              <span
                                className={`font-semibold ${
                                  agent.status === "SUCCESS"
                                    ? "text-green-600"
                                    : "text-red-600"
                                }`}
                              >
                                {agent.status}
                              </span>
                              {agent.execution_time_ms && (
                                <span className="ml-2">
                                  • {agent.execution_time_ms}ms
                                </span>
                              )}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-4">
                        <details className="cursor-pointer">
                          <summary className="font-medium text-gray-700 hover:text-gray-900">
                            View Agent Response
                          </summary>
                          <div className="mt-3 space-y-2">
                            {Object.entries(agent.output || {}).map(
                              ([key, value]) => (
                                <div key={key} className="text-sm">
                                  <span className="font-semibold text-gray-700">
                                    {key.replace(/_/g, " ").toUpperCase()}:{" "}
                                  </span>
                                  <span className="text-gray-600">
                                    {typeof value === "object"
                                      ? JSON.stringify(value, null, 2)
                                      : String(value)}
                                  </span>
                                </div>
                              )
                            )}
                          </div>
                        </details>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  No agent responses available
                </p>
              )}
            </div>

            {/* Timeline */}
            {(applicationData.created_at || applicationData.processed_at) && (
              <div className="bg-white rounded-2xl shadow-xl p-6 mt-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <svg
                    className="w-6 h-6 mr-2 text-blue-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Application Timeline
                </h3>
                <div className="space-y-3">
                  {applicationData.created_at && (
                    <div className="flex items-center">
                      <div className="bg-blue-100 rounded-full p-2 mr-3">
                        <svg
                          className="w-4 h-4 text-blue-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          Application Submitted
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(
                            applicationData.created_at
                          ).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}
                  {applicationData.processed_at && (
                    <div className="flex items-center">
                      <div className="bg-green-100 rounded-full p-2 mr-3">
                        <svg
                          className="w-4 h-4 text-green-600"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          Processing Completed
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(
                            applicationData.processed_at
                          ).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 flex justify-center space-x-4">
          <button
            onClick={() => window.print()}
            className="bg-white text-blue-600 border-2 border-blue-600 px-6 py-3 rounded-lg hover:bg-blue-50 transition font-semibold flex items-center"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
              />
            </svg>
            Print Results
          </button>
          <button
            onClick={() => router.push("/application")}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-semibold flex items-center"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Submit New Application
          </button>
        </div>
      </div>
    </div>
  );
}
