# agents/job_extractor.py
from bs4 import BeautifulSoup
import requests
import logging
import json
from prompts.job_info_prompt import JOB_INFO_SCHEMA, JOB_INFO_PROMPT_TEMPLATE
from utils.prompt_runner import run_json_prompt

class JobInfoExtractor:
    def __init__(self, llm):
        self.llm = llm

    def scrape_job_page(self, url: str) -> str:
        print(f"Scraping job page: {url}")
        logging.info(f"Scraping job page: {url}")
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup.body.get_text(separator="\n", strip=True) if soup.body else ""
        except Exception as e:
            logging.error(f"Error scraping job page: {e}")
            return ""

    def run(self, url: str) -> tuple:
        job_text = self.scrape_job_page(url)
        if not job_text:
            raise ValueError("Job page could not be scraped.")
        job_info = run_json_prompt(self.llm, JOB_INFO_PROMPT_TEMPLATE, {
            "job_text": job_text,
            "job_info_schema": json.dumps(JOB_INFO_SCHEMA),
            "url": url
        }, JOB_INFO_SCHEMA)
        return job_text, job_info
