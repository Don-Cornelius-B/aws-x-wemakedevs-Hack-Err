from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
import time
import uuid
import boto3
from app.services.auth_service import require_action
from app.services.opensearch_service import store_hazard_report, get_recent_hazards
from app.config import settings

router = APIRouter()
s3_client = boto3.client('s3', endpoint_url=settings.LOCALSTACK_ENDPOINT, region_name=settings.AWS_REGION)

@router.post("/upload")
async def upload_hazard(
    file: UploadFile = File(...),
    # Anyone authenticated (or mocked Citizen) can upload
    user: dict = Depends(require_action("SubmitHazardReport", "HazardReport"))
):
    try:
        report_id = f"rep-{uuid.uuid4().hex[:8]}"
        file_key = f"photos/{report_id}_{file.filename}"
        
        # In a real app, read file and upload to S3.
        # file_content = await file.read()
        # s3_client.put_object(Bucket="ner-hazard-uploads", Key=file_key, Body=file_content)
        
        # Here we mock the process to simulate the S3 upload and Lambda EXIF parsing
        # (Assuming the client already sent the metadata, or we create mock metadata for demo)
        report_data = {
            "report_id": report_id,
            "location": {"lat": 26.5, "lon": 92.5}, # Mocked location
            "reporter_role": user.get("role", "Citizen"),
            "fissure_depth_cm": 0.0,
            "soil_type": "unknown",
            "verified": False,
            "severity": 3,
            "photo_s3_key": file_key,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        store_hazard_report(report_data)
        return {"status": "success", "report_id": report_id, "data": report_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
def recent_hazards():
    return get_recent_hazards(limit=50)

@router.post("/verify/{report_id}")
def verify_hazard(report_id: str, user: dict = Depends(require_action("VerifyHazardReport", "HazardReport"))):
    # Mock verification
    # Would normally update OpenSearch document setting verified=True
    return {"status": "verified", "report_id": report_id, "verified_by": user.get("sub")}
