# app/api/master_orchestrator.py

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from app.schema.schema import (
    EmailCoverSchema,
    FitEvaluatorSchema,
    JobInfoSchema,
    OrgEvaluatorSchema
)
import sys
from pathlib import Path

# Add the parent directory of 'core' to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))


from agents.job_extractor import JobInfoExtractor
from agents.fit_evaluator import FitEvaluatorAgent
from agents.org_evaluater import OrgEvaluatorAgent
from agents.email_generator import EmailGeneratorAgent
from agents.get_recruiter_agent import GetRecruiterAgent
from llm.groq import GroqLLM
from llm.perplexity import PerplexityLLM
from utils.file_io import load_resume
from core.config import settings


def run_all_agents_sync(job_description: str) -> dict:
    result = {
        "job_info": None,
        "fit_eval": None,
        "email_cover": None,
        "org_eval": None,
        "recruiters": None,
        "errors": []
    }

    try:
        perplexity_llm = PerplexityLLM(api_key=settings.PERPLEXITY_API_KEY)
        groq_llm = GroqLLM(api_key=settings.GROQ_API_KEY)

        job_agent = JobInfoExtractor(llm=groq_llm)
        fit_agent = FitEvaluatorAgent(llm=groq_llm)
        email_agent = EmailGeneratorAgent(llm=groq_llm)
        org_agent = OrgEvaluatorAgent(llm=perplexity_llm)
        recruiter_agent = GetRecruiterAgent(llm=perplexity_llm)

        resume = load_resume()
        if not resume:
            raise ValueError("No resume found. Please ensure 'data/resume.txt' exists.")

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_job = executor.submit(job_agent.run, job_description)
            job_text, job_info = future_job.result(timeout=120)
            result["job_info"] = JobInfoSchema(**job_info)

            # Run rest in parallel
            fit_future = executor.submit(fit_agent.run, resume, job_info)
            email_future = executor.submit(email_agent.run, resume, job_info)
            org_future = executor.submit(org_agent.run, job_info.get("company_name", ""), job_info.get("location_country", ""))
            recruiter_future = executor.submit(recruiter_agent.run, job_info.get("company_name", ""), job_info.get("location_country", ""))

            result["fit_eval"] = FitEvaluatorSchema(**fit_future.result(timeout=120))
            result["email_cover"] = EmailCoverSchema(**email_future.result(timeout=120))
            result["org_eval"] = OrgEvaluatorSchema(**org_future.result(timeout=120))
            result["recruiters"] = recruiter_future.result(timeout=120)

    except TimeoutError as te:
        logging.error(f"Agent timed out: {te}")
        result["errors"].append(f"Agent timed out: {str(te)}")
    except Exception as e:
        logging.exception("Error running agents")
        result["errors"].append(str(e))

    return result
