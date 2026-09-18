#!/bin/bash
# scripts/setup_localstack.sh
# Initializes LocalStack S3 and SQS primitives for NER-Landslide-Guard

echo "Initializing LocalStack resources..."

# Wait for LocalStack to be ready
until curl -s http://localhost:4566/_localstack/health | grep "\"s3\": \"\(available\|running\)\"" > /dev/null; do
  echo "Waiting for LocalStack S3..."
  sleep 2
done

echo "LocalStack S3 is ready. Creating bucket..."
awslocal s3 mb s3://ner-hazard-uploads || aws --endpoint-url=http://localhost:4566 s3 mb s3://ner-hazard-uploads

echo "LocalStack SQS is ready. Creating queue..."
awslocal sqs create-queue --queue-name ner-alert-notifications || aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name ner-alert-notifications

echo "Setup complete! Created s3://ner-hazard-uploads and SQS ner-alert-notifications."
