# Checklist deploy — open_claw (Railway)

Thứ tự: **Gateway → telegram-bot**.

---

## 1. Local test

```powershell
cd C:\Project\open_claw
powershell -File tools\local-test.ps1 -SkipDocker
```

---

## 2. Railway — project `open_claw`

| Service | Deploy từ |
|---------|-----------|
| `openclaw-gateway` | `apps/gateway` |
| `telegram-bot` | `apps/telegram-bot` |

```powershell
Copy-Item .env.example .env.secrets
# GEMINI_API_KEY, OPENCLAW_GATEWAY_TOKEN, TELEGRAM_BOT_TOKEN

powershell -File tools\set-railway-secrets.ps1
```

Chỉ gateway: `powershell -File tools\set-railway-secrets.ps1 -SkipTelegramBot`

---

## 3. Biến môi trường

### Gateway

| Biến | Bắt buộc |
|------|----------|
| `GEMINI_API_KEY` | ✅ |
| `GOOGLE_API_KEY` | ✅ |
| `OPENAI_API_KEY` | ✅ (fallback ChatGPT) |
| `DEEPSEEK_API_KEY` | ✅ (fallback cuối) |
| `OPENCLAW_GATEWAY_TOKEN` | ✅ |
| `PORT` | `18789` |

**Volume (bắt buộc cho memory session):** mount `/root/.openclaw` trên service `openclaw-gateway`.
Lưu ý: volume ghi đè thư mục config/plugin — DeepSeek provider được bake vào `/app/vendor-plugins` và load qua `plugins.load.paths` (không phụ thuộc volume).

### `telegram-bot`

| Biến | Bắt buộc |
|------|----------|
| `TELEGRAM_BOT_TOKEN` | ✅ Token BotFather |
| `OPENCLAW_GATEWAY_TOKEN` | ✅ Cùng gateway |
| `OPENCLAW_BASE_URL` | `http://openclaw-gateway.railway.internal:18789/v1` |
| `ALLOWED_CHAT_IDS` | ✅ Sau `/chatid` |

---

## 4. Deploy

```powershell
cd apps\gateway
railway up . --path-as-root --service openclaw-gateway --environment production --detach

cd ..\telegram-bot
railway up . --path-as-root --service telegram-bot --environment production --detach
```

Hoặc `git push origin main` → Actions `deploy-railway.yml`.

---

## 5. Smoke test Telegram

1. Nhắn bot `/chatid` → copy ID vào `ALLOWED_CHAT_IDS` → redeploy bot
2. `/ping` → `pong`
3. `/ask Xin chào` → trả lời từ Gemini qua gateway
4. Gửi 2–3 tin liên tiếp (hỏi lại thông tin vừa nói) → bot nhớ context; `/clear` xóa memory
5. Gửi ảnh + caption → bot đọc/trích thông tin ảnh
6. Gửi file `.xlsx` (+ caption tùy chọn) → bot đọc bảng và trả lời
7. `/baogia SGN-HKG 120kg 16000` → nhận PDF báo giá
8. `/pkl` + MAWB/shipper + dòng `1. … | kiện | kg | kích thước` → nhận PDF PKL

---

## 6. Giám sát

| Nơi | Xem |
|-----|-----|
| `openclaw-gateway` logs | Gemini, model errors |
| `telegram-bot` logs | Polling, OpenClaw HTTP |
| [RUNBOOK.md](./RUNBOOK.md) | Vận hành |
