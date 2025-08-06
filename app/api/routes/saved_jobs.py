from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.db.records_handler import (
    save_application_record,
    load_application_records,
    mark_as_applied,
    list_sheet_names,
    load_sheet_data
)

router = APIRouter(prefix="/api")


# --------- Request Models ---------

class SaveJobRequest(BaseModel):
    job_info: dict
    fit_eval: dict
    email_cover: dict
    org_eval: Optional[dict] = None
    recruiters: Optional[List[str]] = None


class ApplyJobRequest(BaseModel):
    job_id: str


# --------- Routes ---------

@router.get("/saved-jobs")
def get_saved_jobs():
    """
    Fetch all saved job applications.
    """
    return load_application_records()


@router.post("/save-job")
def save_job(req: SaveJobRequest):
    """
    Save a new job application record to Excel.
    """
    save_application_record(
        job_info=req.job_info,
        fit_eval=req.fit_eval,
        email_gen=req.email_cover,
        org_eval=req.org_eval,
        recruiter_data=req.recruiters
    )
    return {"status": "saved"}


@router.post("/mark-applied")
def mark_job_applied(req: ApplyJobRequest):
    """
    Mark a saved job as applied.
    """
    success = mark_as_applied(req.job_id)
    return {"status": "ok" if success else "error"}

@router.get("/sheet-names")
def get_sheet_names():
    """
    Get the names of all sheets in the Excel database.
    """
    return {"sheet_names": list_sheet_names()}

@router.get("/sheet-data/{sheet_name}")
def get_sheet_data(sheet_name: str):
    """
    Load data from a specific sheet in the Excel database.
    """
    data = load_sheet_data(sheet_name)
    return {"data": data if data else []}