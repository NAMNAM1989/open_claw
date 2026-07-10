"""Tạo file mẫu tariff_template.xlsx — chạy một lần khi cần."""

from pathlib import Path

from openpyxl import Workbook

HEADERS = [
    "Route",
    "Carrier",
    "Cargo",
    "Min_kg",
    "Max_kg",
    "Buy_rate",
    "Sell_rate",
    "Currency",
    "FSC_%",
    "AWB_fee",
    "Effective_from",
]

SAMPLE_ROWS = [
    ["SGN-HKG", "CX", "general", 0, 45, 15000, 18500, "VND", 15, 500000, "2026-07-01"],
    ["SGN-HKG", "CX", "general", 45, 100, 13500, 16000, "VND", 15, 500000, "2026-07-01"],
    ["SGN-HKG", "CX", "general", 100, 0, 12000, 14000, "VND", 15, 500000, "2026-07-01"],
    ["SGN-NRT", "NH", "general", 0, 45, 18000, 21000, "VND", 18, 550000, "2026-07-01"],
    ["SGN-NRT", "NH", "general", 45, 0, 16000, 18500, "VND", 18, 550000, "2026-07-01"],
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "templates" / "tariff_template.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Tariff"
    ws.append(HEADERS)
    for row in SAMPLE_ROWS:
        ws.append(row)
    wb.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
