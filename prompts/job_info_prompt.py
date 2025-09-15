# prompts/job_info_prompt.py

JOB_INFO_SCHEMA = {
    "Job_Title": "string",
    "company_name": "string",
    "location": "string",
    "location_country": "string",
    "job_id": "string",
    "job_url": "string",
    "Remote/Onsite": "string",
    "Job_Description": "string",
    "Responsibilities": "string",
    "Requirements": "string",
    "Skills": ["string"],
    "Job_Function": "string",
    "recruiter_contact no": "string",
    "recruiter_email": "string",
    "Salary_Range": "string",
    "Experience_Required": "string",
    "Posted_Date": "string",
    "visa_sponsorship": "Yes | No | Unknown",
    "reloation_provided": "Yes | No | Unknown",
    "summery": "string",
    "Additional_Info": {
        "Tech_Stack": ["string"],
        "Perks": ["string"]
    }
}

JOB_INFO_PROMPT_TEMPLATE = '''
You are an advanced AI agent specialized in precisely extracting and structuring information from job listings.
Your goal is to thoroughly parse the provided job posting text and output the details into a structured JSON format.
special instructions:

* **Summary:** Create a detailed summary of the job posting, between 500 and 600 words. It should cover responsibilities, required skills, and experience.
* **Tech Stack:** Inside `additional_info`, identify and list all relevant technologies, programming languages, frameworks, and tools mentioned.
* **Perks:** Inside `additional_info`, extract any benefits or perks offered (e.g., health insurance, retirement plans, remote work options).
* **Visa and Relocation:** For `visa_sponsorship` and `relocation_provided`, respond with "Yes", "No", or "Unknown".
* **Job ID:** Extract the `job_id` from the URL or job description. If not available, generate a unique ID.
* **URL Info:** Try to extract information from the job URL ({url}), such as the `job_id`.

Respond strictly inside <json></json> tags. The JSON object must conform to the following schema.
Do not include any explanations or text outside of the JSON object.

Schema:
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
