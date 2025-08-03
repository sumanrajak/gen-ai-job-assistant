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
    Job_Title: str
    company_name: str
    location: str
    location_country: str
    job_id: str
    job_url: str
    Remote_Onsite: Literal["Remote", "Hybrid", "Onsite", "Unknown"] = Field(..., alias="Remote/Onsite")
    Job_Description: str
    Responsibilities: str
    Requirements: str
    Skills: List[str]
    Job_Function: str
    recruiter_contact_no: str = Field(..., alias="recruiter_contact no")
    recruiter_email: str
    Salary_Range: str
    Experience_Required: str
    Posted_Date: str
    visa_sponsorship: Literal["Yes", "No", "Unknown"]
    reloation_provided: Literal["Yes", "No", "Unknown"]
    summery: str
    Additional_Info: AdditionalInfo


# ---------------- Org Evaluator ----------------
class CompanyResearchReport(BaseModel):
    company_name: str
    company_location: str
    company_size: str
    company_average_salary_software_engineer: str
    recent_layoffs: str

class OrgEvaluatorSchema(BaseModel):
    company_research_report: CompanyResearchReport
