# Runbook vận hành — open_claw

> **Production Railway:** chỉ `openclaw-gateway`. Các mục bot áp dụng khi chạy local hoặc deploy lại service `telegram-bot`.

Hướng dẫn hàng ngày sau khi deploy Railway + Supabase.

---

## 1. Dashboard nhanh

| Cần xem | Nơi |
|---------|-----|
| Log Gateway (production) | Railway → `openclaw-gateway` → Deployments → Logs |
| Log bot (local / optional) | Terminal `python -m bot.main` hoặc Railway `telegram-bot` nếu bật lại |
| DB / SQL | Supabase Dashboard → SQL Editor |
| Gemini quota | [Google AI Studio](https://aistudio.google.com) |
| Code | GitHub → `open_claw` |

---

## 2. Deploy code mới

```powershell
# Local — sau khi push main, GitHub Actions deploy (phase 5)
# Hoặc thủ công:
cd C:\Project\open_claw
git push origin main

# Railway CLI (gateway)
npx @railway/cli redeploy --service openclaw-gateway --environment production
```

**Thứ tự an toàn:** gateway trước. Bot (nếu có service Railway) sau.

---

## 3. Session eCargo hết hạn

**Triệu chứng:** Bot báo `session_expired`, Playwright redirect login.

```powershell
# Trên PC có Chrome đăng nhập eCargo
cd apps\telegram-bot
python scripts\save_ecargo_session.py
```

Upload `data/ecargo_storage.json` lên Railway Volume `telegram-bot`.

---

## 4. OpenClaw Gateway không phản hồi

**Triệu chứng:** Log bot `openclaw=False`, `/ask` lỗi timeout.

| Bước | Việc |
|------|------|
| 1 | Railway → `openclaw-gateway` → Logs — crash? |
| 2 | Kiểm tra `GEMINI_API_KEY` / `GOOGLE_API_KEY` còn hiệu lực (Google AI Studio) |
| 3 | Kiểm tra `OPENCLAW_GATEWAY_TOKEN` đã set trên gateway (và bot nếu có) |
| 4 | Redeploy gateway — **không** đổi sang DeepSeek/OpenAI |
| 5 | Xem [MODELS.md](./MODELS.md) — stack LLM chỉ Gemini |

---

## 5. Supabase

### Chạy migration mới

```bash
supabase link --project-ref <ref>
supabase db push
```

Hoặc copy SQL vào SQL Editor.

### Backup

Supabase Dashboard → Database → Backups (plan dependent).

---

## 6. Rotate secrets

| Secret | Khi nào |
|--------|---------|
| `OPENCLAW_GATEWAY_TOKEN` | Nghi lộ / định kỳ 90 ngày |
| `TELEGRAM_BOT_TOKEN` | Lộ token / BotFather revoke |
| `GMAIL_APP_PASSWORD` | Đổi mật khẩu Google |
| `SUPABASE_SERVICE_ROLE_KEY` | Rotate trên Supabase → cập nhật Railway |
| `GEMINI_API_KEY` | Restrict key trên Google Cloud |

Sau rotate: redeploy **cả hai** service Railway.

---

## 7. Nhóm Telegram mới

1. Gửi `/chatid` trong nhóm
2. Thêm ID vào `ALLOWED_CHAT_IDS` trên Railway
3. Redeploy bot (hoặc restart nếu đọc file `data/allowed_chat_ids.txt`)

---

## 8. Health check thủ công

```bash
# Từ máy trong Railway (hoặc local với port forward)
curl -sS http://openclaw-gateway.railway.internal:18789/v1/models \
  -H "Authorization: Bearer $OPENCLAW_GATEWAY_TOKEN"
```

Bot startup tự chạy tương đương qua `session_health`.

---

## 9. Sự cố thường gặp

| Triệu chứng | Nguyên nhân | Xử lý |
|-------------|-------------|-------|
| Bot im lặng | 2 instance cùng token | Chỉ 1 replica Railway |
| Double reply | OpenClaw Telegram channel bật | Tắt channel trên Gateway |
| QR không về | `mail_qr_manual_only=true` | Bấm 📲 Quét QR |
| Đọc ảnh lỗi | Thiếu Tesseract / vision | Check Dockerfile + `GEMINI` |
| Quote sai số | Tariff OCR lỗi | Gửi lại `/gia` ảnh rõ hơn |

---

## 10. Liên hệ tài liệu

- Kiến trúc: [ARCHITECTURE.md](./ARCHITECTURE.md)
- Schema: [DATA.md](./DATA.md)
- Báo giá: [QUOTE_ENGINE.md](./QUOTE_ENGINE.md)
