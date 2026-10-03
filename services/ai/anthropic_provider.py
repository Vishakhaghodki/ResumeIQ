import requests

from .base import SYSTEM_PROMPT, AIProvider, build_prompt


class AnthropicProvider(AIProvider):
    name = "anthropic"
    is_live = True

    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model

    def generate_feedback(self, ctx):
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": self.model, "max_tokens": 1000, "system": SYSTEM_PROMPT,
                  "messages": [{"role": "user", "content": build_prompt(ctx)}]},
            timeout=45,
        )
        resp.raise_for_status()
        blocks = resp.json().get("content", [])
        return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
