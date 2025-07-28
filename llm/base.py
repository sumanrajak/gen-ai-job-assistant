# llm/base.py
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    def call(self, prompt: str, response_schema: dict) -> str:
        pass
