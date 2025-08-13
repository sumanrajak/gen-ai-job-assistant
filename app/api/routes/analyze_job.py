from fastapi import APIRouter
from pydantic import BaseModel
from app.api.master_orchestrator import run_all_agents_sync

router = APIRouter(prefix="/api")

class JDRequest(BaseModel):
    job_description: str

@router.post("/analyze-job")
async def analyze_job(request: JDRequest):
    result = run_all_agents_sync(request.job_description)
    return result
