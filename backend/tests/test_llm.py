# This test would use fake response to simulate the API response. NO REAL API CALLS.
from __future__ import annotations

import json
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

import pytest

from app.core import llm


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body

    def close(self) -> None:
        return None


class FakeTextResponse:
    def __init__(self, body: str) -> None:
        self._body = body.encode("utf-8")

    def __enter__(self) -> FakeTextResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def patch_settings(
    monkeypatch: pytest.MonkeyPatch,
    *,
    api_key: str = "test-key",
    base_url: str = "https://api.deepseek.test",
    model: str = "deepseek-test-default",
) -> None:
    monkeypatch.setattr(
        llm,
        "get_settings",
        lambda: SimpleNamespace(
            deepseek_api_key=api_key,
            deepseek_base_url=base_url,
            deepseek_model=model,
        ),
    )


def test_chat_sends_prompt_and_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_settings(monkeypatch)
    captured: dict[str, object] = {}

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse({"choices": [{"message": {"content": "OK"}}]})

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    result = llm.chat("hello", model="deepseek-test", temperature=0, timeout=3)

    request = captured["request"]
    payload = json.loads(request.data.decode("utf-8"))
    assert result == "OK"
    assert captured["timeout"] == 3
    assert request.full_url == "https://api.deepseek.test/chat/completions"
    assert request.get_method() == "POST"
    assert request.get_header("Authorization") == "Bearer test-key"
    assert request.get_header("Content-type") == "application/json"
    assert payload == {
        "model": "deepseek-test",
        "messages": [{"role": "user", "content": "hello"}],
        "temperature": 0,
    }


def test_chat_uses_default_parameters_and_handles_chinese(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_settings(monkeypatch, model="deepseek-configured-model")
    captured: dict[str, object] = {}

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse({"choices": [{"message": {"content": "收到，开始冒险"}}]})

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    result = llm.chat("进入酒馆")

    request = captured["request"]
    payload = json.loads(request.data.decode("utf-8"))
    assert result == "收到，开始冒险"
    assert captured["timeout"] == 30.0
    assert payload == {
        "model": "deepseek-configured-model",
        "messages": [{"role": "user", "content": "进入酒馆"}],
        "temperature": 0.7,
    }


def test_chat_builds_url_from_base_url_without_duplicate_slash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_settings(monkeypatch, base_url="https://api.deepseek.test/")
    captured: dict[str, object] = {}

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        captured["request"] = request
        return FakeResponse({"choices": [{"message": {"content": "OK"}}]})

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    llm.chat("hello")

    assert captured["request"].full_url == "https://api.deepseek.test/chat/completions"


def test_chat_trims_api_key_before_authorization_header(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_settings(monkeypatch, api_key=" test-key ")
    captured: dict[str, object] = {}

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        captured["request"] = request
        return FakeResponse({"choices": [{"message": {"content": "OK"}}]})

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    llm.chat("hello")

    assert captured["request"].get_header("Authorization") == "Bearer test-key"


def test_chat_accepts_standard_messages_boundaries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_settings(monkeypatch)
    messages: list[llm.ChatMessage] = [
        {"role": "system", "content": "answer briefly"},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "上一轮行动"},
        {"role": "tool", "content": "骰点结果: 18"},
    ]
    captured_payload: dict[str, object] = {}

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        captured_payload.update(json.loads(request.data.decode("utf-8")))
        return FakeResponse({"choices": [{"message": {"content": "继续行动"}}]})

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    result = llm.chat(messages)

    assert result == "继续行动"
    assert captured_payload["messages"] == messages


def test_chat_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_settings(monkeypatch, api_key="   ")

    with pytest.raises(llm.DeepSeekChatError, match="DEEPSEEK_API_KEY"):
        llm.chat("hello")


def test_chat_requires_at_least_one_message(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_settings(monkeypatch)

    with pytest.raises(llm.DeepSeekChatError, match="At least one chat message"):
        llm.chat([])


def test_chat_wraps_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_settings(monkeypatch)

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        raise HTTPError(
            url="https://api.deepseek.test/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=FakeResponse({"error": {"message": "bad key"}}),
        )

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    with pytest.raises(llm.DeepSeekChatError, match="status 401"):
        llm.chat("hello")


def test_chat_wraps_url_error(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_settings(monkeypatch)

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        raise URLError("network down")

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    with pytest.raises(llm.DeepSeekChatError, match="network down"):
        llm.chat("hello")


def test_chat_wraps_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_settings(monkeypatch)

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        raise TimeoutError("timed out")

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    with pytest.raises(llm.DeepSeekChatError, match="timed out"):
        llm.chat("hello")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"choices": None},
        {"choices": []},
        {"choices": [{}]},
        {"choices": [{"message": {}}]},
        {"choices": [{"message": None}]},
    ],
)
def test_chat_rejects_unexpected_response(
    monkeypatch: pytest.MonkeyPatch,
    payload: object,
) -> None:
    patch_settings(monkeypatch)

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        return FakeResponse(payload)

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    with pytest.raises(llm.DeepSeekChatError, match="Unexpected DeepSeek API response"):
        llm.chat("hello")


def test_chat_rejects_non_json_response_body(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_settings(monkeypatch)

    def fake_urlopen(request: object, timeout: float) -> FakeTextResponse:
        return FakeTextResponse("not json")

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    with pytest.raises(llm.DeepSeekChatError, match="Unexpected DeepSeek API response body"):
        llm.chat("hello")


@pytest.mark.parametrize("payload", [None, [], "ok"])
def test_chat_rejects_json_response_with_wrong_top_level_type(
    monkeypatch: pytest.MonkeyPatch,
    payload: object,
) -> None:
    patch_settings(monkeypatch)

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        return FakeResponse(payload)

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    with pytest.raises(llm.DeepSeekChatError, match="Unexpected DeepSeek API response"):
        llm.chat("hello")


def test_chat_rejects_non_string_content(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_settings(monkeypatch)

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        return FakeResponse({"choices": [{"message": {"content": 123}}]})

    monkeypatch.setattr(llm, "urlopen", fake_urlopen)

    with pytest.raises(llm.DeepSeekChatError, match="Unexpected DeepSeek API content"):
        llm.chat("hello")
