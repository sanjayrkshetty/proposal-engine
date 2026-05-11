"""Base Agent — abstract base class for all Proposal Engine agents using Groq."""
import os
import json
from abc import ABC, abstractmethod
from groq import Groq

MODEL_FAST = "llama-3.1-8b-instant"   # fast, low tokens — questionnaire, discovery, scoping
MODEL_PRO  = "llama-3.3-70b-versatile" # quality — proposal only


class BaseAgent(ABC):
    """Abstract base for all Proposal Engine agents."""

    def __init__(self, service_config: dict):
        self.config = service_config
        api_key = os.environ.get("GROQ_API_KEY", "")
        self.client = Groq(api_key=api_key)
        self.model = MODEL_FAST  # default fast; ProposalAgent overrides to MODEL_PRO

    def call_llm(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.2) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    def call_llm_json(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.2) -> dict:
        raw = self.call_llm(prompt, max_tokens=max_tokens, temperature=temperature)
        if raw.startswith("```"):
            lines = raw.split("\n")
            inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            raw = "\n".join(inner)
        return json.loads(raw)

    @abstractmethod
    def run(self, *args, **kwargs) -> dict:
        pass
