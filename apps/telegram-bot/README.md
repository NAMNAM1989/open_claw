# NamNam Ops — Telegram bot

Service `telegram-bot` trong project Railway **`open_claw`**. Gọi OpenClaw Gateway qua HTTP.

## Lệnh

| Lệnh | Mô tả |
|------|--------|
| `/start` | Giới thiệu |
| `/ping` | `pong` |
| `/chatid` | Lấy ID nhóm/chat (để `ALLOWED_CHAT_IDS`) |
| `/ask <text>` | Hỏi qua Gemini (OpenClaw) |
| `/clear` | Xóa bộ nhớ hội thoại chat hiện tại |
| `/baogia` | Tạo PDF báo giá từ text |
| `/pkl` | Tạo PDF packing list từ text |
| Gửi text | Cùng luồng `/ask` (session OpenClaw) |
| Gửi ảnh | Đọc ảnh qua Gemini vision (caption tùy chọn) |
| Gửi Excel `.xlsx` | Đọc bảng (rút gọn) → tóm tắt qua AI; caption = câu hỏi |

### Ví dụ `/baogia`

```
/baogia SGN-HKG 120kg 16000
```

hoặc nhiều dòng: Khách / Route / KL / Đơn giá / Kiện / Kích thước.

### Ví dụ `/pkl`

```
/pkl
MAWB: 123-45678900
Shipper: A Co
Consignee: B Co
Origin: SGN
Dest: HKG
1. Widget A | 10 | 100kg | 50x40x40
```

## Local

```powershell
Copy-Item ..\..\.env.example .env
# TELEGRAM_BOT_TOKEN, OPENCLAW_*, ALLOWED_CHAT_IDS

pip install -r requirements.txt
python scripts\check_config.py
python -m bot.main
```

Gateway local: `OPENCLAW_BASE_URL=http://127.0.0.1:18789/v1`

## Railway

```env
TELEGRAM_BOT_TOKEN=
ALLOWED_CHAT_IDS=
OPENCLAW_BASE_URL=http://openclaw-gateway.railway.internal:18789/v1
OPENCLAW_GATEWAY_TOKEN=
VOLUMETRIC_DIVISOR=6000
```

Deploy:

```powershell
cd apps/telegram-bot
railway up . --path-as-root --service telegram-bot --environment production --detach
```
