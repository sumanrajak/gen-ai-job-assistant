import json
import logging
from prompts.fit_evaluator_prompt import FIT_EVALUATOR_PROMPT_TEMPLATE, FIT_EVALUATOR_SCHEMA
from utils.prompt_runner import run_json_prompt
from app.schema.schema import FitEvaluatorSchema

class FitEvaluatorAgent:
    def __init__(self, llm):
        """
        Constructor for FitEvaluatorAgent.

        Args:
            llm (BaseLLM): A language model that can be used to evaluate the fit of a resume to a job description.

        Returns:
            None
        """
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
            "schema": json.dumps(FIT_EVALUATOR_SCHEMA, indent=2)
        }

        try:
            result = run_json_prompt(self.llm, FIT_EVALUATOR_PROMPT_TEMPLATE, prompt_inputs, FitEvaluatorSchema)
            return result
        except Exception as e:
            print(f"Error during fit evaluation: {e}")
            raise
