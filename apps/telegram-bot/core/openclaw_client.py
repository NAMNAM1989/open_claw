from __future__ import annotations

import base64
import json
import logging
import re
import time
from typing import Any

import httpx

from core.settings import settings

log = logging.getLogger("namnam.openclaw")


class OpenClawError(RuntimeError):
    pass


class OpenClawClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._base = (base_url or settings.openclaw_base_url).rstrip("/")
        self._token = token or settings.openclaw_gateway_token
        self._timeout = timeout or settings.openclaw_timeout
        self._vision_timeout = settings.openclaw_vision_timeout

    @property
    def configured(self) -> bool:
        return bool(self._base and self._token)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def health_check(self) -> tuple[bool, str]:
        if not self.configured:
            return False, "Chưa cấu hình OPENCLAW_BASE_URL / OPENCLAW_GATEWAY_TOKEN"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(f"{self._base}/models", headers=self._headers())
                if resp.status_code == 200 and "openclaw" in resp.text.lower():
                    return True, "OpenClaw Gateway OK"
                return False, f"models HTTP {resp.status_code}"
        except Exception as exc:
            return False, str(exc)

    def chat(
        self,
        prompt: str,
        *,
        system: str = "",
        user_key: str = "tg:bot",
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        content = self._chat_completion(
            messages=self._build_messages(prompt, system=system),
            user_key=user_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self._timeout,
        )
        return content

    def chat_vision(
        self,
        image_bytes: bytes,
        prompt: str,
        *,
        mime_type: str = "image/jpeg",
        system: str = "",
        user_key: str = "tg:bot",
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> str:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        data_url = f"data:{mime_type};base64,{b64}"
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        )
        return self._chat_completion(
            messages=messages,
            user_key=user_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self._vision_timeout,
        )

    def _build_messages(self, prompt: str, *, system: str = "") -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        user_key: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
    ) -> str:
        if not self.configured:
            raise OpenClawError("OpenClaw chưa cấu hình")

        payload = {
            "model": f"openclaw/{settings.openclaw_agent_id}",
            "user": user_key,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(
                    f"{self._base}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            raise OpenClawError(f"OpenClaw HTTP lỗi: {exc}") from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        log.info("openclaw chat_ok latency_ms=%s", latency_ms)

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenClawError(f"OpenClaw response invalid: {json.dumps(data)[:200]}") from exc


_client: OpenClawClient | None = None


def get_openclaw_client() -> OpenClawClient:
    global _client
    if _client is None:
        _client = OpenClawClient()
    return _client


def reset_openclaw_client() -> None:
    global _client
    _client = None
