# PowerShell test script for TechAtlas Backend endpoints

Write-Host ""
Write-Host "========================================"
Write-Host "Testing TechAtlas Backend Endpoints"
Write-Host "========================================"
Write-Host ""

$baseUrl = "http://localhost:5000"

# Test 1: Root endpoint
Write-Host "Test 1: GET / (Root endpoint)"
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "[SUCCESS] Status: 200 OK" -ForegroundColor Green
    Write-Host "Response:"
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "[FAILED] Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "----------------------------------------"
Write-Host ""

# Test 2: Health check
Write-Host "Test 2: GET /health (Health check)"
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "[SUCCESS] Status: 200 OK" -ForegroundColor Green
    Write-Host "Response:"
    $response | ConvertTo-Json
} catch {
    Write-Host "[FAILED] Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "----------------------------------------"
Write-Host ""

# Test 3: Detect decision endpoint
Write-Host "Test 3: POST /detect-decision (Detect decision)"
try {
    $body = @{
        message = "We decided to migrate to PostgreSQL because the schema is stable"
        user = "priya@company.com"
        channel_id = "tech-team"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/detect-decision" -Method Post -Body $body -ContentType "application/json"
    Write-Host "[SUCCESS] Status: 200 OK" -ForegroundColor Green
    Write-Host "Response:"
    $response | ConvertTo-Json -Depth 3
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "[FAILED] Status Code: $statusCode" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details:"
        $_.ErrorDetails.Message
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "Testing Complete"
Write-Host "========================================"
Write-Host ""
