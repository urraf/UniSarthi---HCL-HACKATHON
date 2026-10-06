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


class LLMError(Exception):
    """Raised when the LLM is switched off (mock mode) or keeps failing."""


def chat_json(system: str, user: str, temperature: float = 0.0) -> tuple[dict, dict]:
    """
    Send one prompt and return (parsed_json, usage).

    usage = {"calls": 1, "tokens": <total tokens>, "ms": <latency>}
    Retries once if the reply is not valid JSON.
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

    body = {
        "model": model,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    usage = {"calls": 0, "tokens": 0, "ms": 0}
    last_error = ""
    for _attempt in range(2):
        start = time.time()
        try:
            resp = requests.post(url, json=body, headers=headers, timeout=120)
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

    raise LLMError(f"LLM did not return valid JSON: {last_error}")


def _parse_json(text: str) -> dict:
    """Parse JSON, even if the model wrapped it in extra text or ``` fences."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in reply")
    return json.loads(text[start : end + 1])
