import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import datetime
import os
import logging
EXCEL_DB_PATH = "job_application_records.xlsx"
def display_section(header: str, data: dict, level: int = 1):
    """
    Display a section with labeled fields and copy buttons.
    Handles nested dicts, and auto-switches between text_input and text_area based on value length.
    """
    header_prefix = "#" * (level + 2)  # ###, #### etc.
    st.markdown(f"{header_prefix} 🧩 {header}")

    for key, value in data.items():
        # Handle nested dicts recursively
        if isinstance(value, dict):
            display_section(f"{header} → {key}", value, level=level + 1)
            continue

        # Generate unique key for Streamlit widgets
        field_key = f"{header}_{key}"

        # Columns: field and copy button
        col1, col2 = st.columns([4, 1])
        with col1:
            str_value = str(value)

            # Choose widget based on text length
            if len(str_value) > 50 or "\n" in str_value:
                st.text_area(label=key, value=str_value, key=field_key, disabled=True, height=100)
            else:
                st.text_input(label=key, value=str_value, key=field_key, disabled=True)

        with col2:
            # Safe escaping for JS clipboard
            escaped_value = str_value.replace("'", "\\'").replace("\n", "\\n")
            copy_code = f"""
                <div style="display: flex; justify-content: center;">
                    <button onclick="navigator.clipboard.writeText('{escaped_value}').then(() => alert('Copied to clipboard!'))"
                        style="
                            background-color: #4CAF50;
                            color: white;
                            padding: 6px 12px;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                            font-size: 14px;
                        ">📋 Copy</button>
                </div>
                """
            components.html(copy_code, height=40)

def display_status(status_dict: dict):
    """Display real-time status of each agent"""
    st.markdown("### 🚦 Agent Processing Status")
    for agent, status in status_dict.items():
        status_color = "green" if status == "✅ Done" else ("orange" if status == "⏳ In Progress" else "red")
        st.markdown(f"- **{agent}**: <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)

def display_error_logs(errors: list):
    """Display collected errors"""
    if errors:
        st.markdown("### ❌ Errors")
        for error in errors:
            st.error(error)


def display_recruiter_details_streamlit(heading,recruiter_data):
    """
    Displays a list of recruiter details in a Streamlit UI.

    Each recruiter will have their name, a button to open their LinkedIn profile,
    and their email address (if available).

    Args:
        recruiter_data (list of dict): A list of recruiter objects.
            Each object should have:
            - 'name' (str)
            - 'linkedin_profile_url' (str)
            - 'email_address' (str, or 'Not publicly available')
    """
    st.header(heading)
    

    if not recruiter_data:
        st.info("No recruiter details to display.")
        return

    # Use Streamlit's columns or just iterate to create cards/sections
    # For a simple list, direct iteration with st.expander or st.container works well.
    # Let's use st.container for a card-like look for each recruiter.

    for i, recruiter in enumerate(recruiter_data):
        with st.container(border=True): # Adds a visual border around each recruiter's info
            recruiter_ID = ''.join(filter(lambda x: not x.isdigit(), recruiter.split("/")[-1]))
            st.subheader(recruiter_ID)
            linkedin_url = recruiter
            if linkedin_url:
                # Streamlit's button can directly open URLs
                st.link_button(
                    label="View LinkedIn Profile",
                    url=linkedin_url,
                    help=f"Go to {recruiter_ID}'s LinkedIn profile",
                    type="primary" # Optional: makes the button blue
                )
            else:
                st.write("LinkedIn Profile: Not available")

            
            
            # Optional: Add a separator for better visual distinction if not using st.container border
            # if i < len(recruiter_data) - 1:
            #     st.divider()


def display_section_grid(header: str, data: dict):
    st.subheader(header)
    for key, value in data.items():
        if isinstance(value, dict):
            # Recursively display nested dictionaries
            st.markdown(f"**{key.replace('_', ' ').title()}:**")
            for sub_key, sub_value in value.items():
                st.markdown(f"- **{sub_key.replace('_', ' ').title()}:** {sub_value}")
        elif isinstance(value, list):
            st.write(f"**{key.replace('_', ' ').title()}:** {', '.join(value)}")
        else:
            if value is not None and value != "":
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

def display_recruiter_details_streamlit_modified(heading, recruiter_data):
    """
    Displays a list of recruiter details in a Streamlit UI, adjusted for cleaner integration.
    """
    st.markdown(f"**{heading}:**")

    if not recruiter_data:
        st.info("No recruiter details to display.")
        return

    for i, recruiter_url in enumerate(recruiter_data):
        # Extract a simplified name from the URL if possible, or use index
        # Example: if URL is linkedin.com/in/john-doe-123, try to get "John Doe"
        recruiter_name = f"Recruiter {i+1}"
        if "/in/" in recruiter_url:
            parts = recruiter_url.split("/in/")[1].split("/")[0].replace('-', ' ').title()
            recruiter_name = parts if parts else recruiter_name

        st.markdown(f"**{recruiter_name}**")
        st.link_button(
            label="View LinkedIn Profile",
            url=recruiter_url,
            help=f"Go to {recruiter_name}'s LinkedIn profile",
            type="primary"
        )
        st.markdown("---") # Separator for each recruiter



def display_application_records():
    """Fetches and displays saved application records from a selected Excel sheet."""

    if not os.path.exists(EXCEL_DB_PATH):
        st.info("No saved application records found yet.")
        return

    try:
        # Load all sheet names from the Excel file
        excel_file = pd.ExcelFile(EXCEL_DB_PATH, engine='openpyxl')
        sheet_names = excel_file.sheet_names

        if not sheet_names:
            st.info("No sheets found in the Excel file.")
            return

        # Create a dropdown to select the sheet (country)
        selected_sheet = st.selectbox(
            "Select Location (Country):",
            options=sheet_names,
            index=0 # Default to the first sheet
        )

        # Read the DataFrame from the selected sheet
        df = pd.read_excel(EXCEL_DB_PATH, sheet_name=selected_sheet, engine='openpyxl')

        if df.empty:
            st.info(f"No saved application records found in the '{selected_sheet}' sheet yet.")
            return

        # Sort by date saved, newest first
        # Convert 'Date Saved' to datetime objects for proper sorting if it's not already
        df["Date Saved"] = pd.to_datetime(df["Date Saved"], errors='coerce') # 'coerce' turns invalid dates into NaT
        df = df.sort_values(by="Date Saved", ascending=False).reset_index(drop=True)

        st.subheader(f"Records for {selected_sheet}")

        # Iterate and display records for the selected sheet
        for index, row in df.iterrows():
            job_title = row.get("Job_Title", "N/A")
            company_name = row.get("company_name", "N/A")
            # Format date only if it's a valid datetime object
            date_saved = row.get("Date Saved", pd.NaT)
            date_saved_str = date_saved.strftime("%Y-%m-%d") if pd.notna(date_saved) else "N/A"
            location = row.get("location", "N/A")
            job_id = row.get("job_id", "N/A")
            is_applied = row.get("is_applied", False)

            header_text = (
                f"{' ✅ ' if is_applied else ''} "
                f"[{job_id}] - "
                f"{company_name} - "
                f"[ {job_title}] - "
                f"{date_saved_str} - "
                f"{location[:20]}{'...' if len(location) > 20 else ''}" # Increased location display
            )

            with st.expander(header_text):
                # Ensure the 'Mark as Applied' button interacts correctly with the specific sheet
                if is_applied:
                    st.success("Application already marked as applied.")
                else:
                    # Use a unique key for the button based on index AND selected_sheet
                    if st.button("Mark as Applied", key=f"apply_button_{selected_sheet}_{index}"):
                        # Update the DataFrame in memory
                        df.loc[index, 'is_applied'] = True
                        try:
                            # To update a specific sheet without affecting others, we need to
                            # re-read all sheets, update the specific one, and then re-write the entire file.
                            # This is crucial because `to_excel` in 'replace' mode only works on a single sheet
                            # and doesn't preserve other sheets when not in append mode on the file.

                            # Load the entire workbook again
                            workbook_data = {sheet: pd.read_excel(EXCEL_DB_PATH, sheet_name=sheet, engine='openpyxl')
                                             for sheet in excel_file.sheet_names}

                            # Update the DataFrame for the current sheet
                            workbook_data[selected_sheet] = df

                            # Write all sheets back to the Excel file
                            with pd.ExcelWriter(EXCEL_DB_PATH, engine='openpyxl') as writer:
                                for sheet_name_to_write, sheet_df in workbook_data.items():
                                    sheet_df.to_excel(writer, sheet_name=sheet_name_to_write, index=False)

                            st.success("Application marked as applied. Please re-select the sheet to see the update.")
                            st.experimental_rerun() # Rerun to reflect the change immediately
                        except Exception as e:
                            st.error(f"❌ Error updating application record: {e}")
                            logging.exception("Error updating Excel record:")

                st.subheader("🎯 Job Fit Evaluation")
                st.write(f"**Fit Score:** {row.get('fit_score', 'N/A')}/10.0")
                st.write(f"**Matched Skills:** {row.get('fit_matched_skills', 'N/A')}")
                st.write(f"**Missing Skills:** {row.get('fit_missing_skills', 'N/A')}")
                st.write(f"**Summary:** {row.get('fit_summary', 'N/A')}")

                st.markdown("---")

                st.subheader("✉️ Communication Data")
                if row.get("job_url"):
                    st.markdown(f"**Job URL:** [Link]({row.get('job_url', 'N/A')})")
                if row.get("email_cold_subject"):
                    st.markdown("**Cold Email:**")
                    st.write(f"**Subject:** {row.get('email_cold_subject', 'N/A')}")
                    st.text_area("Body (Cold Email)", value=row.get('email_cold_body', 'N/A'), height=150, disabled=True, key=f"cold_email_body_{selected_sheet}_{index}")

                if row.get("cover_letter_body"):
                    st.markdown("**Cover Letter:**")
                    st.text_area("Body (Cover Letter)", value=row.get('cover_letter_body', 'N/A'), height=300, disabled=True, key=f"cover_letter_body_{selected_sheet}_{index}")

                if row.get("linkedin_message_recruiter"):
                    st.markdown("**LinkedIn Message (Recruiter):**")
                    st.text_area("Body (Recruiter)", value=row.get('linkedin_message_recruiter', 'N/A'), height=100, disabled=True, key=f"linkedin_recruiter_{selected_sheet}_{index}")

                if row.get("linkedin_message_referrer"):
                    st.markdown("**LinkedIn Message (Referrer):**")
                    st.text_area("Body (Referrer)", value=row.get('linkedin_message_referrer', 'N/A'), height=100, disabled=True, key=f"linkedin_referrer_{selected_sheet}_{index}")

                # Optionally display recruiter URLs and organization data
                recruiter_urls = []
                try:
                    # Ensure it tries to load from a string, not a float if 'N/A' or similar is passed
                    recruiter_data_raw = row.get("recruiter_linkedin_urls", "[]")
                    if isinstance(recruiter_data_raw, str):
                        recruiter_urls = json.loads(recruiter_data_raw)
                    else: # Handle cases where it might be NaN or other non-string types
                        recruiter_urls = []
                except json.JSONDecodeError:
                    logging.warning(f"JSON Decode Error for recruiter_linkedin_urls at index {index}: {recruiter_data_raw}")
                    pass # Handle cases where it might not be valid JSON

                if recruiter_urls:
                    st.markdown("---")
                    st.subheader("👤 Recruiter Information")
                    for i, r_url in enumerate(recruiter_urls):
                        r_name = r_url.split("/in/")[1].split("/")[0].replace('-', ' ').title() if "/in/" in r_url else f"Recruiter {i+1}"
                        st.write(f"**LinkedIn Profile ({r_name}):** [Link]({r_url})")

                if row.get("org_company_name"):
                    st.markdown("---")
                    st.subheader("🏢 Organization Data")
                    st.write(f"**Company Name:** {row.get('org_company_name', 'N/A')}")
                    st.write(f"**Location:** {row.get('org_company_location', 'N/A')}")
                    st.write(f"**Size:** {row.get('org_company_size', 'N/A')}")
                    st.write(f"**Avg. SE Salary:** {row.get('org_avg_salary_se', 'N/A')}")
                    st.write(f"**Recent Layoffs:** {row.get('org_recent_layoffs', 'N/A')}")

    except FileNotFoundError:
        st.error(f"❌ Error: The Excel file '{EXCEL_DB_PATH}' was not found.")
    except PermissionError:
        st.error(f"❌ Permission denied. Please close the Excel file '{EXCEL_DB_PATH}' if it's open.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred while loading records: {e}")
        logging.exception("Error reading Excel DB for display:")

def save_application_record(job_info, fit_eval, email_gen, org_eval, recruiter_data):
    """Saves all extracted and generated data to an Excel sheet."""
    record = {
        "Date Saved": datetime.date.today().isoformat(),
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
        "org_company_name": org_eval.get("company_research_report", {}).get("company_name", ""),
        "org_company_location": org_eval.get("company_research_report", {}).get("company_location", ""),
        "org_company_size": org_eval.get("company_research_report", {}).get("company_size", ""),
        "org_avg_salary_se": org_eval.get("company_research_report", {}).get("company_average_salary_software_engineer", ""),
        "org_recent_layoffs": org_eval.get("company_research_report", {}).get("recent_layoffs", ""),
        "recruiter_linkedin_urls": json.dumps(recruiter_data) if recruiter_data else "[]", # Store as JSON string
        "is_applied": False,  # Default to False, can be updated later
        # You can add more fields from JOB_INFO_SCHEMA, ORG_EVALUATER_SCHEMA if needed
    }
    print("Record to be saved:", record) # For debugging

    new_record_df = pd.DataFrame([record])
    print("DataFrame for new record:\n", new_record_df) # For debugging

    # Determine the sheet name, using 'Other' as a fallback if country is not available
    sheet_name = job_info.get("location_country", "Other")
    if not sheet_name: # Handle cases where location_country might be an empty string
        sheet_name = "Other"

    try:
        if os.path.exists(EXCEL_DB_PATH):
            # Read existing sheets to maintain their content
            with pd.ExcelWriter(EXCEL_DB_PATH, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                # Iterate through existing sheets to preserve them
                excel_file = pd.ExcelFile(EXCEL_DB_PATH, engine='openpyxl')
                for existing_sheet in excel_file.sheet_names:
                    if existing_sheet != sheet_name: # Don't re-write the target sheet yet
                        existing_df = pd.read_excel(EXCEL_DB_PATH, sheet_name=existing_sheet, engine='openpyxl')
                        existing_df.to_excel(writer, sheet_name=existing_sheet, index=False)

                # Now handle the target sheet
                if sheet_name in excel_file.sheet_names:
                    existing_data_for_sheet = pd.read_excel(EXCEL_DB_PATH, sheet_name=sheet_name, engine='openpyxl')
                    combined_df = pd.concat([existing_data_for_sheet, new_record_df], ignore_index=True)
                    combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    new_record_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # If the file doesn't exist, create it with the new record
            with pd.ExcelWriter(EXCEL_DB_PATH, engine='openpyxl') as writer:
                new_record_df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Record successfully saved to {EXCEL_DB_PATH} in sheet '{sheet_name}'.")

    except FileNotFoundError:
        print(f"Error: The Excel file '{EXCEL_DB_PATH}' was not found.")
    except PermissionError:
        print(f"Error: Permission denied. Please close the Excel file '{EXCEL_DB_PATH}' if it's open.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


