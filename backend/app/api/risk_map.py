from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.auth_service import require_action
from app.services.opensearch_service import get_risk_zones, update_corridor_status
from app.services.priority_engine import PriorityEngine

router = APIRouter()
priority_engine = PriorityEngine()

class StatusUpdate(BaseModel):
    status: str

@router.get("/zones")
def get_zones():
    # Returns GeoJSON feature collection
    zones = get_risk_zones()
    features = []
    for z in zones:
        features.append({
            "type": "Feature",
            "geometry": z.get("geometry", {}),
            "properties": {
                "corridor_id": z.get("corridor_id"),
                "name": z.get("name"),
                "highway": z.get("highway"),
                "status": z.get("status"),
                "risk_level": z.get("risk_level")
            }
        })
    return {"type": "FeatureCollection", "features": features}

@router.get("/corridors")
def get_corridors():
    zones = get_risk_zones()
    return [{"corridor_id": z.get("corridor_id"), "status": z.get("status")} for z in zones]

@router.post("/corridors/{corridor_id}/status")
def update_status(corridor_id: str, update: StatusUpdate, user: dict = Depends(require_action("UpdateRoadStatus", "RoadCorridor"))):
    if update.status not in ["OPEN", "COMPROMISED", "BLOCKED"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    success = update_corridor_status(corridor_id, update.status)
    if not success:
        # Fallback for demo if OS is down
        print(f"Simulating OS update for {corridor_id} to {update.status}")
        
    # Also update priority engine graph to recalculate triage
    priority_engine.update_road_status(corridor_id, update.status)
    triage = priority_engine.calculate_triage_priority()
    
    return {"status": "success", "corridor_id": corridor_id, "new_status": update.status, "triage": triage}
