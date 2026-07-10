from __future__ import annotations

from pathlib import Path

import yaml

_CONFIG = Path(__file__).resolve().parents[2] / "config" / "ecargo_errors.yaml"
_CACHE: dict | None = None


def _load() -> dict:
    global _CACHE
    if _CACHE is None:
        with _CONFIG.open(encoding="utf-8") as f:
            _CACHE = yaml.safe_load(f) or {}
    return _CACHE


def format_user_error(raw: str) -> str:
    text = (raw or "").lower()
    catalog = _load()
    for _key, entry in catalog.items():
        if _key == "generic":
            continue
        for needle in entry.get("match", []):
            if needle.lower() in text:
                return str(entry.get("user_message", "")).strip()
    generic = catalog.get("generic", {})
    return str(generic.get("user_message", "Lỗi eCargo.")).strip()


def is_session_error(raw: str) -> bool:
    text = (raw or "").lower()
    for needle in _load().get("session_expired", {}).get("match", []):
        if needle.lower() in text:
            return True
    return False
