# PowerShell test script for TechAtlas Backend endpoints

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing TechAtlas Backend Endpoints" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:5000"

# Test 1: Root endpoint
Write-Host "Test 1: GET / (Root endpoint)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "✓ Status: SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ Status: FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n----------------------------------------`n"

# Test 2: Health check
Write-Host "Test 2: GET /health (Health check)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "✓ Status: SUCCESS" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Status: FAILED" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n----------------------------------------`n"

# Test 3: Detect decision endpoint
Write-Host "Test 3: POST /detect-decision (Detect decision)" -ForegroundColor Yellow
try {
    $body = @{
        message = "We decided to migrate to PostgreSQL because the schema is stable"
        user = "priya@company.com"
        channel_id = "tech-team"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/detect-decision" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✓ Status: SUCCESS (200 OK)" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 3
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "✗ Status: FAILED (Status Code: $statusCode)" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details:" -ForegroundColor Red
        $_.ErrorDetails.Message
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing Complete" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
