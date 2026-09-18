#!/bin/bash
set -e

# Configuration
OS_URL="http://localhost:9200"
LS_URL="http://localhost:4566/_localstack/health"

echo "======================================================="
echo " NER Landslide Risk Monitoring & Early Warning System "
echo "======================================================="

# Step 1: Detect container engine and launch services
if command -v finch >/dev/null 2>&1; then
    echo "[1/5] Using Finch for local orchestration..."
    finch compose up -d
elif command -v docker >/dev/null 2>&1; then
    echo "[1/5] Using Docker for local orchestration..."
    docker-compose up -d
else
    echo "ERROR: Neither Finch nor Docker found. Please install an engine."
    exit 1
fi

# Step 2: Poll OpenSearch and LocalStack until healthy
echo "[2/5] Waiting for OpenSearch and LocalStack to spin up..."
until $(curl --output /dev/null --silent --head --fail "$OS_URL"); do
    printf '.'
    sleep 3
done
echo " OpenSearch is UP!"

until $(curl --output /dev/null --silent --fail "$LS_URL"); do
    printf '.'
    sleep 3
done
echo " LocalStack is UP!"

# Step 3: Setup LocalStack S3 and SQS
echo "[3/5] Provisioning local AWS resources via LocalStack..."
bash scripts/setup_localstack.sh

# Step 4: Seed OpenSearch Geospatial Data
echo "[4/5] Seeding OpenSearch with NER Geodata (NH-29, NH-10, EKH, Champhai)..."
# In a real environment, we'd run this inside a virtualenv or container
python3 opensearch/seed_ner_data.py || echo "Warning: Seed script failed (maybe python dependencies missing). Ensure opensearch-py is installed locally."

# Step 5: Backend & Frontend health checks
echo "[5/5] Checking Backend and Frontend health..."
until $(curl --output /dev/null --silent --head --fail "http://localhost:8000/health"); do
    printf '.'
    sleep 3
done
echo " Backend is UP!"

until $(curl --output /dev/null --silent --head --fail "http://localhost:3000"); do
    printf '.'
    sleep 3
done
echo " Frontend is UP!"

echo ""
echo "======================================================="
echo "                SYSTEM IS READY "
echo "======================================================="
echo "Frontend App:    http://localhost:3000"
echo "Backend API:     http://localhost:8000/docs"
echo "OpenSearch:      http://localhost:9200"
echo "LocalStack:      http://localhost:4566"
echo ""
echo "--- Demo Roles for Cedar ABAC ---"
echo "- Citizen"
echo "- FieldInspector"
echo "- DistrictOfficer"
echo "Select these directly in the UI via the top navigation dropdown."
echo "======================================================="
