from pydantic import BaseModel
from typing import List

GET_RECRUITER_SCHEMA = {
   "search_query": "str",
}

GET_RECRUITER_PROMPT = '''
You are an expert google search agent.
you are very experienced  in doing advance google  queary search 
like use advance goolgle search techniques to find recruiters on LinkedIn or other professional networks.
like "site:linkedin.com/in/ OR site:linkedin.com/pub/ ("hiring manager" OR recruiter) "company_name" "location""

give me a advance google search query to find recruiters for the company and location provided.
company_name: {company_name}
location: {location}
that ill put in google search bar to find recruiters for the company and location provided.
note the location can be any where in the world. accordingly the linkdin url will be different.

**[IMPORTANT]Respond strictly inside <json> </json> tags in JSON format matching this schema:**
{schema}

---
'''
