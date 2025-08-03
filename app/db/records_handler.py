import os
import pandas as pd
import json
from datetime import date

EXCEL_DB_PATH = "job_application_records.xlsx"

def save_application_record(job_info, fit_eval, email_gen, org_eval=None, recruiter_data=None):
    record = {
        "Date Saved": date.today().isoformat(),
        "Job_Title": job_info.get("Job_Title", ""),
        "job_id": job_info.get("job_id", ""),
        "company_name": job_info.get("company_name", ""),
        "location": job_info.get("location", ""),
        "location_country": job_info.get("location_country", ""),
        "job_url": job_info.get("job_url", ""),
        "fit_score": fit_eval.get("fit_score", None),
        "fit_matched_skills": ", ".join(fit_eval.get("matched_skills", [])),
        "fit_missing_skills": ", ".join(fit_eval.get("missing_skills", [])),
        "fit_summary": fit_eval.get("summary", ""),
        "email_cold_subject": email_gen.get("cold email", {}).get("subject", ""),
        "email_cold_body": email_gen.get("cold email", {}).get("body", ""),
        "cover_letter_body": email_gen.get("cover letter", {}).get("body", ""),
        "linkedin_message_recruiter": email_gen.get("linkdin_networking_message_recruiter", {}).get("body", ""),
        "linkedin_message_referrer": email_gen.get("linkdin_networking_message_referrer", {}).get("body", ""),
        "org_company_name": org_eval.get("company_research_report", {}).get("company_name", "") if org_eval else "",
        "org_company_location": org_eval.get("company_research_report", {}).get("company_location", "") if org_eval else "",
        "org_company_size": org_eval.get("company_research_report", {}).get("company_size", "") if org_eval else "",
        "org_avg_salary_se": org_eval.get("company_research_report", {}).get("company_average_salary_software_engineer", "") if org_eval else "",
        "org_recent_layoffs": org_eval.get("company_research_report", {}).get("recent_layoffs", "") if org_eval else "",
        "recruiter_linkedin_urls": json.dumps(recruiter_data) if recruiter_data else "[]",
        "is_applied": False
    }

    df = pd.DataFrame([record])
    if os.path.exists(EXCEL_DB_PATH):
        existing = pd.read_excel(EXCEL_DB_PATH)
        df = pd.concat([existing, df], ignore_index=True)

    df.to_excel(EXCEL_DB_PATH, index=False)

def load_application_records():
    if not os.path.exists(EXCEL_DB_PATH):
        return []
    df = pd.read_excel(EXCEL_DB_PATH)
    return df.fillna("").to_dict(orient="records")

def mark_as_applied(job_id: str):
    if not os.path.exists(EXCEL_DB_PATH):
        return False
    df = pd.read_excel(EXCEL_DB_PATH)
    if job_id not in df["job_id"].values:
        return False
    df.loc[df["job_id"] == job_id, "is_applied"] = True
    df.to_excel(EXCEL_DB_PATH, index=False)
    return True
