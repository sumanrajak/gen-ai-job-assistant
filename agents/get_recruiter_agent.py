import json
import logging
from prompts.get_recruiter_prompt import GET_RECRUITER_SCHEMA, GET_RECRUITER_PROMPT
from utils.prompt_runner import run_json_prompt



import requests
from googlesearch import search # Import the search function from googlesearch-python

def google_search_top(query):
    """
    Performs a Google search for the given query using the googlesearch-python package
    and returns the top 5 result URLs.

    Args:
        query (str): The search query string.

    Returns:
        list: A list of the top 5 Google search result URLs.
              Returns an empty list if no results are found or an error occurs.
    """
    try:
        # Use the search function from googlesearch-python
        # num_results specifies the number of results to retrieve
        top_results = list(search(query, num_results=10))
        return top_results
    except Exception as e:
        print(f"An error occurred during search: {e}")
        return []
class GetRecruiterAgent:
    def __init__(self, llm):
        """
        Constructor for GetRecruiterAgent.

        Args:
            llm (BaseLLM): A language model that can be used to evaluate the fit of a resume to a job description.

        Returns:
            None
        """
        self.llm = llm

    def run(self, company_name: str, location: str) -> dict:
        """
        get_recruiter_agent: Searches for recruiter information for a given company and location.

        Args:
            company_name (str): The text of the resume.
            location (dict): A dictionary containing information about the job.

        Returns:
            dict: A dictionary containing the fit score and skills matched/missing.

        """
        print("Running recruiter agent...")
        # search_query = f'site:linkedin.com/in/ OR site:linkedin.com/pub/ (hiring manager OR recruiter) "{company_name}" "{location}"'
        # print(f"Searching for: {search_query}")
        # top_results = google_search_top(search_query)



        
        prompt_inputs = {
            "company_name": company_name,
            "location": location,
            "schema": json.dumps(GET_RECRUITER_SCHEMA, indent=2)
        }

        try:
            result = run_json_prompt(self.llm, GET_RECRUITER_PROMPT, prompt_inputs,GET_RECRUITER_SCHEMA)
            top_results = google_search_top(result.get("search_query", ""))

            return top_results
        except Exception as e:
            print(f"Error during get_recruiter_agent: {e}")
            raise
