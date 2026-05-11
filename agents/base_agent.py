"""Base Agent — abstract base class for all SISA agents using Groq."""
import os
import json
from abc import ABC, abstractmethod
from groq import Groq

# Inject API key at module load time
os.environ.setdefault("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")

MODEL_FAST = "llama-3.1-8b-instant"   # fast, low tokens — questionnaire, discovery, scoping
MODEL_PRO  = "llama-3.3-70b-versatile" # quality — proposal only


class BaseAgent(ABC):
    """Abstract base for all SISA proposal-engine agents."""

    def __init__(self, service_config: dict):
        self.config = service_config
        api_key = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
        self.client = Groq(api_key=api_key)
        self.model = MODEL_FAST  # default fast; proposal_agent overrides to MODEL_PRO

    def call_llm(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.2) -> str:
        """Call Groq LLM and return raw text response."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    def call_llm_json(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.2) -> dict:
        """Call LLM and parse JSON response. Strips markdown code fences if present."""
        raw = self.call_llm(prompt, max_tokens=max_tokens, temperature=temperature)
        # Strip markdown code fences
        if raw.startswith("```"):
            lines = raw.split("\n")
            # Remove first line (```json or ```) and last line (```)
            inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            raw = "\n".join(inner)
        return json.loads(raw)

    @abstractmethod
    def run(self, *args, **kwargs) -> dict:
        """Execute agent pipeline. Returns dict with at minimum 'data' and 'markdown' keys."""
        pass
