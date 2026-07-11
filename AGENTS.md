# open_claw monorepo — hướng dẫn agent

## Tổng quan

Nền tảng **NamNam Ops**: Railway project `open_claw`, Gemini → ChatGPT → DeepSeek, GitHub CI.

- **Production:** `openclaw-gateway` + `telegram-bot`
- **Docs:** `docs/PLATFORM.md` · `docs/MODELS.md`

## Layout

```
apps/
  gateway/           OpenClaw + Gemini/GPT/DeepSeek (Railway)
  telegram-bot/      Bot Telegram → gateway
plugins/
  cursor-agent/      Dev local only
supabase/migrations/ # Tùy chọn
docs/
```

## Railway (project `open_claw`)

| Service | Deploy từ |
|---------|-----------|
| `openclaw-gateway` | `apps/gateway` |
| `telegram-bot` | `apps/telegram-bot` |
