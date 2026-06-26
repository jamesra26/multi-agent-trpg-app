# Deepseek access layer
from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Literal, TypedDict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings

DEEPSEEK_CHAT_COMPLETIONS_PATH = "/chat/completions"

ChatRole = Literal["system", "user", "assistant", "tool"]


class ChatMessage(TypedDict):
    role: ChatRole
    content: str


class DeepSeekChatError(RuntimeError):
    """Raised when DeepSeek chat completion fails."""


def chat(
    prompt_or_messages: str | Sequence[ChatMessage],
    *,
    model: str | None = None,
    temperature: float = 0.7,
    timeout: float = 30.0,
) -> str:
    """Call DeepSeek Chat Completions and return the assistant text."""

    settings = get_settings()
    api_key = settings.deepseek_api_key.strip()
    if not api_key:
        raise DeepSeekChatError("DEEPSEEK_API_KEY is not configured.")

    payload = {
        "model": model or settings.deepseek_model,
        "messages": _normalize_messages(prompt_or_messages),
        "temperature": temperature,
    }
    request = Request(
        _chat_completions_url(settings.deepseek_base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        finally:
            exc.close()
        raise DeepSeekChatError(
            f"DeepSeek API request failed with status {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise DeepSeekChatError(f"DeepSeek API request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise DeepSeekChatError(f"DeepSeek API request timed out: {exc}") from exc

    try:
        data = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise DeepSeekChatError(
            f"Unexpected DeepSeek API response body: {response_body}"
        ) from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise DeepSeekChatError(f"Unexpected DeepSeek API response: {data}") from exc

    if not isinstance(content, str):
        raise DeepSeekChatError(f"Unexpected DeepSeek API content: {content!r}")
    return content


def _normalize_messages(prompt_or_messages: str | Sequence[ChatMessage]) -> list[ChatMessage]:
    if isinstance(prompt_or_messages, str):
        return [{"role": "user", "content": prompt_or_messages}]

    messages = list(prompt_or_messages)
    if not messages:
        raise DeepSeekChatError("At least one chat message is required.")
    return messages


def _chat_completions_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}{DEEPSEEK_CHAT_COMPLETIONS_PATH}"
