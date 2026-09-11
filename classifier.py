import json
import os

from groq import Groq

MODEL = "openai/gpt-oss-20b"
CATEGORIES = ("sales_lead", "support", "spam", "other")

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def _build_prompt(sender, subject, body_text, strict):
    instruction = (
        "Return ONLY JSON, no other text."
        if strict
        else "Respond with ONLY valid JSON (no markdown fences, no extra commentary)."
    )
    return (
        "You are an email classification assistant. Classify the email below into exactly one "
        f"category: {', '.join(CATEGORIES)}.\n\n"
        f"Sender: {sender}\n"
        f"Subject: {subject}\n"
        f"Body:\n{body_text}\n\n"
        f"{instruction}\n"
        'The JSON object must have exactly these keys: "category" (one of '
        f"{', '.join(CATEGORIES)}), "
        '"confidence" (a float between 0 and 1), and "reasoning" (one sentence explaining the classification).'
    )


def _request(client, sender, subject, body_text, strict):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": _build_prompt(sender, subject, body_text, strict)}],
            reasoning_format="parsed",
        )
        return response.choices[0].message.content
    except Exception:
        return None


def _parse(content):
    if not content:
        return None
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) and "category" in data else None


def classify_email(sender, subject, body_text):
    """Classify an email via Groq, retrying once with a stricter prompt if JSON parsing fails."""
    client = _get_client()
    for strict in (False, True):
        content = _request(client, sender, subject, body_text, strict)
        parsed = _parse(content)
        if parsed is not None:
            return parsed
    return {"category": "other", "confidence": 0.0, "reasoning": "classification failed"}
