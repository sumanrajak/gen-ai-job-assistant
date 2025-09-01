# app/schemas/agent_outputs.py

from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# ---------------- Email/Cover Letter ----------------
class ColdEmail(BaseModel):
    subject: str
    body: str

class CoverLetter(BaseModel):
    body: str

class LinkedInMessage(BaseModel):
    body: str

class EmailCoverSchema(BaseModel):
    cold_email: ColdEmail = Field(..., alias="cold email")
    cover_letter: CoverLetter = Field(..., alias="cover letter")
    linkdin_networking_message_recruiter: LinkedInMessage
    linkdin_networking_message_referrer: LinkedInMessage


# ---------------- Fit Evaluator ----------------
class FitEvaluatorSchema(BaseModel):
    fit_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    summary: str


# ---------------- Get Recruiter ----------------
class GetRecruiterSchema(BaseModel):
    search_query: str


# ---------------- Job Info ----------------
class AdditionalInfo(BaseModel):
    Tech_Stack: List[str]
    Perks: List[str]

class JobInfoSchema(BaseModel):
    Job_Title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    location_country: Optional[str] = None
    job_id: Optional[str] = None
    job_url: Optional[str] = None
    Remote_Onsite: Optional[str] = None
    Job_Description: Optional[str] = None
    Responsibilities: Optional[str] = None
    Requirements: Optional[str] = None
    Skills: Optional[List[str]] = None
    Job_Function: Optional[str] = None
    recruiter_contact_no: Optional[str] = Field(None, alias="recruiter_contact no")
    recruiter_email: Optional[str] = None
    Salary_Range: Optional[str] = None
    Experience_Required: Optional[str] = None
    Posted_Date: Optional[str] = None
    visa_sponsorship: Optional[Literal["Yes", "No", "Unknown"]] = None
    reloation_provided: Optional[Literal["Yes", "No", "Unknown"]] = None
    summery: Optional[str] = None
    Additional_Info: Optional[AdditionalInfo] = None


# ---------------- Org Evaluator ----------------
class CompanyResearchReport(BaseModel):
    company_name: str
    company_location: str
    company_size: str
    company_average_salary_software_engineer: str
    recent_layoffs: str

class OrgEvaluatorSchema(BaseModel):
    company_research_report: CompanyResearchReport
