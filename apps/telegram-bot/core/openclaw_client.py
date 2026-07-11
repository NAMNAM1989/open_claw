from __future__ import annotations

import base64

import httpx

from core.settings import settings

_DEFAULT_MAX_TOKENS = 250
_MAX_USER_CHARS = 1500


def _friendly_error(status: int, body: str) -> str:
    text = body.lower()
    if status == 429 or "quota" in text or "rate_limit" in text or "resource_exhausted" in text:
        return (
            "LLM tạm hết quota (429). Gateway đang thử ChatGPT/DeepSeek — "
            "đợi 1–2 phút rồi hỏi lại."
        )
    if "unknown model" in text or "model_not_found" in text:
        return "Cấu hình model fallback lỗi — kiểm tra gateway (OpenAI/DeepSeek)."
    if status >= 500:
        return "OpenClaw gateway lỗi tạm thời — thử lại sau."
    return f"OpenClaw lỗi HTTP {status}"


def _clip(text: str, limit: int = _MAX_USER_CHARS) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


class OpenClawClient:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float | None = None,
        agent_id: str | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self._base = (base_url or settings.openclaw_base_url).rstrip("/")
        self._token = token or settings.openclaw_gateway_token
        self._timeout = timeout if timeout is not None else settings.openclaw_timeout
        self._agent_id = agent_id or settings.openclaw_agent_id
        self._max_tokens = max_tokens if max_tokens is not None else _DEFAULT_MAX_TOKENS

    async def health_ok(self) -> bool:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self._base}/models",
                headers={"Authorization": f"Bearer {self._token}"},
            )
            return r.status_code == 200

    async def chat(
        self,
        chat_id: int,
        text: str,
        *,
        user: str | None = None,
        max_chars: int | None = None,
    ) -> str:
        limit = max_chars if max_chars is not None else _MAX_USER_CHARS
        return await self._complete(
            user or f"tg:{chat_id}",
            [{"role": "user", "content": _clip(text, limit)}],
        )

    async def chat_vision(
        self,
        chat_id: int,
        caption: str,
        image_bytes: bytes,
        mime: str = "image/jpeg",
        *,
        user: str | None = None,
    ) -> str:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        prompt = _clip(caption.strip() or "Trích thông tin chính từ ảnh (ngắn).", 400)
        # Session riêng cho ảnh — không kéo transcript chat dài + ảnh vào cùng context
        vision_user = user or f"tg:{chat_id}:vision"
        user_content = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            },
        ]
        return await self._complete(
            vision_user,
            [{"role": "user", "content": user_content}],
            max_tokens=min(self._max_tokens, 300),
        )

    async def _complete(
        self,
        user: str,
        messages: list[dict],
        max_tokens: int | None = None,
    ) -> str:
        payload = {
            "model": f"openclaw/{self._agent_id}",
            "user": user,
            "messages": messages,
            "max_tokens": max_tokens if max_tokens is not None else self._max_tokens,
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                r = await client.post(
                    f"{self._base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._token}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if r.status_code >= 400:
                    raise RuntimeError(_friendly_error(r.status_code, r.text))
                data = r.json()
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "OpenClaw phản hồi quá lâu (timeout). Thử câu hỏi ngắn hơn."
            ) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Không kết nối được OpenClaw: {exc}") from exc

        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError("OpenClaw không trả lời (thiếu choices)")
        message = choices[0].get("message") or {}
        content = message.get("content")
        if not content:
            raise RuntimeError("OpenClaw không trả lời (nội dung trống)")
        return str(content).strip()
