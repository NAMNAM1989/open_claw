from __future__ import annotations

import re
from dataclasses import dataclass, field


_KV = re.compile(r"^\s*([^:：\n]+)\s*[:：]\s*(.+?)\s*$")
_ROUTE = re.compile(r"\b([A-Za-z]{3})\s*[-–→]\s*([A-Za-z]{3})\b", re.I)
_KG = re.compile(r"(\d+(?:[.,]\d+)?)\s*kg\b", re.I)
_NUM = re.compile(r"^(\d+(?:[.,]\d+)?)$")
_DIM = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*[xX×*]\s*(\d+(?:[.,]\d+)?)\s*[xX×*]\s*(\d+(?:[.,]\d+)?)"
)
_PKL_LINE = re.compile(
    r"^\s*(\d+)[.)]\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\d+(?:[.,]\d+)?)\s*kg?\s*"
    r"(?:\|\s*(.+?))?\s*$",
    re.I,
)
_SHORT_QUOTE = re.compile(
    r"^\s*([A-Za-z]{3})\s*[-–]\s*([A-Za-z]{3})\s+(\d+(?:[.,]\d+)?)\s*kg?\s+(\d+(?:[.,]\d+)?)\s*$",
    re.I,
)


def _f(s: str) -> float:
    return float(s.replace(",", ".").strip())


def _norm_key(k: str) -> str:
    k = k.strip().lower()
    aliases = {
        "khách": "customer",
        "khach": "customer",
        "customer": "customer",
        "route": "route",
        "tuyến": "route",
        "tuyen": "route",
        "kl": "weight_kg",
        "kg": "weight_kg",
        "cân": "weight_kg",
        "can": "weight_kg",
        "weight": "weight_kg",
        "đơn giá": "unit_price",
        "don gia": "unit_price",
        "unit price": "unit_price",
        "giá": "unit_price",
        "gia": "unit_price",
        "kiện": "pieces",
        "kien": "pieces",
        "pcs": "pieces",
        "pieces": "pieces",
        "kích thước": "dims",
        "kich thuoc": "dims",
        "dim": "dims",
        "dims": "dims",
        "ghi chú": "note",
        "ghi chu": "note",
        "note": "note",
        "mawb": "mawb",
        "awb": "mawb",
        "shipper": "shipper",
        "người gửi": "shipper",
        "nguoi gui": "shipper",
        "consignee": "consignee",
        "người nhận": "consignee",
        "nguoi nhan": "consignee",
        "origin": "origin",
        "đi": "origin",
        "di": "origin",
        "dest": "dest",
        "destination": "dest",
        "đến": "dest",
        "den": "dest",
    }
    return aliases.get(k, k)


@dataclass
class Dim:
    L: float
    W: float
    H: float
    pieces: int = 1


@dataclass
class QuoteInput:
    customer: str = ""
    route: str = ""
    weight_kg: float = 0.0
    unit_price: float = 0.0
    pieces: int = 0
    dims: list[Dim] = field(default_factory=list)
    note: str = ""
    currency: str = "VND"


@dataclass
class PklLine:
    no: int
    description: str
    pieces: int
    weight_kg: float
    dims: str = ""


@dataclass
class PklInput:
    mawb: str = ""
    shipper: str = ""
    consignee: str = ""
    origin: str = ""
    dest: str = ""
    lines: list[PklLine] = field(default_factory=list)
    note: str = ""


def parse_kv_block(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = _KV.match(line)
        if not m:
            continue
        out[_norm_key(m.group(1))] = m.group(2).strip()
    return out


def parse_dims(s: str, pieces: int = 1) -> list[Dim]:
    dims: list[Dim] = []
    for m in _DIM.finditer(s or ""):
        dims.append(Dim(_f(m.group(1)), _f(m.group(2)), _f(m.group(3)), pieces or 1))
    return dims


def parse_quote(text: str) -> QuoteInput:
    text = (text or "").strip()
    if not text:
        raise ValueError(
            "Thiếu dữ liệu.\n"
            "VD:\n/baogia SGN-HKG 120kg 16000\n"
            "hoặc nhiều dòng: Khách / Route / KL / Đơn giá / …"
        )

    short = _SHORT_QUOTE.match(text)
    if short:
        return QuoteInput(
            route=f"{short.group(1).upper()}-{short.group(2).upper()}",
            weight_kg=_f(short.group(3)),
            unit_price=_f(short.group(4)),
        )

    kv = parse_kv_block(text)
    q = QuoteInput(
        customer=kv.get("customer", ""),
        route=kv.get("route", ""),
        note=kv.get("note", ""),
    )

    if not q.route:
        rm = _ROUTE.search(text)
        if rm:
            q.route = f"{rm.group(1).upper()}-{rm.group(2).upper()}"

    w = kv.get("weight_kg")
    if w:
        wm = _KG.search(w) or _NUM.match(w)
        if wm:
            q.weight_kg = _f(wm.group(1))
    if not q.weight_kg:
        wm = _KG.search(text)
        if wm:
            q.weight_kg = _f(wm.group(1))

    p = kv.get("unit_price")
    if p:
        digits = re.sub(r"[^\d.,]", "", p)
        if digits:
            q.unit_price = _f(digits)

    pcs = kv.get("pieces")
    if pcs and re.search(r"\d+", pcs):
        q.pieces = int(re.search(r"\d+", pcs).group(0))

    dim_src = kv.get("dims", "")
    q.dims = parse_dims(dim_src, q.pieces or 1)

    if not q.route:
        raise ValueError("Thiếu Route (VD: SGN-HKG).")
    if q.weight_kg <= 0:
        raise ValueError("Thiếu KL/kg hợp lệ.")
    if q.unit_price <= 0:
        raise ValueError("Thiếu Đơn giá hợp lệ.")
    return q


def parse_pkl(text: str) -> PklInput:
    text = (text or "").strip()
    if not text:
        raise ValueError(
            "Thiếu dữ liệu PKL.\n"
            "VD:\nMAWB: …\nShipper: …\n1. Hàng A | 10 | 100kg | 50x40x40"
        )

    kv = parse_kv_block(text)
    p = PklInput(
        mawb=kv.get("mawb", ""),
        shipper=kv.get("shipper", ""),
        consignee=kv.get("consignee", ""),
        origin=kv.get("origin", "").upper(),
        dest=kv.get("dest", "").upper(),
        note=kv.get("note", ""),
    )

    if not p.origin or not p.dest:
        rm = _ROUTE.search(text)
        if rm:
            p.origin = p.origin or rm.group(1).upper()
            p.dest = p.dest or rm.group(2).upper()

    for line in text.splitlines():
        m = _PKL_LINE.match(line)
        if not m:
            continue
        p.lines.append(
            PklLine(
                no=int(m.group(1)),
                description=m.group(2).strip(),
                pieces=int(m.group(3)),
                weight_kg=_f(m.group(4)),
                dims=(m.group(5) or "").strip(),
            )
        )

    if not p.lines:
        raise ValueError(
            "Thiếu dòng hàng. VD: `1. Widget A | 10 | 100kg | 50x40x40`"
        )
    return p


def chargeable_kg(
    actual_kg: float,
    dims: list[Dim],
    divisor: float = 6000.0,
) -> tuple[float, float | None]:
    if not dims:
        return actual_kg, None
    vol = sum((d.L * d.W * d.H * d.pieces) / divisor for d in dims)
    return max(actual_kg, vol), vol
