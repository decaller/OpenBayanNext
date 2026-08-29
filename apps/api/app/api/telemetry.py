from fastapi import APIRouter
from app.services.telemetry import telemetry_tracker

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

@router.get("/stats")
async def get_telemetry_stats():
    """Returns live analytical stats: page visits, query counts, and avg search latency."""
    return telemetry_tracker.get_stats()

@router.post("/visit")
async def record_page_visit():
    """Records a page visit."""
    telemetry_tracker.record_visit()
    return {"status": "ok", "visits": telemetry_tracker.page_visits}
