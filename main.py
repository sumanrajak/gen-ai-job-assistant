# main.py
import streamlit as st
from agents.job_extractor import JobInfoExtractor
from llm.perplexity import PerplexityLLM
from agents.fit_evaluator import FitEvaluatorAgent
from agents.email_generator import EmailGeneratorAgent
from agents.org_evaluater import OrgEvaluatorAgent
from utils.file_io import load_resume
from dotenv import load_dotenv
import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from llm.groq import GroqLLM

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

st.set_page_config(page_title="Job Auto Apply", layout="centered")

st.title("🚀 Job Auto Apply -/ LLM Assistant ")

# Input job URL
job_url = st.text_input("Enter Job Posting URL")

if st.button("Extract Job Details") and job_url:
    if not os.getenv("PERPLEXITY_API_KEY"):
        st.error("Perplexity API key not found. Please set PERPLEXITY_API_KEY in your .env file.")
        logging.error("Perplexity API key not found.")
    else:
        with st.spinner("Processing... This might take a moment..."):
            try:
                llmPRO = PerplexityLLM(api_key=os.getenv("PERPLEXITY_API_KEY"))
                llm=GroqLLM(api_key=os.getenv("GROQ_API_KEY"))
                job_agent = JobInfoExtractor(llm=llm)
                fit_agent = FitEvaluatorAgent(llm=llm)
                email_agent = EmailGeneratorAgent(llm=llm)
                org_agent = OrgEvaluatorAgent(llm=llmPRO)

                # Use ThreadPoolExecutor for concurrent execution
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_job_extraction = executor.submit(job_agent.run, job_url)

                    job_text, job_info = None, None
                    try:
                        job_text, job_info = future_job_extraction.result(timeout=300) # Add a timeout for extraction
                        st.subheader("Raw Job Description")
                        st.text_area("Job Text", job_text, height=200)
                        st.subheader("Structured Job Info")
                        st.json(job_info)

                        if job_info: # Only proceed with fit evaluation if job_info was successfully extracted
                            resume = load_resume()
                            if resume:
                                future_fit_evaluation = executor.submit(fit_agent.run, resume, job_info)
                                email_cover = executor.submit(email_agent.run, resume, job_info)
                                fit_report = None
                                try:
                                    fit_report = future_fit_evaluation.result(timeout=300) # Add a timeout for evaluation
                                    email_cover_result = email_cover.result(timeout=300) # Add a timeout for email generation
                                    org_evaluation = org_agent.run(job_info.get("company_name", "SAP"), job_info.get("location_country", "UAE"))
                                    st.subheader("Fit Evaluation Report")
                                    st.json(fit_report)
                                    st.subheader("Email and Cover Letter")
                                    st.json(email_cover_result)
                                    st.subheader("Organization Evaluation")
                                    st.json(org_evaluation)
                                except TimeoutError:
                                    st.error("Fit evaluation timed out. Please try again.")
                                    logging.error("Fit evaluation timed out for URL: %s", job_url)
                                except Exception as fit_eval_e:
                                    st.error(f"Error during fit evaluation: {fit_eval_e}")
                                    logging.exception("Error during fit evaluation for URL: %s", job_url)
                            else:
                                st.warning("No resume found. Please ensure 'resume.txt' is in the 'data' directory.")
                                logging.warning("No resume found when trying to evaluate fit for URL: %s", job_url)
                        else:
                            st.error("Could not extract structured job information. Fit evaluation skipped.")
                            logging.error("Could not extract structured job information for URL: %s", job_url)

                    except TimeoutError:
                        st.error("Job extraction timed out. Please check the URL and try again.")
                        logging.error("Job extraction timed out for URL: %s", job_url)
                    except Exception as job_extract_e:
                        st.error(f"Error during job extraction: {job_extract_e}")
                        logging.exception("Error during job extraction for URL: %s", job_url)

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                logging.exception("An unexpected error occurred in main execution.")