import json

import pytest

from core.chat_memory import ChatSessions
from core.openclaw_client import OpenClawClient


@pytest.mark.asyncio
async def test_chat_parses_response(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="http://gw.test/v1/chat/completions",
        json={"choices": [{"message": {"content": "Xin chào"}}]},
    )
    client = OpenClawClient(base_url="http://gw.test/v1", token="tok", timeout=5.0)
    out = await client.chat(123, "hi")
    assert out == "Xin chào"
    body = json.loads(httpx_mock.get_request().content)
    assert body["user"] == "tg:123"
    assert body["max_tokens"] == 250
    assert len(body["messages"]) == 1


@pytest.mark.asyncio
async def test_chat_clips_long_input(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="http://gw.test/v1/chat/completions",
        json={"choices": [{"message": {"content": "ok"}}]},
    )
    client = OpenClawClient(base_url="http://gw.test/v1", token="tok", timeout=5.0)
    await client.chat(1, "x" * 5000)
    body = json.loads(httpx_mock.get_request().content)
    assert len(body["messages"][0]["content"]) <= 1500


@pytest.mark.asyncio
async def test_chat_uses_session_user_key(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="http://gw.test/v1/chat/completions",
        json={"choices": [{"message": {"content": "ok"}}]},
    )
    client = OpenClawClient(base_url="http://gw.test/v1", token="tok", timeout=5.0)
    await client.chat(1, "tôi tên gì?", user="tg:1:2")
    body = json.loads(httpx_mock.get_request().content)
    assert body["user"] == "tg:1:2"


@pytest.mark.asyncio
async def test_chat_vision_isolated_session(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url="http://gw.test/v1/chat/completions",
        json={"choices": [{"message": {"content": "MAWB 123"}}]},
    )
    client = OpenClawClient(base_url="http://gw.test/v1", token="tok", timeout=5.0)
    out = await client.chat_vision(99, "đọc MAWB", b"fake")
    assert out == "MAWB 123"
    body = json.loads(httpx_mock.get_request().content)
    assert body["user"] == "tg:99:vision"
    assert body["max_tokens"] <= 300
    assert body["messages"][0]["content"][1]["type"] == "image_url"


def test_session_clear_bumps_epoch():
    s = ChatSessions(ttl_seconds=3600)
    assert s.user_key(1) == "tg:1"
    s.clear(1)
    assert s.user_key(1) == "tg:1:1"


def test_session_ttl_expires(monkeypatch):
    s = ChatSessions(ttl_seconds=10)
    clock = {"t": 100.0}
    monkeypatch.setattr("core.chat_memory.time.monotonic", lambda: clock["t"])
    s.clear(7)
    assert s.user_key(7) == "tg:7:1"
    clock["t"] = 120.0
    assert s.user_key(7) == "tg:7"
