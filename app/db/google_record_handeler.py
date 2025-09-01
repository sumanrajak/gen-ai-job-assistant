import pandas as pd
import json
import re
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

# ==============================================================================
# Step 1: Configuration & Initialization (Replace with your details)
# ==============================================================================
GOOGLE_SHEET_NAME = "gen_ai_job_search"  # The name of your Google Spreadsheet
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Path to your JSON key file

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_worksheet(sheet_title: str, worksheet_title: str):
    """Initializes the gspread client and returns a worksheet handle."""
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open(sheet_title)
    except FileNotFoundError:
        print(f"Error: Service account file '{SERVICE_ACCOUNT_FILE}' not found.")
        return None
    except SpreadsheetNotFound:
        print(f"Spreadsheet '{sheet_title}' not found. Creating a new one...")
        try:
            spreadsheet = client.create(sheet_title)
            # Share the new spreadsheet with the service account
            spreadsheet.share(creds.client_email, perm_type='user', role='writer')
        except Exception as e:
            print(f"Error creating spreadsheet: {e}")
            return None

    try:
        # Check if the worksheet already exists
        worksheet = spreadsheet.worksheet(worksheet_title)
    except WorksheetNotFound:
        print(f"Worksheet '{worksheet_title}' not found. Creating a new one...")
        # Add a new worksheet if it doesn't exist
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="100", cols="25")
        # Write the header row
        # This is a dummy dataframe just to get the headers
        headers = list(pd.DataFrame([{} for _ in range(1)]).columns)
        worksheet.append_row(headers)
    
    return worksheet

def get_all_worksheets():
    """Returns a dictionary of all worksheets in the spreadsheet."""
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open(GOOGLE_SHEET_NAME)
        worksheets = {ws.title: ws for ws in spreadsheet.worksheets()}
        return worksheets
    except (FileNotFoundError, SpreadsheetNotFound) as e:
        print(f"Error accessing spreadsheet: {e}")
        return {}
    
# ==============================================================================
# Step 2: Refactored CRUD Operations
# ==============================================================================

def save_application_record(job_info, fit_eval, email_gen, org_eval=None, recruiter_data=None):
    """Saves a new job application record to the appropriate Google Sheet."""
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
    
    sheet_name = job_info.get("location_country", "").strip() or "General"
    sheet_name = re.sub(r'[\\:/?*\[\]]', '', sheet_name)[:31]
    
    worksheet = get_worksheet(GOOGLE_SHEET_NAME, sheet_name)
    if worksheet:
        # Check if headers exist, if not, create them
        current_headers = worksheet.row_values(1)
        record_headers = list(record.keys())
        if not current_headers or current_headers != record_headers:
            # Clear existing headers and append new ones if they don't match
            if current_headers:
                worksheet.clear()
            worksheet.append_row(record_headers)
            print(f"Warning: Headers in sheet '{sheet_name}' were incorrect. Updated.")
            
        worksheet.append_row(list(record.values()))
        print(f"Successfully saved record for '{record['Job_Title']}' to Google Sheet.")
        return True
    return False

def load_application_records():
    """Loads all records from all sheets and combines them."""
    all_records = []
    worksheets = get_all_worksheets()
    for ws_name, ws in worksheets.items():
        if ws_name == 'Sheet1' and ws.get_all_values() == [['']]:
            continue # Ignore default empty sheet
        try:
            records = ws.get_all_records()
            all_records.extend(records)
        except gspread.exceptions.APIError:
            print(f"Could not load records from sheet '{ws_name}'. Skipping.")
            continue
    return all_records

def mark_as_applied(job_id: str):
    """Marks a job record as applied based on job_id."""
    worksheets = get_all_worksheets()
    for ws_name, ws in worksheets.items():
        cell = ws.find(str(job_id))
        if cell:
            try:
                # Find the "is_applied" column index
                headers = ws.row_values(1)
                is_applied_col_idx = headers.index("is_applied") + 1
                # Update the cell value
                ws.update_cell(cell.row, is_applied_col_idx, "TRUE")
                print(f"Successfully marked job_id {job_id} as applied.")
                return True
            except ValueError:
                print(f"Column 'is_applied' not found in sheet '{ws_name}'.")
                continue
    print(f"job_id {job_id} not found in any sheet.")
    return False

def toggle_flag_status(job_id: str):
    """Toggles the 'is_flagged' status for a given job_id."""
    worksheets = get_all_worksheets()
    for ws_name, ws in worksheets.items():
        cell = ws.find(str(job_id))
        if cell:
            try:
                headers = ws.row_values(1)
                is_flagged_col_idx = headers.index("is_flagged") + 1
                
                # Get current value and toggle
                current_value = ws.cell(cell.row, is_flagged_col_idx).value
                new_value = "FALSE" if current_value.upper() == "TRUE" else "TRUE"
                
                ws.update_cell(cell.row, is_flagged_col_idx, new_value)
                print(f"Successfully toggled flag for job_id {job_id}.")
                return True
            except ValueError:
                print(f"Column 'is_flagged' not found in sheet '{ws_name}'.")
                continue
    print(f"job_id {job_id} not found in any sheet.")
    return False

def update_notes(job_id: str, notes: str):
    """Updates the 'notes' for a given job_id."""
    worksheets = get_all_worksheets()
    for ws_name, ws in worksheets.items():
        cell = ws.find(str(job_id))
        if cell:
            try:
                headers = ws.row_values(1)
                notes_col_idx = headers.index("notes") + 1
                ws.update_cell(cell.row, notes_col_idx, notes)
                print(f"Successfully updated notes for job_id {job_id}.")
                return True
            except ValueError:
                print(f"Column 'notes' not found in sheet '{ws_name}'.")
                continue
    print(f"job_id {job_id} not found in any sheet.")
    return False

def delete_job_record(job_id: str):
    """Deletes a job record by its job_id."""
    worksheets = get_all_worksheets()
    for ws_name, ws in worksheets.items():
        cell = ws.find(str(job_id))
        if cell:
            ws.delete_rows(cell.row)
            print(f"Successfully deleted record for job_id {job_id}.")
            return True
    print(f"job_id {job_id} not found in any sheet.")
    return False

# ==============================================================================
# Additional helper functions for listing sheets and loading specific sheet data
# ==============================================================================

def list_sheet_names():
    """Lists all worksheet names in the spreadsheet."""
    worksheets = get_all_worksheets()
    return list(worksheets.keys()) if worksheets else []

def load_sheet_data(sheet_name: str):
    """Loads all records from a specific worksheet."""
    worksheet = get_worksheet(GOOGLE_SHEET_NAME, sheet_name)
    if worksheet:
        return worksheet.get_all_records()
    return []