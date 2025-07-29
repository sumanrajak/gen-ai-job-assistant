import json
import logging
from prompts.org_evaluater_prompt import ORG_EVALUATER_SCHEMA, ORG_EVALUATER_PROMPT
from utils.prompt_runner import run_json_prompt

class OrgEvaluatorAgent:
    def __init__(self, llm):
        """
        Constructor for FitEvaluatorAgent.

        Args:
            llm (BaseLLM): A language model that can be used to evaluate the fit of a resume to a job description.

        Returns:
            None
        """
        self.llm = llm

    def run(self, company_name: str, location: str) -> dict:
        """
        Evaluate the fit of a resume to a job description.

        Args:
            resume (str): The text of the resume.
            job_info (dict): A dictionary containing information about the job.

        Returns:
            dict: A dictionary containing the fit score and skills matched/missing.

        """
        print("Running OrgEvaluatorAgent...")

        prompt_inputs = {
            "company_name": company_name,
            "location": location,
            "schema": json.dumps(ORG_EVALUATER_SCHEMA, indent=2)
        }

        try:
            result = run_json_prompt(self.llm, ORG_EVALUATER_PROMPT, prompt_inputs, ORG_EVALUATER_SCHEMA)
            print("Fit evaluation completed successfully.", result)
            return result
        except Exception as e:
            print(f"Error during fit evaluation: {e}")
            raise
