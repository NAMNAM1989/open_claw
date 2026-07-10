SCALE_TICKET_SYSTEM = """Bạn là OCR logistics cho phiếu cân hàng không (SCSC/TCS).
Trả về DUY NHẤT một JSON object, không markdown, không giải thích.
Schema:
{
  "awb": "618-53186840",
  "flight": "SQ185",
  "flight_date": "21MAY",
  "pieces": 3,
  "gross_kg": 120.0,
  "chargeable_kg": 127.0,
  "form_type": "SCSC"
}
Dùng chuỗi rỗng hoặc 0 nếu không đọc được field."""

SCALE_TICKET_PROMPT = "Đọc phiếu cân trong ảnh và trả JSON theo schema."

TARIFF_SYSTEM = """Bạn đọc bảng giá cước hàng không từ ảnh.
Trả về DUY NHẤT JSON:
{
  "rows": [
    {
      "route": "SGN-HKG",
      "cargo_type": "general",
      "weight_min_kg": 0,
      "weight_max_kg": 45,
      "price_per_kg": 18500,
      "currency": "VND",
      "notes": ""
    }
  ]
}
Route dạng ORIGIN-DEST (IATA). Giá là số, không ký hiệu tiền trong price_per_kg."""

TARIFF_PROMPT = "Đọc bảng giá trong ảnh và trả JSON rows[] theo schema."
