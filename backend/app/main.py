from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.opensearch_service import check_opensearch_health
from app.api import hazards, risk_map, sync

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Starting NER-Landslide-Guard FastAPI Backend...")
    is_healthy = check_opensearch_health()
    if not is_healthy:
        print("WARNING: OpenSearch is not reachable. Proceeding in degraded mode.")
    yield
    # Shutdown logic
    print("Shutting down backend...")

app = FastAPI(title="NER-Landslide-Guard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hazards.router, prefix="/api/hazards", tags=["Hazards"])
app.include_router(risk_map.router, prefix="/api/risk", tags=["Risk Map"])
app.include_router(sync.router, prefix="/api/sync", tags=["Offline Sync"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
