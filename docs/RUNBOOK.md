# Runbook vận hành — open_claw

Production: project Railway `open_claw` — `openclaw-gateway` + `telegram-bot`.

---

## 1. Dashboard

| Cần xem | Nơi |
|---------|-----|
| Gateway | Railway → `openclaw-gateway` → Logs |
| Bot | Railway → `telegram-bot` → Logs |
| Gemini | Google AI Studio |

---

## 2. Deploy

`git push origin main` hoặc `railway up . --path-as-root` từ `apps/gateway` / `apps/telegram-bot`.

---

## 3. Bot im lặng

| Bước | Việc |
|------|------|
| 1 | `ALLOWED_CHAT_IDS` có chứa chat_id? (`/chatid`) |
| 2 | `TELEGRAM_BOT_TOKEN` đã set trên Railway? |
| 3 | `OPENCLAW_GATEWAY_TOKEN` khớp gateway |
| 4 | Gateway logs — Gemini 3.5 OK? |

---

## 4. Rotate token

`OPENCLAW_GATEWAY_TOKEN` hoặc `TELEGRAM_BOT_TOKEN` → cập nhật `.env.secrets` → `set-railway-secrets.ps1` → redeploy service liên quan.
