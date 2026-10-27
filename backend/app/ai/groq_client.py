import urllib.error
import urllib.request
import json

from app.core.config import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
TIMEOUT_SECONDS = 20


class LLMError(RuntimeError):
    """Raised when the model cannot give a usable answer."""


def ask_model(system_prompt: str, user_prompt: str, max_tokens: int = 300) -> str:
    """Send one chat request to Groq and return the text reply."""
    if not settings.groq_api_key:
        raise LLMError("GROQ_API_KEY is not set.")
    body = json.dumps({
        "model": settings.groq_model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }).encode("utf-8")
    request = urllib.request.Request(
        GROQ_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "InterviewOS/0.1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read())
        return data["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as error:
        raise LLMError(f"Model call failed: {error}") from error