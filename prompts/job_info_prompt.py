# prompts/job_info_prompt.py

JOB_INFO_SCHEMA = {
    "Job Title": "string",
    "Company Name": "string",
    "Company Type": "Startup | MNC | Government | Non-profit | Unknown",
    "Location": "string",
    "Remote/Onsite": "Remote | Hybrid | Onsite | Unknown",
    "Job Description": "string",
    "Responsibilities": "string",
    "Requirements": "string",
    "Skills": ["string"],
    "Seniority Level": "Intern | Junior | Mid | Senior | Lead | Director",
    "Employment Type": "Full-time | Part-time | Contract | Internship | Temporary",
    "Industry": "string",
    "Job Function": "string",
    "recruiter contact no": "string",
    "recruiter email": "string",
    "Salary Range": "string",
    "Experience Required": "string",
    "Posted Date": "string",
    "Additional Info": {
        "Tech Stack": ["string"],
        "Team Size": "string",
        "Culture": "string",
        "Perks": ["string"]
    }
}

JOB_INFO_PROMPT_TEMPLATE = '''
You are an AI agent helping to parse job listings.

Extract job details from the following text. Respond strictly in JSON format matching this schema:
{job_info_schema}
Job Posting:
{job_text}
'''

from pydantic import BaseModel
from typing import List

class FitReport(BaseModel):
    fit_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    summary: str
