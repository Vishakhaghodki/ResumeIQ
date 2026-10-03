"""AI provider factory. To add a provider: subclass AIProvider and return it from get_provider()."""
import logging

from .anthropic_provider import AnthropicProvider
from .demo_provider import DemoProvider
from .openai_provider import OpenAIProvider

log = logging.getLogger(__name__)


def get_provider(cfg):
    choice = cfg.get("AI_PROVIDER", "auto")
    if choice in ("anthropic", "auto") and cfg.get("ANTHROPIC_API_KEY"):
        return AnthropicProvider(cfg["ANTHROPIC_API_KEY"], cfg["ANTHROPIC_MODEL"])
    if choice in ("openai", "auto") and cfg.get("OPENAI_API_KEY"):
        return OpenAIProvider(cfg["OPENAI_API_KEY"], cfg["OPENAI_MODEL"], cfg["OPENAI_BASE_URL"])
    return DemoProvider()


def ai_status(cfg):
    p = get_provider(cfg)
    return {"mode": "live" if p.is_live else "demo", "provider": p.name}


def generate_feedback(cfg, ctx):
    """Returns {'text', 'mode', 'provider'}. Falls back to demo mode if the live call fails."""
    provider = get_provider(cfg)
    if provider.is_live:
        try:
            text = provider.generate_feedback(ctx)
            if text:
                return {"text": text, "mode": "live", "provider": provider.name}
        except Exception as exc:  # network error, bad key, rate limit...
            log.warning("AI provider %s failed (%s); using demo fallback", provider.name, exc)
    text = DemoProvider().generate_feedback(ctx)
    return {"text": text, "mode": "demo", "provider": "demo"}
