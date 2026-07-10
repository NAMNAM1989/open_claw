# NamNam Ops — telegram-bot (greenfield)

Bot logistics viết mới trong monorepo `open_claw`. **Không migrate** từ project bot cũ.

## Dev loop

```powershell
cd apps\telegram-bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest tests/ -q
python -m bot.main
```

## Cấu trúc

```
bot/           Telegram entry + handlers
core/          settings, supabase, openclaw client
plugins/
  ops/         booking, eCargo (phase 2)
  sales/       quote, tariff, excel (phase 1)
  documents/   phiếu cân, vision (phase 2)
workspace/     persona sync → apps/gateway/workspace
```

## Chat & báo cáo (phase 4)

| Lệnh | Mô tả |
|------|--------|
| `/ask <câu hỏi>` | Chat AI + context Supabase qua OpenClaw |
| Reply tin bot | Hỏi tiếp không cần /ask |
| `/ops [tuan\|thang]` | Báo cáo booking/job/phiếu cân |
| `/sales [tuan\|thang]` | Báo cáo quote |

## Documents (phase 3)

| Lệnh | Mô tả |
|------|--------|
| `/can` + ảnh | Đọc phiếu cân (OpenClaw vision + regex fallback) |
| `/gia` + ảnh | Đọc bảng giá → lưu tariff |

Cần `OPENCLAW_BASE_URL` + `OPENCLAW_GATEWAY_TOKEN` cho vision.

## Ops eCargo (phase 2)

| Lệnh / hành động | Mô tả |
|------------------|--------|
| Gửi text booking | 5 dòng hoặc nhãn `Xe:` / `MAWB:` … |
| `có` / `/go` | Chạy đăng ký eCargo |
| `/booking` | Xem pending |
| `/status` | Job gần nhất |
| `/chatid` | Lấy chat_id nhóm |

Env ops: `ECARGO_DRY_RUN=true` (mặc định), `ECARGO_STORAGE_STATE`, `GMAIL_*`, `MAIL_WATCH_ENABLED`.

Session: `python scripts/save_ecargo_session.py`

## Lệnh sales (phase 1)

| Lệnh | Mô tả |
|------|--------|
| `/import_gia` | Import Excel tariff (gửi file + caption, hoặc reply file) |
| `/tariff` | Xem bảng giá đang active |
| `/bao_gia SGN-HKG 120` | Báo giá + lưu Supabase |

Mẫu Excel: `templates/tariff_template.xlsx`

Supabase: set `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` — nếu thiếu, chạy in-memory (dev).
