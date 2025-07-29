import json
import logging
from prompts.email_cover_prompt import EMAIL_COVER_SCHEMA, EMAIL_COVER_TEMPLATE
from utils.prompt_runner import run_json_prompt

class EmailGeneratorAgent:
    def __init__(self, llm):
        """
        Initialize the EmailGeneratorAgent with a language model.

        Args:
            llm (BaseLLM): A language model instance used by the agent for generating emails.
        """
        # Set the language model for the agent
        self.llm = llm

    def run(self, resume: str, job_info: dict) -> dict:
        """
        Evaluate the fit of a resume to a job description.

        Args:
            resume (str): The text of the resume.
            job_info (dict): A dictionary containing information about the job.

        Returns:
            dict: A dictionary containing the fit score and skills matched/missing.

        """
        print("Running FitEvaluatorAgent...")

        prompt_inputs = {
            "resume": resume,
            "job_info": json.dumps(job_info, indent=2),
            "schema": json.dumps(EMAIL_COVER_SCHEMA, indent=2)
        }

        try:
            result = run_json_prompt(self.llm, EMAIL_COVER_TEMPLATE, prompt_inputs, EMAIL_COVER_SCHEMA)
            print("email and cover letter generated successfully.", result)
            return result
        except Exception as e:
            print(f"Error during email and cover letter generation: {e}")
            raise
