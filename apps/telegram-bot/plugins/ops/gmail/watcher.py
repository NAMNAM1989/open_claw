from __future__ import annotations

import email
import imaplib
import logging
import re
from email.header import decode_header

from core.settings import settings
from plugins.ops.models import QrMail, VerifyMail

log = logging.getLogger("namnam.gmail")

VERIFY_LINK_RE = re.compile(r"https?://[^\s\"']+verify[^\s\"']*", re.I)
REG_RE = re.compile(r"\b(\d{8})\b")
VCT_RE = re.compile(r"\bVCT[\s\-]?(\d+)\b", re.I)


def _decode_header_value(value: str) -> str:
    parts = decode_header(value)
    out = []
    for chunk, enc in parts:
        if isinstance(chunk, bytes):
            out.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            out.append(chunk)
    return "".join(out)


class GmailWatcher:
    def __init__(self) -> None:
        self._user = settings.gmail_user
        self._password = settings.gmail_app_password

    @property
    def configured(self) -> bool:
        return bool(self._user and self._password)

    def _connect(self) -> imaplib.IMAP4_SSL:
        client = imaplib.IMAP4_SSL("imap.gmail.com")
        client.login(self._user, self._password)
        client.select("INBOX")
        return client

    def find_verify_mail(self, *, registration_no: str = "", limit: int = 10) -> VerifyMail | None:
        if not self.configured:
            return None
        client = self._connect()
        try:
            _, data = client.search(None, '(UNSEEN SUBJECT "Phiếu Đăng Ký")')
            ids = (data[0] or b"").split()[-limit:]
            for msg_id in reversed(ids):
                _, msg_data = client.fetch(msg_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                subject = _decode_header_value(msg.get("Subject", ""))
                body = self._extract_text(msg)
                url_m = VERIFY_LINK_RE.search(body)
                reg_m = REG_RE.search(subject + " " + body)
                reg = registration_no or (reg_m.group(1) if reg_m else "")
                if reg and registration_no and reg != registration_no:
                    continue
                if url_m:
                    return VerifyMail(subject=subject, verify_url=url_m.group(0), registration_no=reg)
            return None
        finally:
            client.logout()

    def find_qr_mail(self, *, registration_no: str = "", limit: int = 10) -> QrMail | None:
        if not self.configured:
            return None
        client = self._connect()
        try:
            _, data = client.search(None, '(UNSEEN SUBJECT "VCT")')
            ids = (data[0] or b"").split()[-limit:]
            for msg_id in reversed(ids):
                _, msg_data = client.fetch(msg_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                subject = _decode_header_value(msg.get("Subject", ""))
                body = self._extract_text(msg)
                reg_m = REG_RE.search(subject + " " + body)
                vct_m = VCT_RE.search(subject + " " + body)
                reg = registration_no or (reg_m.group(1) if reg_m else "")
                if registration_no and reg and reg != registration_no:
                    continue
                image = self._first_image_attachment(msg)
                if image or vct_m:
                    return QrMail(
                        subject=subject,
                        registration_no=reg,
                        vct_number=vct_m.group(1) if vct_m else "",
                        image_bytes=image,
                    )
            return None
        finally:
            client.logout()

    @staticmethod
    def _extract_text(msg: email.message.Message) -> str:
        if msg.is_multipart():
            chunks = []
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True) or b""
                    chunks.append(payload.decode(errors="replace"))
            return "\n".join(chunks)
        payload = msg.get_payload(decode=True) or b""
        return payload.decode(errors="replace")

    @staticmethod
    def _first_image_attachment(msg: email.message.Message) -> bytes | None:
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype.startswith("image/"):
                return part.get_payload(decode=True)
        return None
