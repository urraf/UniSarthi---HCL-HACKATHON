"""
One small helper to talk to the LLM.

Groq and Ollama both accept the same OpenAI-style request:
    POST <base_url>/chat/completions  {model, messages, ...}
so the only difference between them is the URL, the model name and the API key.

We always ask for JSON, because our code needs to read the answer reliably.
"""
import json
import os
import time

import requests

from app import config

GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MAX_ATTEMPTS = 3


class LLMError(Exception):
    """Raised when the LLM is switched off (mock mode) or keeps failing."""


def chat_json(system: str, user: str, temperature: float = 0.0) -> tuple[dict, dict]:
    """
    Send one prompt and return (parsed_json, usage).

    usage = {"calls": 1, "tokens": <total tokens>, "ms": <latency>, "model": <model that answered>}
    Retries if the reply is not valid JSON or the server is rate limiting us.
    Callers catch LLMError and fall back to simple rules.
    """
    if config.LLM_PROVIDER == "mock":
        raise LLMError("LLM_PROVIDER=mock: no LLM call made")

    if config.LLM_PROVIDER == "groq":
        if not config.GROQ_API_KEY:
            raise LLMError("GROQ_API_KEY is not set in backend/.env")
        url = f"{GROQ_BASE_URL}/chat/completions"
        headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}
        model = config.GROQ_MODEL
    elif config.LLM_PROVIDER == "ollama":
        url = f"{config.OLLAMA_URL}/v1/chat/completions"
        headers = {}
        model = config.OLLAMA_MODEL
    else:
        raise LLMError(f"Unknown LLM_PROVIDER: {config.LLM_PROVIDER}")

    models = [model] + (config.GROQ_FALLBACK_MODELS if config.LLM_PROVIDER == "groq" else [])
    for name in models:
        try:
            return _call(url, headers, name, system, user, temperature)
        except DailyLimit:
            continue  # this model's daily quota is used up: try the next one
        except LLMError:
            break     # Groq unreachable or still rate limited: go to the local model if allowed

    # Last resort: the local Ollama model (no quota, slower)
    if config.LLM_PROVIDER == "groq" and config.FALLBACK_TO_OLLAMA:
        return _call(f"{config.OLLAMA_URL}/v1/chat/completions", {}, config.OLLAMA_MODEL, system, user, temperature)
    raise LLMError("All configured models are over their limit or unavailable")


class DailyLimit(Exception):
    """The model's tokens-per-day quota is used up (waiting a few seconds will not help)."""


def _call(url: str, headers: dict, model: str, system: str, user: str, temperature: float) -> tuple[dict, dict]:
    body = {
        "model": model,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    usage = {"calls": 0, "tokens": 0, "ms": 0, "model": model}
    last_error = ""
    for _attempt in range(MAX_ATTEMPTS):
        start = time.time()
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=120)
            if resp.status_code == 429 and "per day" in resp.text:
                raise DailyLimit(model)
            if resp.status_code == 429:
                # Rate limited per minute (free tiers): wait as long as the server asks (max 30 s), then retry
                last_error = "rate limited (429)"
                time.sleep(min(float(resp.headers.get("retry-after", 2)), 30))
                continue
            resp.raise_for_status()
        except requests.RequestException as e:
            raise LLMError(f"LLM request failed: {e}") from e

        data = resp.json()
        usage["calls"] += 1
        usage["tokens"] += data.get("usage", {}).get("total_tokens", 0)
        usage["ms"] += int((time.time() - start) * 1000)

        text = data["choices"][0]["message"]["content"]
        try:
            return _parse_json(text), usage
        except ValueError as e:
            last_error = str(e)  # try once more

    raise LLMError(f"LLM failed after {MAX_ATTEMPTS} attempts: {last_error}")


def _parse_json(text: str) -> dict:
    """Parse JSON, even if the model wrapped it in extra text or ``` fences."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in reply")
    return json.loads(text[start : end + 1])
