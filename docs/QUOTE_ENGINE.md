# Quote Engine — thiết kế báo giá deterministic

Phần của gói **B (chứng từ & báo giá)** trong nền tảng open_claw.

---

## 1. Nguyên tắc

| Đúng | Sai |
|------|-----|
| Giá từ `tariffs.rows_json` đã parse | LLM tự nhân `price * kg` |
| `quote_engine` Python thuần | Chỉ hỏi Gemini "giá bao nhiêu" |
| Mọi quote có `quote_code` + Supabase | Chỉ trả text chat |
| Hiển thị nguồn tariff + disclaimer | Cam kết giá pháp lý |

**AI (Gemini qua OpenClaw):** chỉ **đọc ảnh** → `PriceRow[]`. Không tính tiền.

---

## 2. Luồng

```
/gia + ảnh
  → OpenClaw vision → rows[]
  → Supabase tariffs
  → Telegram: bảng giá

"tính cước 120kg SGN-HKG" hoặc /bao_gia SGN-HKG 120
  → quote_parse.py
  → Supabase get_latest_tariff(chat_id)
  → volumetric.py (nếu có kích thước)
  → quote_engine.py
  → Supabase quotes
  → Telegram: Quote Q-xxx
```

---

## 3. `QuoteRequest` (input)

```python
@dataclass
class QuoteRequest:
    route: str              # SGN-HKG
    weight_kg: float        # 120
    cargo_type: str = "general"
    pieces: int = 0
    dims: list[Dim] = []    # optional L,W,H cm
    currency: str = "VND"
```

**Parse từ text** (`quote_parse.py`):

| Pattern | Ví dụ |
|---------|--------|
| Route IATA | `SGN-HKG`, `SGN - HKG` |
| Weight | `120kg`, `120 kg` |
| Dimensions | `60x40x40`, `1 kiện 60*40*40` |
| Cargo | `general`, `hàng thường` |

---

## 4. `volumetric.py`

```python
DIVISOR = 6000  # env VOLUMETRIC_DIVISOR

def chargeable_kg(actual_kg, dims, pieces=1) -> tuple[float, float | None]:
    vol = sum((d.L * d.W * d.H * d.pieces) / DIVISOR for d in dims)
    return max(actual_kg, vol), vol or None
```

---

## 5. `match_price_row`

Ưu tiên:

1. Normalize route (`HCM` → `SGN` alias map trong config)
2. Filter `cargo_type` (blank = general)
3. Tìm bậc weight: `min <= chargeable <= max` hoặc parse `weight_range`
4. Nhiều bậc khớp → bậc **cao nhất** mà `min <= chargeable`

---

## 6. `QuoteResult` (output)

```python
@dataclass
class QuoteResult:
    quote_code: str
    route: str
    actual_kg: float
    volumetric_kg: float | None
    chargeable_kg: float
    total: float
    currency: str
    line_items: list[QuoteLine]
    disclaimer: str
    tariff_id: uuid | None
```

---

## 7. Telegram format

```
💰 Báo giá Q-20260709-A3F2
SGN → HKG · general · tính cước 120 kg

• Cân thực: 120 kg
• Cước kg: 16.000 × 120 = 1.920.000 VND
• Tổng ước tính: 1.920.000 VND

Nguồn: bảng giá 09/07 14:32 (8 dòng)
⚠️ Chưa gồm VAT/customs. Giá chốt khi booking.
```

---

## 8. Lệnh & intent

| Entry | Handler |
|-------|---------|
| `/bao_gia SGN-HKG 120` | `bot/handlers/quote.py` |
| `tính cước 120kg SGN-HKG` | `intent.QUOTE` → orchestrator |
| Reply tariff + hỏi giá | `try_handle_quote_text` |

---

## 9. Config env

```env
QUOTE_ENGINE_ENABLED=true
VOLUMETRIC_DIVISOR=6000
QUOTE_MIN_CHARGE_DEFAULT=0
QUOTE_FUEL_SURCHARGE_PCT=0
ROUTE_ALIASES=HCM:SGN,HAN:HAN
```

---

## 10. Tests (pytest)

| Test | Case |
|------|------|
| `test_match_break_weight` | 120kg → bậc 45-100 vs 100+ |
| `test_volumetric_wins` | actual 50, vol 80 → chargeable 80 |
| `test_no_tariff` | Message hướng dẫn `/gia` trước |
| `test_quote_code_unique` | Insert 2 quotes ≠ code |

---

## 11. Phase triển khai

| Step | File |
|------|------|
| 1 | `plugins/image_reader/quote_parse.py` |
| 2 | `plugins/image_reader/volumetric.py` |
| 3 | `plugins/image_reader/quote_engine.py` |
| 4 | `core/supabase_client.py` save/get tariff & quote |
| 5 | `bot/handlers/quote.py` + `intent.py` |
| 6 | `tests/test_quote_engine.py` |

Phụ thuộc: Supabase migration + OpenClaw vision route (phase 3–4 PLATFORM).
