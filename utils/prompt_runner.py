# utils/prompt_runner.py
from langchain_core.prompts import ChatPromptTemplate
import json
import logging

def run_json_prompt(llm, template_str: str, input_vars: dict, response_schema: dict) -> dict:
    try:
        prompt = ChatPromptTemplate.from_template(template_str).format_prompt(**input_vars).to_string()
        raw_result = llm.call(prompt, response_schema)
        # print(raw_result,prompt )
        return json.loads(raw_result)
    except Exception as e:
        logging.error(f"Prompt execution failed: {e}")
        raise
