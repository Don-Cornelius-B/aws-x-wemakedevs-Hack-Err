$ErrorActionPreference = "Stop"

$OS_URL = "http://localhost:9200"
$LS_URL = "http://localhost:4566/_localstack/health"

Write-Host "======================================================="
Write-Host " NER Landslide Risk Monitoring & Early Warning System "
Write-Host "======================================================="

# Step 1: Detect container engine and launch services
if (Get-Command "finch" -ErrorAction SilentlyContinue) {
    Write-Host "[1/5] Using Finch for local orchestration..."
    finch compose up -d
}
elseif (Get-Command "docker" -ErrorAction SilentlyContinue) {
    Write-Host "[1/5] Using Docker for local orchestration..."
    docker-compose up -d
}
else {
    Write-Host "ERROR: Neither Finch nor Docker found. Please install an engine." -ForegroundColor Red
    exit 1
}

# Step 2: Poll OpenSearch and LocalStack until healthy
Write-Host "[2/5] Waiting for OpenSearch and LocalStack to spin up..."
$os_ready = $false
while (-not $os_ready) {
    try {
        $res = Invoke-WebRequest -Uri $OS_URL -Method Head -UseBasicParsing -ErrorAction SilentlyContinue
        if ($res.StatusCode -eq 200) { $os_ready = $true }
    } catch {
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 3
    }
}
Write-Host " OpenSearch is UP!"

$ls_ready = $false
while (-not $ls_ready) {
    try {
        $res = Invoke-WebRequest -Uri $LS_URL -UseBasicParsing -ErrorAction SilentlyContinue
        if ($res.StatusCode -eq 200) { $ls_ready = $true }
    } catch {
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 3
    }
}
Write-Host " LocalStack is UP!"

# Step 3: Setup LocalStack S3 and SQS
Write-Host "[3/5] Provisioning local AWS resources via LocalStack..."
# Execute the bash script via WSL or Git Bash if available, or just run the aws cli commands directly.
# Since we know the commands from setup_localstack.sh, let's just run them:
aws --endpoint-url=http://localhost:4566 s3 mb s3://ner-hazard-uploads
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name ner-alert-notifications

# Step 4: Seed OpenSearch Geospatial Data
Write-Host "[4/5] Seeding OpenSearch with NER Geodata (NH-29, NH-10, EKH, Champhai)..."
try {
    python opensearch/seed_ner_data.py
} catch {
    Write-Host "Warning: Seed script failed (maybe python dependencies missing). Ensure opensearch-py is installed locally." -ForegroundColor Yellow
}

# Step 5: Backend & Frontend health checks
Write-Host "[5/5] Checking Backend and Frontend health..."
$backend_ready = $false
while (-not $backend_ready) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Head -UseBasicParsing -ErrorAction SilentlyContinue
        if ($res.StatusCode -eq 200) { $backend_ready = $true }
    } catch {
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 3
    }
}
Write-Host " Backend is UP!"

$frontend_ready = $false
while (-not $frontend_ready) {
    try {
        $res = Invoke-WebRequest -Uri "http://localhost:3000" -Method Head -UseBasicParsing -ErrorAction SilentlyContinue
        if ($res.StatusCode -eq 200) { $frontend_ready = $true }
    } catch {
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 3
    }
}
Write-Host " Frontend is UP!"

Write-Host ""
Write-Host "======================================================="
Write-Host "                SYSTEM IS READY "
Write-Host "======================================================="
Write-Host "Frontend App:    http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API:     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "OpenSearch:      http://localhost:9200"
Write-Host "LocalStack:      http://localhost:4566"
Write-Host ""
Write-Host "--- Demo Roles for Cedar ABAC ---"
Write-Host "- Citizen"
Write-Host "- FieldInspector"
Write-Host "- DistrictOfficer"
Write-Host "Select these directly in the UI via the top navigation dropdown."
Write-Host "======================================================="
