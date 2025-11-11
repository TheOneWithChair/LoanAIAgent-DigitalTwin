# PowerShell script to test the Loan Application API

Write-Host "Testing Loan Application API..." -ForegroundColor Cyan
Write-Host ""

# Read the test data
$jsonData = Get-Content -Path "test_application.json" -Raw

# Make the API call
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/submit_loan_application" `
        -Method Post `
        -ContentType "application/json" `
        -Body $jsonData
    
    Write-Host "✅ Success!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Yellow
    $response | ConvertTo-Json -Depth 10
    Write-Host ""
    Write-Host "Application ID: $($response.application_id)" -ForegroundColor Green
    Write-Host "Applicant ID: $($response.applicant_id)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error!" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host ""
        Write-Host "Error Details:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message
    }
}
