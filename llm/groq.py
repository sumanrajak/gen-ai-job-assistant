from openai import OpenAI
from llm.base import BaseLLM
import re
import os

class GroqLLM(BaseLLM):
    def __init__(self, api_key: str = None, model: str = "llama3-70b-8192"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.api_key
        )
        self.model = model

    def call(self, prompt: str, response_schema: dict = None) -> str:
        if not self.api_key:
            raise ValueError("API key is required for GroqLLM")
        print("running groq llm")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        answer = response.choices[0].message.content
        print("groq llm response:", answer)
        return self._extract_json(answer)

    def _extract_json(self, text: str) -> str:
        match = re.search(r"<json>(.*?)</json>", text, re.DOTALL)
        return match.group(1).strip() if match else text
