# main.py

import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import datetime
import pandas as pd
import json


import time
import streamlit as st
import streamlit.components.v1 as components # Import components for custom HTML/JS
from utils.file_io import load_resume # Assuming this exists and works
from llm.perplexity import PerplexityLLM # Assuming these LLMs are correctly implemented
from llm.groq import GroqLLM # Assuming these LLMs are correctly implemented
from agents.job_extractor import JobInfoExtractor
from agents.fit_evaluator import FitEvaluatorAgent
from agents.email_generator import EmailGeneratorAgent
from agents.org_evaluater import OrgEvaluatorAgent
from agents.get_recruiter_agent import GetRecruiterAgent
from ui.ui_components import display_recruiter_details_streamlit_modified # Assuming this exists and works
from ui.ui_components import display_application_records # Assuming this exists and works
from ui.ui_components import save_application_record # Assuming this exists and works

# --------------------- Config & Logging ---------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define the path for the Excel database


st.set_page_config(page_title="Job Auto Apply", layout="wide")

# --- Custom CSS for a cleaner look and feel like the image ---
st.markdown("""
<style>
    .reportview-container {
        background: #0E1117; /* Dark background */
    }
    .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        color: #FFFFFF; /* White text for main title */
        font-size: 3em;
        text-align: center;
        margin-bottom: 1em;
    }
    h2 {
        color: #ADD8E6; /* Light blue for section titles */
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    h3 {
        color: #ADD8E6;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    .stTextInput label, .stTextArea label {
        color: #ADD8E6; /* Light blue for input labels */
        font-weight: bold;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #262730; /* Darker input background */
        color: #FFFFFF; /* White text in inputs */
        border: 1px solid #4F505B;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
    }
    .stButton > button {
        background-color: #4A90E2; /* Blue button */
        color: white;
        border-radius: 0.5rem;
        padding: 0.6rem 1.5rem;
        font-size: 1.1em;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3A7BBF;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        color: #ADD8E6; /* Light blue for tab text */
    }
    .stTabs [data-baseweb="tab-list"] button.st-emotion-cache-1fzh2tz {
        background-color: #262730; /* Darker tab background */
        border-bottom: 3px solid transparent;
        transition: border-bottom 0.3s ease;
    }
    .stTabs [data-baseweb="tab-list"] button.st-emotion-cache-1fzh2tz[aria-selected="true"] {
        border-bottom: 3px solid #4A90E2; /* Active tab underline */
    }
    .metric-card {
        background-color: #262730;
        border-radius: 0.75rem;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        color: #FFFFFF;
        height: 100%; /* Ensure cards in a row have similar height */
    }
    .metric-card h3 {
        color: #ADD8E6;
        margin-top: 0;
        font-size: 1.5em;
    }
    .metric-card p {
        font-size: 1.2em;
        margin: 0.5em 0;
    }
    .st-emotion-cache-16txt5c { /* Target Streamlit's default container padding */
        padding: 2rem;
    }
    .copy-button-container {
        display: flex;
        justify-content: flex-end; /* Aligns the button to the right */
        margin-top: -30px; /* Adjust to position correctly relative to the text area/input */
        margin-bottom: 10px;
    }
    .copy-button {
        background-color: #5cb85c; /* Green color for copy button */
        color: white;
        padding: 5px 10px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9em;
        transition: background-color 0.2s;
    }
    .copy-button:hover {
        background-color: #4cae4c;
    }
</style>
""", unsafe_allow_html=True)


st.title("🚀 Job Auto Apply Assistant")

# --------------------- State Initialization ---------------------
if 'job_info_data' not in st.session_state:
    st.session_state.job_info_data = None
if 'fit_eval_data' not in st.session_state:
    st.session_state.fit_eval_data = None
if 'email_gen_data' not in st.session_state:
    st.session_state.email_gen_data = None
if 'org_eval_data' not in st.session_state:
    st.session_state.org_eval_data = None
if 'recruiter_data' not in st.session_state:
    st.session_state.recruiter_data = None
if 'raw_job_description_text' not in st.session_state:
    st.session_state.raw_job_description_text = ""

# --------------------- Navigation Bar ---------------------
tab1, tab2 = st.tabs(["Parse Job", "Records"])

with tab1:
    st.header("Parse Job Listing")
    job_text_input = st.text_area(
        "Paste job listing text here...",
        height=250,
        key="job_text_input_area"
    )

    if st.button("🔍 Parse Job and Evaluate", use_container_width=True):
        if not job_text_input:
            st.warning("Please paste the job listing text into the box.")
        else:
            perplexity_key = os.getenv("PERPLEXITY_API_KEY")
            groq_key = os.getenv("GROQ_API_KEY")

            if not perplexity_key or not groq_key:
                st.error("🚨 Missing API keys in .env file. Please check your configuration.")
            else:
                with st.spinner("⚙️ Processing job listing... This may take a moment..."):
                    try:
                        # Initialize LLMs and Agents
                        perplexity_llm = PerplexityLLM(api_key=perplexity_key)
                        groq_llm = GroqLLM(api_key=groq_key)

                        job_agent = JobInfoExtractor(llm=groq_llm)
                        fit_agent = FitEvaluatorAgent(llm=groq_llm)
                        email_agent = EmailGeneratorAgent(llm=groq_llm)
                        org_agent = OrgEvaluatorAgent(llm=perplexity_llm)
                        get_recruiter_agent = GetRecruiterAgent(llm=perplexity_llm)

                        # Store raw text

                        # Thread execution for parallel processing
                        with ThreadPoolExecutor(max_workers=4) as executor: # Increased workers for more parallelism
                            future_job = executor.submit(job_agent.run, job_text_input)

                            try:
                                # Job Extractor
                                job_text, job_info = future_job.result(timeout=180) # Increased timeout
                                st.session_state.job_info_data = job_info
                                st.session_state.raw_job_description_text = job_text

                                resume = load_resume()
                                if not resume:
                                    st.error("🚫 No resume found! Please ensure 'data/resume.txt' exists and contains your resume.")
                                    st.stop()

                                # Prepare arguments for concurrent calls
                                fit_args = (resume, job_info)
                                email_args = (resume, job_info)
                                org_args = (job_info.get("company_name", ""), job_info.get("location_country", ""))
                                recruiter_args = (job_info.get("company_name", ""), job_info.get("location_country", ""))

                                # Add delay of 2 seconds for each function call
                                time.sleep(2)
                                future_fit = executor.submit(fit_agent.run, *fit_args)
                                time.sleep(2)
                                future_email = executor.submit(email_agent.run, *email_args)
                                time.sleep(2)
                                future_org = executor.submit(org_agent.run, *org_args)
                                time.sleep(2)
                                future_recruiter = executor.submit(get_recruiter_agent.run, *recruiter_args)

                                # Collect results
                                st.session_state.fit_eval_data = future_fit.result(timeout=180)
                                st.session_state.email_gen_data = future_email.result(timeout=180)
                                st.session_state.org_eval_data = future_org.result(timeout=180)
                                st.session_state.recruiter_data = future_recruiter.result(timeout=180)

                            except TimeoutError as e:
                                st.error(f"⏳ An agent timed out: {e}. Please try again or check the input.")
                                logging.error(f"TimeoutError during agent execution: {e}")
                            except Exception as e:
                                st.error(f"❌ An error occurred during processing: {e}")
                                logging.exception(f"Error during agent execution: {e}")

                    except Exception as e:
                        st.error(f"🔥 Critical error during setup or initial processing: {e}")
                        logging.exception(f"Critical error: {e}")

    # --- Display Results in Grid Layout ---
    if st.session_state.job_info_data:
        st.markdown("---")
        st.header("Analysis Results")

        # Section 1: Raw Job Description
        with st.container(border=True):
            st.subheader("📝 Raw Job Description")
            st.text_area("Full Job Description", value=st.session_state.raw_job_description_text, height=300, disabled=True)

        st.markdown("---")

        # Grid for Job Info, Fit Evaluation, Company Evaluation, Email/Cover Letter, Recruiter Info
        col1, col2 = st.columns(2)

        with col1:
            # Job Info
            with st.container(border=True):
                st.subheader("💼 Extracted Job Information")
                job_info = st.session_state.job_info_data
                for key, value in job_info.items():
                    if key not in ["Job_Description", "Additional_Info"] and value: # Exclude detailed JD and Additional_Info for this high-level view
                        st.write(f"**{key.replace('_', ' ')}:** {value}")
                if job_info.get("Additional_Info"):
                    st.markdown("**Additional Info:**")
                    for sub_key, sub_value in job_info["Additional_Info"].items():
                        st.write(f"- **{sub_key.replace('_', ' ')}:** {', '.join(sub_value) if isinstance(sub_value, list) else sub_value}")

            st.markdown("---")

            # Fit Evaluation
            if st.session_state.fit_eval_data:
                with st.container(border=True):
                    st.subheader("🎯 Fit Evaluation Report")
                    fit_data = st.session_state.fit_eval_data
                    st.metric(label="Fit Score", value=f"{fit_data.get('fit_score', 'N/A')}/10.0")
                    st.write(f"**Matched Skills:** {', '.join(fit_data.get('matched_skills', []))}")
                    st.write(f"**Missing Skills:** {', '.join(fit_data.get('missing_skills', []))}")
                    st.write(f"**Summary:** {fit_data.get('summary', 'N/A')}")

            st.markdown("---")

            # Recruiter Information
            if st.session_state.recruiter_data:
                with st.container(border=True):
                    st.subheader("👤 Recruiter Information")
                    display_recruiter_details_streamlit_modified("Recruiter Details", st.session_state.recruiter_data)


        with col2:
            # Email & Cover Letter Generation
            if st.session_state.email_gen_data:
                with st.container(border=True):
                    st.subheader("✉️ Generated Communication")
                    email_data = st.session_state.email_gen_data

                    # Helper function to display text and copy button
                    def display_with_copy(label, value, is_text_area=True):
                        if value is None:
                            return # Skip if no value

                        # Unique key for Streamlit widget
                        widget_key = f"{label.replace(' ', '_').lower()}_{value[:20].replace(' ', '_')}_{hash(value)}"

                        # Safe escaping for JS clipboard
                        escaped_value = str(value).replace("'", "\\'").replace("\n", "\\n")

                        # Use Streamlit's text_input or text_area
                        if is_text_area:
                            st.text_area(label, value=value, height=150, disabled=True, key=widget_key + "_ta")
                        else:
                            st.text_input(label, value=value, disabled=True, key=widget_key + "_ti")

                        # Custom HTML for the copy button
                        copy_code = f"""
                            <div class="copy-button-container">
                                <button class="copy-button" onclick="navigator.clipboard.writeText('{escaped_value}').then(() => alert('Copied to clipboard!'))">📋 Copy</button>
                            </div>
                            """
                        components.html(copy_code, height=40)


                    if email_data.get("cold email"):
                        st.markdown("**Cold Email:**")
                        display_with_copy("Subject", email_data["cold email"].get("subject", ""), is_text_area=False)
                        display_with_copy("Body", email_data["cold email"].get("body", ""), is_text_area=True)
                        st.markdown("---") # Separator

                    if email_data.get("cover letter"):
                        st.markdown("**Cover Letter:**")
                        display_with_copy("Body", email_data["cover letter"].get("body", ""), is_text_area=True)
                        st.markdown("---") # Separator

                    if email_data.get("linkdin_networking_message_recruiter"):
                        st.markdown("**LinkedIn Message (Recruiter):**")
                        display_with_copy("Body", email_data["linkdin_networking_message_recruiter"].get("body", ""), is_text_area=True)
                        st.markdown("---") # Separator

                    if email_data.get("linkdin_networking_message_referrer"):
                        st.markdown("**LinkedIn Message (Referrer):**")
                        display_with_copy("Body", email_data["linkdin_networking_message_referrer"].get("body", ""), is_text_area=True)

            st.markdown("---")

            # Organization Evaluation
            if st.session_state.org_eval_data and st.session_state.org_eval_data.get("company_research_report"):
                with st.container(border=True):
                    st.subheader("🏢 Organization Evaluation")
                    org_report = st.session_state.org_eval_data["company_research_report"]
                    for key, value in org_report.items():
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")

        # --- Save Button ---
        st.markdown("---")
        if st.button("💾 Save Application Record", use_container_width=True, key="save_record_button"):
            if st.session_state.job_info_data and st.session_state.fit_eval_data and st.session_state.email_gen_data:
                save_application_record(
                    st.session_state.job_info_data,
                    st.session_state.fit_eval_data,
                    st.session_state.email_gen_data,
                    st.session_state.org_eval_data,
                    st.session_state.recruiter_data
                )
                st.success("✅ Application record saved successfully!")
                # Clear current session state after saving to allow new parsing
                st.session_state.job_info_data = None
                st.session_state.fit_eval_data = None
                st.session_state.email_gen_data = None
                st.session_state.org_eval_data = None
                st.session_state.recruiter_data = None
                st.session_state.raw_job_description_text = ""
                st.rerun() # Rerun to clear the display
            else:
                st.warning("⚠️ No complete data to save. Please parse a job first.")


with tab2:
    st.header("Job Application Records")
    display_application_records()


# --------------------- Helper Functions ---------------------

def display_section_grid(header: str, data: dict):
    """Displays a section of data in the grid layout."""
    st.subheader(header)
    for key, value in data.items():
        if isinstance(value, dict):
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
