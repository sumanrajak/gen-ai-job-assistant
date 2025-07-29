# main.py

import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import streamlit as st
from utils.file_io import load_resume
from llm.perplexity import PerplexityLLM
from llm.groq import GroqLLM
from agents.job_extractor import JobInfoExtractor
from agents.fit_evaluator import FitEvaluatorAgent
from agents.email_generator import EmailGeneratorAgent
from agents.org_evaluater import OrgEvaluatorAgent
from agents.get_recruiter_agent import GetRecruiterAgent
from ui.ui_components import display_section, display_status, display_error_logs, display_recruiter_details_streamlit

# --------------------- Config & Logging ---------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(page_title="Job Auto Apply", layout="wide")
st.title("🚀 Job Auto Apply Assistant")

# --------------------- UI Input ---------------------
job_url = st.text_input("🔗 Enter Job Posting URL")

# --------------------- State Initialization ---------------------
if 'agent_status' not in st.session_state:
    st.session_state.agent_status = {
        "JobInfoExtractor": "⏳ In Progress",
        "FitEvaluator": "🛑 Pending",
        "EmailGenerator": "🛑 Pending",
        "OrgEvaluator": "🛑 Pending",
        "GetRecruiter": "🛑 Pending"
    }
if 'errors' not in st.session_state:
    st.session_state.errors = []

# --------------------- Process Button ---------------------
if st.button("🔍 Extract & Evaluate Job") and job_url:

    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if not perplexity_key or not groq_key:
        st.error("Missing API keys in .env file.")
    else:
        with st.spinner("⚙️ Processing... Please wait..."):

            try:
                # Initialize LLMs and Agents
                perplexity_llm = PerplexityLLM(api_key=perplexity_key)
                groq_llm = GroqLLM(api_key=groq_key)

                job_agent = JobInfoExtractor(llm=groq_llm)
                fit_agent = FitEvaluatorAgent(llm=groq_llm)
                email_agent = EmailGeneratorAgent(llm=groq_llm)
                org_agent = OrgEvaluatorAgent(llm=perplexity_llm)
                get_recruiter_agent = GetRecruiterAgent(llm=perplexity_llm)

                # Thread execution
                with ThreadPoolExecutor(max_workers=2) as executor:
                    st.session_state.agent_status["JobInfoExtractor"] = "⏳ In Progress"
                    future_job = executor.submit(job_agent.run, job_url)

                    try:
                        job_text, job_info = future_job.result(timeout=120)
                        st.session_state.agent_status["JobInfoExtractor"] = "✅ Done"
                        display_section("Raw Job Description", {"Text": job_text})
                        display_section("Structured Job Info", job_info)

                        resume = load_resume()
                        if not resume:
                            st.session_state.errors.append("No resume found in 'data/resume.txt'")
                            st.stop()

                        # Run fit + email
                        st.session_state.agent_status["FitEvaluator"] = "⏳ In Progress"
                        st.session_state.agent_status["EmailGenerator"] = "⏳ In Progress"
                        st.session_state.agent_status["GetRecruiter"] = "⏳ In Progress"

                        future_fit = executor.submit(fit_agent.run, resume, job_info)
                        future_email = executor.submit(email_agent.run, resume, job_info)

                        try:
                            fit_result = future_fit.result(timeout=120)
                            email_result = future_email.result(timeout=120)
                            st.session_state.agent_status["FitEvaluator"] = "✅ Done"
                            st.session_state.agent_status["EmailGenerator"] = "✅ Done"
                            st.session_state.agent_status["GetRecruiter"] = "⏳ In Progress"

                            display_section("Fit Evaluation Report", fit_result)
                            display_section("Email & Cover Letter", email_result)

                        except TimeoutError:
                            st.session_state.errors.append("Fit or Email Agent timed out.")
                            st.session_state.agent_status["FitEvaluator"] = "❌ Timeout"
                            st.session_state.agent_status["EmailGenerator"] = "❌ Timeout"


                        # Run org evaluation
                        st.session_state.agent_status["OrgEvaluator"] = "⏳ In Progress"
                        try:
                            org_result = org_agent.run(job_info.get("company_name", ""), job_info.get("location_country", ""))
                            
                            recruiter = get_recruiter_agent.run(job_info.get("company_name", ""), job_info.get("location_country", ""))
                            st.session_state.agent_status["GetRecruiter"] = "✅ Done"
                            st.session_state.agent_status["OrgEvaluator"] = "✅ Done"
                            st.session_state.agent_status["GetRecruiter"] = "✅ Done"
                            display_section("Organization Evaluation", org_result)
                            display_recruiter_details_streamlit("Recruiter Information",recruiter)
                        except Exception as e:
                            st.session_state.errors.append(f"OrgEvaluator failed: {e}")
                            st.session_state.agent_status["OrgEvaluator"] = "❌ Failed"
                            st.session_state.agent_status["GetRecruiter"] = "❌ Failed"

                    except Exception as e:
                        st.session_state.agent_status["JobInfoExtractor"] = "❌ Failed"
                        st.session_state.errors.append(f"JobInfoExtractor failed: {e}")

            except Exception as e:
                st.session_state.errors.append(f"Main workflow error: {e}")

# --------------------- Display Agent Status & Logs ---------------------
display_status(st.session_state.agent_status)
display_error_logs(st.session_state.errors)
