from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, Literal, TypedDict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings

DEEPSEEK_CHAT_COMPLETIONS_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"

ChatRole = Literal["system", "user", "assistant", "tool"]


class ChatMessage(TypedDict):
    role: ChatRole
    content: str


class DeepSeekChatError(RuntimeError):
    """Raised when DeepSeek chat completion fails."""


def chat(
    prompt_or_messages: str | Sequence[ChatMessage],
    *,
    model: str = DEFAULT_DEEPSEEK_MODEL,
    temperature: float = 0.7,
    timeout: float = 30.0,
) -> str:
    """Call DeepSeek Chat Completions and return the assistant text."""

    api_key = get_settings().deepseek_api_key.strip()
    if not api_key:
        raise DeepSeekChatError("DEEPSEEK_API_KEY is not configured.")

    payload = {
        "model": model,
        "messages": _normalize_messages(prompt_or_messages),
        "temperature": temperature,
    }
    request = Request(
        DEEPSEEK_CHAT_COMPLETIONS_URL,
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
        detail = exc.read().decode("utf-8", errors="replace")
        raise DeepSeekChatError(
            f"DeepSeek API request failed with status {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise DeepSeekChatError(f"DeepSeek API request failed: {exc.reason}") from exc

    data = json.loads(response_body)
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
