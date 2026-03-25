import json
import os
import re
from hashlib import sha256

from openai import OpenAI


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
DEFAULT_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def _get_client() -> OpenAI | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def has_openai_client() -> bool:
    return _get_client() is not None


def _extract_json_object(raw_text: str) -> dict | None:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        payload = json.loads(match.group(0))
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        return None


def generate_text(prompt: str, fallback: str, system_prompt: str | None = None) -> str:
    client = _get_client()
    if client is None:
        return fallback

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                    or (
                        "You are Aurora, an adaptive fitness, nutrition, and recovery assistant. "
                        "Return practical, easy-to-understand wellness guidance. "
                        "Use plain language, clear structure, and include safety caveats when appropriate."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        message = response.choices[0].message.content
        return message.strip() if message else fallback
    except Exception:
        return fallback


def generate_json(prompt: str, fallback: dict, system_prompt: str | None = None) -> dict:
    client = _get_client()
    if client is None:
        return fallback

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                    or (
                        "You are Aurora, an adaptive fitness and nutrition AI. "
                        "Return valid JSON only. No markdown fences, no prose outside the JSON object."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        message = response.choices[0].message.content or ""
        payload = _extract_json_object(message)
        return payload if payload is not None else fallback
    except Exception:
        return fallback


def _local_embedding(text: str, dimensions: int = 32) -> list[float]:
    values = [0.0] * dimensions
    for index, token in enumerate(text.lower().split()):
        digest = sha256(f"{index}:{token}".encode("utf-8")).digest()
        for slot in range(dimensions):
            values[slot] += digest[slot] / 255.0
    norm = sum(value * value for value in values) ** 0.5
    if norm == 0:
        return values
    return [value / norm for value in values]


def embed_text(text: str) -> list[float]:
    client = _get_client()
    if client is None:
        return _local_embedding(text)

    try:
        response = client.embeddings.create(model=DEFAULT_EMBEDDING_MODEL, input=text)
        return response.data[0].embedding
    except Exception:
        return _local_embedding(text)
