from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from uuid import uuid4

from core.settings import settings
from plugins.ops.arrival_rules import compute_arrival
from plugins.ops.error_catalog import is_session_error
from plugins.ops.models import Booking, JobResult
from plugins.ops.session_health import check_ecargo_session

log = logging.getLogger("namnam.ecargo")


class EcargoBackend(ABC):
    @abstractmethod
    def create_vct(self, booking: Booking) -> JobResult:
        ...


class DryRunEcargoBackend(EcargoBackend):
    """Dev/CI — không mở browser."""

    def create_vct(self, booking: Booking) -> JobResult:
        arrival = compute_arrival()
        reg = f"DRY{uuid4().hex[:6].upper()}"
        log.info(
            "DRY RUN eCargo %s %s arrival %s %s",
            booking.mawb,
            booking.vehicle_no,
            arrival.date_str,
            arrival.time_str,
        )
        return JobResult(
            registration_no=reg,
            vct_number=f"VCT-{reg}",
            status_text="dry_run_ok",
            verify_code="DRY-VERIFY",
        )


class PlaywrightEcargoBackend(EcargoBackend):
    """Playwright thật — cần session + selectors."""

    def __init__(self) -> None:
        self._storage = settings.ecargo_storage_path()

    def create_vct(self, booking: Booking) -> JobResult:
        from playwright.sync_api import sync_playwright

        arrival = compute_arrival()
        url = settings.ecargo_create_url
        if not self._storage or not self._storage.is_file():
            raise RuntimeError("eCargo chưa đăng nhập — save_ecargo_session")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state=str(self._storage))
            page = context.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                if "login" in page.url.lower():
                    raise RuntimeError("eCargo session expired — account/login")

                self._fill_create_form(page, booking, arrival)
                page.get_by_role("button", name=re.compile(r"tạo phiếu|create", re.I)).click(
                    timeout=15000
                )
                page.wait_for_timeout(2000)
                content = page.content()
                reg = self._extract_registration(content)
                return JobResult(
                    registration_no=reg,
                    status_text="submitted",
                    verify_code="",
                )
            finally:
                context.close()
                browser.close()

    def _fill_create_form(self, page, booking: Booking, arrival) -> None:
        page.get_by_label(re.compile(r"biển|plate|vehicle", re.I)).fill(booking.vehicle_no)
        page.get_by_role("button", name=re.compile(r"thêm awb|add awb", re.I)).click(
            timeout=10000
        )
        page.get_by_label(re.compile(r"chuyến|flight", re.I)).fill(booking.flight)
        page.get_by_label(re.compile(r"ngày bay|flight date", re.I)).fill(booking.flight_date)
        page.get_by_label(re.compile(r"mawb|vận đơn", re.I)).fill(booking.mawb)
        page.get_by_label(re.compile(r"kiện|pcs", re.I)).fill(str(booking.pcs))
        page.get_by_label(re.compile(r"trọng|weight|kg", re.I)).fill(
            str(int(booking.gross_weight))
        )
        page.get_by_label(re.compile(r"ngày hàng vào|arrival date", re.I)).fill(arrival.date_str)
        page.get_by_label(re.compile(r"giờ hàng vào|arrival time", re.I)).fill(arrival.time_str)

    @staticmethod
    def _extract_registration(html: str) -> str:
        m = re.search(r"(\d{8})", html)
        return m.group(1) if m else ""


def get_ecargo_backend() -> EcargoBackend:
    if settings.ecargo_dry_run:
        return DryRunEcargoBackend()
    return PlaywrightEcargoBackend()
