"""Kiểm tra cấu hình .env trước chạy bot production."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.settings import settings


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not settings.telegram_bot_token:
        errors.append("TELEGRAM_BOT_TOKEN missing")

    if not settings.supabase_url or not settings.supabase_service_role_key:
        warnings.append("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing - in-memory mode")

    if settings.ai_provider == "openclaw":
        if not settings.openclaw_base_url or not settings.openclaw_gateway_token:
            warnings.append("OPENCLAW_* missing - /ask and /gia vision will fail")

    if not settings.ecargo_dry_run:
        path = settings.ecargo_storage_path()
        if not path or not path.is_file():
            errors.append(f"ECARGO_DRY_RUN=false but missing {settings.ecargo_storage_state}")

    if settings.mail_watch_enabled and not (settings.gmail_user and settings.gmail_app_password):
        warnings.append("MAIL_WATCH_ENABLED but GMAIL_* missing")

    for w in warnings:
        print(f"WARN: {w}", file=sys.stdout)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)

    if errors:
        return 1
    print("OK - config ready (see WARN if any)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
