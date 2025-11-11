"use client";

import { useState } from "react";

export default function LoanApplicationPage() {
  const [formData, setFormData] = useState({
    // Personal Details
    fullName: "",
    dateOfBirth: "",
    phoneNumber: "",
    email: "",
    residentialAddress: "",

    // Credit Profile
    creditHistoryLength: "",
    numberOfCreditAccounts: "",
    securedLoansCount: "",
    unsecuredLoansCount: "",
    creditUtilization: "",
    hardInquiries: "",
    onTimePayments: "",
    latePayments: "",
    defaults: "",
    writtenOffLoans: "",

    // Loan Request Details
    loanAmount: "",
    loanPurpose: "",
    loanTenure: "",
    loanToValueRatio: "",

    // Employment and Income
    employmentStatus: "",
    employmentDuration: "",
    monthlyIncome: "",
    incomeVerified: "",

    // Additional Parameters
    bankLender: "",
    daysPastDue: "",
    existingDebts: "",
    riskNotes: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<{
    type: "success" | "error" | null;
    message: string;
    applicationId?: string;
  }>({ type: null, message: "" });

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus({ type: null, message: "" });

    try {
      // Generate a unique applicant ID
      const applicantId = `APP${Date.now()}`;

      // Transform form data to match backend schema
      const payload = {
        applicant_id: applicantId,
        full_name: formData.fullName,
        date_of_birth: formData.dateOfBirth,
        phone_number: formData.phoneNumber,
        email: formData.email,
        address: formData.residentialAddress,
        credit_history_length_months: parseInt(formData.creditHistoryLength),
        number_of_credit_accounts: parseInt(formData.numberOfCreditAccounts),
        credit_mix: {
          secured_loans: parseInt(formData.securedLoansCount),
          unsecured_loans: parseInt(formData.unsecuredLoansCount),
        },
        credit_utilization_percent: parseFloat(formData.creditUtilization),
        recent_credit_inquiries_6m: parseInt(formData.hardInquiries),
        repayment_history: {
          on_time_payments: parseInt(formData.onTimePayments),
          late_payments: parseInt(formData.latePayments),
          defaults: parseInt(formData.defaults),
          write_offs: parseInt(formData.writtenOffLoans),
        },
        employment_status: formData.employmentStatus,
        employment_duration_months: parseInt(formData.employmentDuration),
        monthly_income: parseFloat(formData.monthlyIncome),
        income_verified: formData.incomeVerified === "yes",
        loan_amount_requested: parseFloat(formData.loanAmount),
        loan_purpose: formData.loanPurpose,
        loan_tenure_months: parseInt(formData.loanTenure),
        loan_to_value_ratio_percent: formData.loanToValueRatio
          ? parseFloat(formData.loanToValueRatio)
          : undefined,
        bank_lender: formData.bankLender || undefined,
        days_past_due: formData.daysPastDue
          ? parseInt(formData.daysPastDue)
          : undefined,
        existing_debts: formData.existingDebts || undefined,
        risk_notes: formData.riskNotes || undefined,
      };

      console.log("Submitting application:", payload);

      // Submit to backend API
      const response = await fetch(
        "http://localhost:8000/submit_loan_application",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Failed to submit application");
      }

      // Success
      setSubmitStatus({
        type: "success",
        message: `Application submitted successfully! Your application ID is: ${data.application_id}`,
        applicationId: data.application_id,
      });

      // Reset form after 3 seconds
      setTimeout(() => {
        setFormData({
          fullName: "",
          dateOfBirth: "",
          phoneNumber: "",
          email: "",
          residentialAddress: "",
          creditHistoryLength: "",
          numberOfCreditAccounts: "",
          securedLoansCount: "",
          unsecuredLoansCount: "",
          creditUtilization: "",
          hardInquiries: "",
          onTimePayments: "",
          latePayments: "",
          defaults: "",
          writtenOffLoans: "",
          loanAmount: "",
          loanPurpose: "",
          loanTenure: "",
          loanToValueRatio: "",
          employmentStatus: "",
          employmentDuration: "",
          monthlyIncome: "",
          incomeVerified: "",
          bankLender: "",
          daysPastDue: "",
          existingDebts: "",
          riskNotes: "",
        });
        setSubmitStatus({ type: null, message: "" });
      }, 5000);
    } catch (error) {
      console.error("Error submitting application:", error);
      setSubmitStatus({
        type: "error",
        message:
          error instanceof Error
            ? error.message
            : "Failed to submit application. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Loan Application Form
            </h1>
            <p className="text-gray-600">
              Please fill out all required fields to process your loan
              application
            </p>
          </div>

          {/* Status Messages */}
          {submitStatus.type && (
            <div
              className={`mb-6 p-4 rounded-lg ${
                submitStatus.type === "success"
                  ? "bg-green-50 border border-green-200"
                  : "bg-red-50 border border-red-200"
              }`}
            >
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  {submitStatus.type === "success" ? (
                    <svg
                      className="h-6 w-6 text-green-600"
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
                  ) : (
                    <svg
                      className="h-6 w-6 text-red-600"
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
                  )}
                </div>
                <div className="ml-3">
                  <p
                    className={`text-sm font-medium ${
                      submitStatus.type === "success"
                        ? "text-green-800"
                        : "text-red-800"
                    }`}
                  >
                    {submitStatus.message}
                  </p>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Personal Details Section */}
            <section className="border-b pb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 text-sm">
                  1
                </span>
                Personal Details
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="fullName"
                    required
                    value={formData.fullName}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your full name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date of Birth <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    name="dateOfBirth"
                    required
                    value={formData.dateOfBirth}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="tel"
                    name="phoneNumber"
                    required
                    value={formData.phoneNumber}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="+1 (555) 000-0000"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="your.email@example.com"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Residential Address <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    name="residentialAddress"
                    required
                    value={formData.residentialAddress}
                    onChange={handleChange}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter your complete address"
                  />
                </div>
              </div>
            </section>

            {/* Credit Profile Section */}
            <section className="border-b pb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 text-sm">
                  2
                </span>
                Credit Profile
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Credit History Length (months){" "}
                    <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="creditHistoryLength"
                    required
                    min="0"
                    value={formData.creditHistoryLength}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 36"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Number of Credit Accounts{" "}
                    <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="numberOfCreditAccounts"
                    required
                    min="0"
                    value={formData.numberOfCreditAccounts}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Total loans + credit cards"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Secured Loans Count <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="securedLoansCount"
                    required
                    min="0"
                    value={formData.securedLoansCount}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Home, auto loans"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Unsecured Loans Count{" "}
                    <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="unsecuredLoansCount"
                    required
                    min="0"
                    value={formData.unsecuredLoansCount}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Personal loans, credit cards"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Credit Utilization (%){" "}
                    <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="creditUtilization"
                    required
                    min="0"
                    max="100"
                    value={formData.creditUtilization}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hard Credit Inquiries (last 12 months){" "}
                    <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="hardInquiries"
                    required
                    min="0"
                    value={formData.hardInquiries}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Number of inquiries"
                  />
                </div>

                <div className="md:col-span-2">
                  <h3 className="text-lg font-medium text-gray-700 mb-4 mt-2">
                    Repayment History
                  </h3>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    On-time Payments <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="onTimePayments"
                    required
                    min="0"
                    value={formData.onTimePayments}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Number of on-time payments"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Late Payments <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="latePayments"
                    required
                    min="0"
                    value={formData.latePayments}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Number of late payments"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Defaults <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="defaults"
                    required
                    min="0"
                    value={formData.defaults}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Number of defaults"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Written-off Loans <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="writtenOffLoans"
                    required
                    min="0"
                    value={formData.writtenOffLoans}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Number of written-off loans"
                  />
                </div>
              </div>
            </section>

            {/* Loan Request Details Section */}
            <section className="border-b pb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 text-sm">
                  3
                </span>
                Loan Request Details
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan Amount Requested ($){" "}
                    <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="loanAmount"
                    required
                    min="0"
                    step="0.01"
                    value={formData.loanAmount}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 50000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan Purpose <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="loanPurpose"
                    required
                    value={formData.loanPurpose}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select purpose</option>
                    <option value="personal">Personal</option>
                    <option value="home">Home</option>
                    <option value="business">Business</option>
                    <option value="auto">Auto</option>
                    <option value="education">Education</option>
                    <option value="medical">Medical</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan Tenure (months) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="loanTenure"
                    required
                    min="1"
                    value={formData.loanTenure}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 60 (5 years)"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Loan-to-Value Ratio (%){" "}
                    {formData.loanPurpose &&
                      ["home", "auto"].includes(formData.loanPurpose) && (
                        <span className="text-red-500">*</span>
                      )}
                  </label>
                  <input
                    type="number"
                    name="loanToValueRatio"
                    min="0"
                    max="100"
                    value={formData.loanToValueRatio}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="For secured loans only"
                  />
                </div>
              </div>
            </section>

            {/* Employment and Income Section */}
            <section className="border-b pb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 text-sm">
                  4
                </span>
                Employment and Income Information
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Employment Status <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="employmentStatus"
                    required
                    value={formData.employmentStatus}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select status</option>
                    <option value="Employed">Employed</option>
                    <option value="Self-employed">Self-employed</option>
                    <option value="Unemployed">Unemployed</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Employment Duration (months){" "}
                    <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="employmentDuration"
                    required
                    min="0"
                    value={formData.employmentDuration}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 24"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Income ($) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    name="monthlyIncome"
                    required
                    min="0"
                    step="0.01"
                    value={formData.monthlyIncome}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 5000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Income Verified <span className="text-red-500">*</span>
                  </label>
                  <select
                    name="incomeVerified"
                    required
                    value={formData.incomeVerified}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select option</option>
                    <option value="yes">Yes</option>
                    <option value="no">No</option>
                  </select>
                </div>
              </div>
            </section>

            {/* Additional Parameters Section */}
            <section className="pb-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                <span className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 text-sm">
                  5
                </span>
                Additional Parameters (Optional)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bank/Lender
                  </label>
                  <input
                    type="text"
                    name="bankLender"
                    value={formData.bankLender}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Name of bank or lender"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Days Past Due
                  </label>
                  <select
                    name="daysPastDue"
                    value={formData.daysPastDue}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select bucket</option>
                    <option value="0">0 days (Current)</option>
                    <option value="30">30 days</option>
                    <option value="60">60 days</option>
                    <option value="90+">90+ days</option>
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Existing Debts or Other Obligations
                  </label>
                  <textarea
                    name="existingDebts"
                    value={formData.existingDebts}
                    onChange={handleChange}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="List any existing debts, monthly payments, or financial obligations"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Risk Notes or Additional Comments
                  </label>
                  <textarea
                    name="riskNotes"
                    value={formData.riskNotes}
                    onChange={handleChange}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Any additional information or notes for review"
                  />
                </div>
              </div>
            </section>

            {/* Submit Button */}
            <div className="flex justify-center pt-6">
              <button
                type="submit"
                disabled={isSubmitting}
                className={`font-semibold py-3 px-12 rounded-lg shadow-lg transform transition focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                  isSubmitting
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700 text-white hover:scale-105"
                }`}
              >
                {isSubmitting ? (
                  <span className="flex items-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Submitting...
                  </span>
                ) : (
                  "Submit Application"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
