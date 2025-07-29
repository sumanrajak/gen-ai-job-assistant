from pydantic import BaseModel
from typing import List

FIT_EVALUATOR_SCHEMA = {
    "fit_score": "float (1.0 - 10.0)",
    "matched_skills": ["string"],
    "missing_skills": ["string"],
    "summary": "string"
}

FIT_EVALUATOR_PROMPT_TEMPLATE = '''
You are a job fit evaluation assistant.

Compare the following resume and job description. Identify the overlap in skills and requirements.

Respond strictly inside <json></json> tags in JSON format matching this schema:
```
{schema}
```
Resume:
{resume}

Job Info:
{job_info}
'''

class FitReport(BaseModel):
    fit_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    summary: str
