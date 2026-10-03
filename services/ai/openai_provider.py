import requests

from .base import SYSTEM_PROMPT, AIProvider, build_prompt


class OpenAIProvider(AIProvider):
    """Works with OpenAI and any OpenAI-compatible endpoint."""

    name = "openai"
    is_live = True

    def __init__(self, api_key, model, base_url):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate_feedback(self, ctx):
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": self.model, "max_tokens": 1000,
                  "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                               {"role": "user", "content": build_prompt(ctx)}]},
            timeout=45,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
