from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ChatSessions:
    """Session key theo chat — tránh gửi history trùng với OpenClaw session."""

    ttl_seconds: float = 24 * 3600
    _epoch: dict[int, int] = field(default_factory=dict)
    _touched: dict[int, float] = field(default_factory=dict)

    def user_key(self, chat_id: int) -> str:
        self._expire(chat_id)
        epoch = self._epoch.get(chat_id, 0)
        self._touched[chat_id] = time.monotonic()
        if epoch:
            return f"tg:{chat_id}:{epoch}"
        return f"tg:{chat_id}"

    def clear(self, chat_id: int) -> None:
        """Bắt đầu session mới (gateway không còn dùng transcript cũ)."""
        self._epoch[chat_id] = self._epoch.get(chat_id, 0) + 1
        self._touched[chat_id] = time.monotonic()

    def _expire(self, chat_id: int) -> None:
        touched = self._touched.get(chat_id)
        if touched is None:
            return
        if time.monotonic() - touched > self.ttl_seconds:
            self._epoch.pop(chat_id, None)
            self._touched.pop(chat_id, None)


sessions = ChatSessions()
