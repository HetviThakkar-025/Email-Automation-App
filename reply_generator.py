import os

from groq import Groq

MODEL = "openai/gpt-oss-20b"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def _build_prompt(sender, subject, body_text):
    return (
        "You are a helpful sales assistant. Write a short, professional reply (3-5 sentences) "
        "to the email below. Acknowledge the sender's interest and propose a next step, such as "
        "a call, to move the conversation forward.\n\n"
        f"Sender: {sender}\n"
        f"Subject: {subject}\n"
        f"Body:\n{body_text}\n\n"
        "Reply with only the email reply text, no subject line and no commentary."
    )


def generate_reply(sender, subject, body_text):
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": _build_prompt(sender, subject, body_text)}],
        reasoning_format="parsed",
    )
    return response.choices[0].message.content
