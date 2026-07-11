#!/usr/bin/env python3
"""Validate bot env before run."""
import sys

from core.settings import settings


def main() -> int:
    errors = []
    if not settings.telegram_bot_token:
        errors.append("TELEGRAM_BOT_TOKEN")
    if not settings.openclaw_gateway_token:
        errors.append("OPENCLAW_GATEWAY_TOKEN")
    if not settings.openclaw_base_url:
        errors.append("OPENCLAW_BASE_URL")
    if not settings.allowed_ids():
        errors.append("ALLOWED_CHAT_IDS (dùng /chatid rồi điền)")

    if errors:
        print("ERROR missing or empty:", ", ".join(errors))
        return 1

    print("OK config")
    return 0


if __name__ == "__main__":
    sys.exit(main())
