"""Call a model and validate the guide it returns.

OpenAI is used through the chat-completions JSON mode. Anthropic is used
through a forced tool call, which is that API's structured-output path.
Both results are checked with the same Pydantic model. A validation failure
is sent back once. After that we stop, rather than shipping a guide that
does not match the schema.
"""

from __future__ import annotations

import json
import re
from typing import Awaitable, Callable

import httpx
from pydantic import ValidationError

from app.config import Settings
from app.pipeline.errors import ExtractionError
from app.pipeline.prompts import SYSTEM
from app.schema import GuideDraft

CompleteFn = Callable[[Settings, str, str], Awaitable[dict]]

_KEY_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{8,}|tvly-[A-Za-z0-9_\-]{8,}|key-[A-Za-z0-9_\-]{8,})")


async def complete_json(settings: Settings, system: str, user: str) -> dict:
    provider = settings.resolved_llm()
    if provider == "openai":
        return await _openai(settings, system, user)
    if provider == "anthropic":
        return await _anthropic(settings, system, user)
    raise ExtractionError("No LLM provider is configured.")


async def draft_from_model(
    settings: Settings,
    user: str,
    complete: CompleteFn = complete_json,
) -> GuideDraft:
    raw = await complete(settings, SYSTEM, user)
    try:
        return GuideDraft.model_validate(raw)
    except ValidationError as first:
        correction = (
            user
            + "\n\nYour previous JSON failed validation:\n"
            + _short_error(first)
            + "\nReturn corrected JSON only."
        )
        raw = await complete(settings, SYSTEM, correction)
        try:
            return GuideDraft.model_validate(raw)
        except ValidationError as second:
            raise ExtractionError(
                "The model did not return a guide that matched the schema. "
                + _short_error(second)
            ) from second


async def _openai(settings: Settings, system: str, user: str) -> dict:
    payload = {
        "model": settings.openai_model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }
    body = await _post_openai(settings, payload)
    choice = (body.get("choices") or [{}])[0]
    if choice.get("finish_reason") == "length":
        raise ExtractionError(
            f"OpenAI cut the guide off (model {settings.openai_model}). Try again."
        )
    message = choice.get("message") or {}
    content = message.get("content")
    if not content:
        raise ExtractionError("OpenAI returned an empty guide.")
    return _load_json(content)


async def _post_openai(settings: Settings, payload: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        # Some newer models reject max_tokens / temperature. We only set
        # temperature. If a model rejects it, retry once without it.
        if response.status_code == 400 and "temperature" in response.text:
            payload = {key: value for key, value in payload.items() if key != "temperature"}
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
    if response.status_code >= 400:
        raise ExtractionError(_http_error("OpenAI", settings.openai_model, response))
    return response.json()


async def _anthropic(settings: Settings, system: str, user: str) -> dict:
    payload = {
        "model": settings.anthropic_model,
        "max_tokens": 16000,
        "system": system,
        "tools": [
            {
                "name": "submit_guide",
                "description": "Submit the OAuth approval guide as structured fields.",
                "input_schema": {"type": "object"},
            }
        ],
        "tool_choice": {"type": "tool", "name": "submit_guide"},
        "messages": [{"role": "user", "content": user}],
    }
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key or "",
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
        )
    if response.status_code >= 400:
        raise ExtractionError(_http_error("Anthropic", settings.anthropic_model, response))
    body = response.json()
    if body.get("stop_reason") == "max_tokens":
        raise ExtractionError(
            f"Anthropic cut the guide off (model {settings.anthropic_model}). Try again."
        )
    for block in body.get("content") or []:
        if block.get("type") == "tool_use" and block.get("name") == "submit_guide":
            tool_input = block.get("input")
            if isinstance(tool_input, dict):
                return tool_input
            if isinstance(tool_input, str):
                return _load_json(tool_input)
        if block.get("type") == "text" and block.get("text"):
            try:
                return _load_json(block["text"])
            except ExtractionError:
                continue
    raise ExtractionError("Anthropic did not return a guide.")


def _load_json(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ExtractionError(f"The model did not return JSON ({exc}).") from exc
    if not isinstance(parsed, dict):
        raise ExtractionError("The model returned JSON that was not an object.")
    return parsed


def _http_error(provider: str, model: str, response: httpx.Response) -> str:
    detail = _KEY_RE.sub("[redacted]", response.text[:400].replace("\n", " "))
    if response.status_code in {401, 403}:
        return f"{provider} rejected the API key ({response.status_code}). Check the key in .env."
    if response.status_code == 404:
        return (
            f"{provider} does not recognize model {model}. "
            f"Set the model name in .env to one your key can call. {detail}"
        )
    return f"{provider} returned {response.status_code} for model {model}. {detail}"


def _short_error(exc: ValidationError) -> str:
    lines = []
    for error in exc.errors()[:8]:
        loc = ".".join(str(part) for part in error.get("loc", []))
        lines.append(f"{loc}: {error.get('msg')}")
    return "; ".join(lines)[:800]
