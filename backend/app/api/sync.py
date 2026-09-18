from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.services.auth_service import require_action
from app.services.opensearch_service import store_hazard_report
import uuid
import time

router = APIRouter()

@router.post("/push")
def sync_push(reports: List[Dict[str, Any]], user: dict = Depends(require_action("SubmitHazardReport", "HazardReport"))):
    """
    Receives batched offline reports queued in client IndexedDB.
    """
    processed = 0
    for report in reports:
        report["report_id"] = report.get("report_id", f"rep-sync-{uuid.uuid4().hex[:8]}")
        report["reporter_role"] = user.get("role", "Citizen")
        report["verified"] = False
        if "timestamp" not in report:
            report["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            
        success = store_hazard_report(report)
        if success:
            processed += 1
            
    return {"status": "success", "synced_count": processed, "total_received": len(reports)}

@router.get("/pull")
def sync_pull(since: str = None):
    """
    Returns incremental updates since client's last sync timestamp.
    """
    # Mock response for demo
    return {
        "status": "success",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "new_reports": [],
        "updated_corridors": []
    }
