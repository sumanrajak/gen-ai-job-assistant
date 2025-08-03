# prompts/job_info_prompt.py

JOB_INFO_SCHEMA = {
    "Job_Title": "string",
    "company_name": "string",
    "location": "string",
    "location_country": "string",
    "job_id": "string",
    "job_url": "string",
    "Remote/Onsite": "Remote | Hybrid | Onsite | Unknown",
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

* **Summery:** Include a brief summary of the job posting in the output.include the responsibility
skills and experience required  in the summary word limit 500 to 600.
* **Tech Stack:** Identify and list all relevant technologies, programming languages, frameworks, and tools mentioned in the job description.
* **Perks:** Extract any benefits or perks offered by the company, such as health insurance
, retirement plans, remote work options, etc.
visa sponsorship and relocation provided should be mentioned if mentioned in the job description.
job_id should be extracted from the url if available or from the job description. or randomly generate a unique id if not available.
* ** extract url info** try to extact info from {url} like job_id .

Respond strictly inside <json></json> tags in JSON format matching this schema:
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
