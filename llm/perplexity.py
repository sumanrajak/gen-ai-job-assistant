# llm/perplexity.py
import requests
import re
import logging
from llm.base import BaseLLM

class PerplexityLLM(BaseLLM):
    def __init__(self, api_key: str, api_url: str = 'https://api.perplexity.ai/chat/completions'):
        self.api_key = api_key
        self.api_url = api_url

    def call(self, prompt: str, response_schema: dict) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        try:
            logging.info("Sending request to Perplexity API...")
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            # print(response.json().get("choices")[0].get("message").get("content"))
            answer = response.json().get("choices", [{}])[0].get("message").get("content")
            return self._extract_json(answer)
        except Exception as e:
            logging.error(f"Perplexity call failed: {e}")
            raise

    def _extract_json(self, text: str) -> str:
        match = re.search(r"<json>(.*?)</json>", text, re.DOTALL)
        return match.group(1).strip() if match else text
