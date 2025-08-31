import os
import pandas as pd
import json
import re
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
        "is_applied": False,
        "is_flagged": False,
        "notes": ""
    }
    new_record_df = pd.DataFrame([record])

    # Determine sheet name from country, default to "General"
    sheet_name = job_info.get("location_country", "").strip()
    if not sheet_name:
        sheet_name = "General"

    # Sanitize sheet name for Excel (max 31 chars, no invalid chars like : \ / ? * [ ])
    sheet_name = re.sub(r'[\\:/?*\[\]]', '', sheet_name)
    sheet_name = sheet_name[:31]

    if os.path.exists(EXCEL_DB_PATH):
        try:
            with pd.ExcelFile(EXCEL_DB_PATH) as xls:
                all_sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
        except Exception:
            # If file is corrupt or empty, start fresh
            all_sheets = {}

        if sheet_name in all_sheets:
            # Append to existing sheet
            existing_df = all_sheets[sheet_name]
            updated_df = pd.concat([existing_df, new_record_df], ignore_index=True)
        else:
            # This is a new sheet
            updated_df = new_record_df
        
        all_sheets[sheet_name] = updated_df

        # Write all sheets back
        with pd.ExcelWriter(EXCEL_DB_PATH, engine='openpyxl') as writer:
            for s_name, s_df in all_sheets.items():
                s_df.to_excel(writer, sheet_name=s_name, index=False)
    else:
        # File doesn't exist, create it with the new record in its sheet
        new_record_df.to_excel(EXCEL_DB_PATH, sheet_name=sheet_name, index=False)

def load_application_records():
    if not os.path.exists(EXCEL_DB_PATH):
        return []
    # Read all sheets and concatenate them
    all_sheets_df = pd.read_excel(EXCEL_DB_PATH, sheet_name=None)
    if not all_sheets_df:
        return []
    
    combined_df = pd.concat(all_sheets_df.values(), ignore_index=True)
    return combined_df.fillna("").to_dict(orient="records")

def mark_as_applied(job_id: str,sheet_name: str = None):
    print(f"Marking job_id {job_id} as applied.")
    if not os.path.exists(EXCEL_DB_PATH):
        return False
    try:
        with pd.ExcelFile(EXCEL_DB_PATH) as xls:
            all_sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

    sheet_to_update = None
    for name, df_sheet in all_sheets.items():
        # Ensure job_id column exists and compare as strings for safety
        if "job_id" in df_sheet.columns and job_id in df_sheet["job_id"].astype(str).values:
            df_sheet.loc[df_sheet["job_id"].astype(str) == job_id, "is_applied"] = True
            sheet_to_update = name
            break

    if sheet_to_update:
        with pd.ExcelWriter(EXCEL_DB_PATH, engine='openpyxl') as writer:
            for name, df_sheet in all_sheets.items():
                df_sheet.to_excel(writer, sheet_name=name, index=False)
        print(f"Successfully marked job_id {job_id} as applied in sheet '{sheet_to_update}'.")
        return True
    else:
        print(f"job_id {job_id} not found in any sheet.")
        return False

def list_sheet_names():
    if not os.path.exists(EXCEL_DB_PATH):
        return []
    with pd.ExcelFile(EXCEL_DB_PATH) as xls:
        return xls.sheet_names

def load_sheet_data(sheet_name: str):
    if not os.path.exists(EXCEL_DB_PATH):
        return []
    with pd.ExcelFile(EXCEL_DB_PATH) as xls:
        if sheet_name not in xls.sheet_names:
            return []
        df = pd.read_excel(xls, sheet_name=sheet_name)
        return df.fillna("").to_dict(orient="records")
    
def toggle_flag_status(job_id: str):
    if not os.path.exists(EXCEL_DB_PATH):
        return False
    try:
        with pd.ExcelFile(EXCEL_DB_PATH) as xls:
            all_sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

    sheet_found = None
    for name, df_sheet in all_sheets.items():
        if "job_id" in df_sheet.columns and job_id in df_sheet["job_id"].astype(str).values:
            sheet_found = name
            break

    if sheet_found:
        df = all_sheets[sheet_found]
        if "is_flagged" not in df.columns:
            df["is_flagged"] = False
        
        mask = df["job_id"].astype(str) == job_id
        current_status = df.loc[mask, "is_flagged"].iloc[0]
        df.loc[mask, "is_flagged"] = not bool(current_status)

        with pd.ExcelWriter(EXCEL_DB_PATH, engine='openpyxl') as writer:
            for name, df_sheet in all_sheets.items():
                df_sheet.to_excel(writer, sheet_name=name, index=False)
        print(f"Successfully toggled flag for job_id {job_id} in sheet '{sheet_found}'.")
        return True
    else:
        print(f"job_id {job_id} not found in any sheet.")
        return False

def update_notes(job_id: str, notes: str):
    """Updates the 'notes' for a given job_id across all sheets."""
    if not os.path.exists(EXCEL_DB_PATH):
        return False
    try:
        with pd.ExcelFile(EXCEL_DB_PATH) as xls:
            all_sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

    sheet_found = None
    for name, df_sheet in all_sheets.items():
        if "job_id" in df_sheet.columns and job_id in df_sheet["job_id"].astype(str).values:
            sheet_found = name
            break

    if sheet_found:
        df = all_sheets[sheet_found]
        if "notes" not in df.columns:
            df["notes"] = ""
        
        mask = df["job_id"].astype(str) == job_id
        df.loc[mask, "notes"] = notes

        with pd.ExcelWriter(EXCEL_DB_PATH, engine='openpyxl') as writer:
            for name, df_sheet in all_sheets.items():
                df_sheet.to_excel(writer, sheet_name=name, index=False)
        print(f"Successfully updated notes for job_id {job_id} in sheet '{sheet_found}'.")
        return True
    else:
        print(f"job_id {job_id} not found in any sheet.")
        return False

def delete_job_record(job_id: str):
    """Deletes a job record by its job_id from any sheet."""
    if not os.path.exists(EXCEL_DB_PATH):
        return False
    try:
        with pd.ExcelFile(EXCEL_DB_PATH) as xls:
            all_sheets = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return False

    sheet_found = None
    for name, df_sheet in all_sheets.items():
        if "job_id" in df_sheet.columns and job_id in df_sheet["job_id"].astype(str).values:
            sheet_found = name
            break

    if sheet_found:
        df = all_sheets[sheet_found]
        mask = df["job_id"].astype(str) == job_id
        df.drop(df[mask].index, inplace=True)
        
        if df.empty:
            del all_sheets[sheet_found]

        with pd.ExcelWriter(EXCEL_DB_PATH, engine='openpyxl') as writer:
            for name, df_sheet in all_sheets.items():
                df_sheet.to_excel(writer, sheet_name=name, index=False)
        print(f"Successfully deleted job_id {job_id} from sheet '{sheet_found}'.")
        return True
    else:
        print(f"job_id {job_id} not found in any sheet.")
        return False