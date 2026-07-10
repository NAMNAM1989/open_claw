"""Lưu session eCargo từ Chrome đã đăng nhập — chạy trên máy dev."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.settings import settings


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Cần: pip install playwright && playwright install chromium")
        raise SystemExit(1)

    out = settings.ecargo_storage_path()
    if not out:
        print("Cấu hình ECARGO_STORAGE_STATE trong .env")
        raise SystemExit(1)
    out.parent.mkdir(parents=True, exist_ok=True)

    url = settings.ecargo_create_url
    print(f"Mở {url} — đăng nhập eCargo thủ công, rồi nhấn Enter…")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)
        input()
        context.storage_state(path=str(out))
        browser.close()
    print(f"Đã lưu session → {out}")


if __name__ == "__main__":
    main()
