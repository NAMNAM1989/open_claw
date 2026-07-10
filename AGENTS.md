# open_claw monorepo — hướng dẫn agent

## Tổng quan

Nền tảng **NamNam Ops**: Railway (gateway), Supabase, Gemini, GitHub CI.

- **Production 24/7:** Railway project `open_claw` — service `openclaw-gateway`
- **Docs:** `docs/PLATFORM.md` · `docs/MODELS.md` (Gemini only)

## Layout

```
apps/
  gateway/           OpenClaw + Gemini (Railway)
plugins/
  cursor-agent/      Dev local only
supabase/migrations/
docs/
```

## Dev — plugin

```powershell
cd plugins\cursor-agent
npm run build
npm test
openclaw gateway restart   # local PC
```

## Dev — gateway Docker

```powershell
cd apps\gateway
docker build -t openclaw-gateway .
docker run -e GEMINI_API_KEY=... -e OPENCLAW_GATEWAY_TOKEN=... -p 18789:18789 openclaw-gateway
```

## Secrets

Không commit `.env`. Xem `.env.example` ở repo root.

## Railway services

| Service | Root |
|---------|------|
| `openclaw-gateway` | `apps/gateway` |
