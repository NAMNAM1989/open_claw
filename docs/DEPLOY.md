# Checklist deploy — open_claw (Railway + Supabase)

Hướng dẫn deploy. Thứ tự: **Supabase (tùy chọn) → Gateway**.

---

## 0. Trước khi deploy (local)

```powershell
cd C:\Project\open_claw
powershell -File tools\local-test.ps1 -SkipDocker
powershell -File tools\check-isolation.ps1
node tools\set-local-gemini.mjs   # local PC
```

Gateway local: `powershell -File tools\smoke-gateway.ps1`

---

## 1. GitHub

| # | Việc |
|---|------|
| 1.1 | Repo `NAMNAM1989/open_claw` |
| 1.2 | Secrets: `RAILWAY_TOKEN`, `RAILWAY_PROJECT_ID` |

---

## 2. Supabase (tùy chọn)

Project `open_claw` — migrations trong `supabase/migrations/`.

```bash
supabase link --project-ref ikcavxwchowbgrkhfxra
supabase db push
```

RLS bật — chỉ **service role** (không dùng anon trên production).

---

## 3. Gemini API

| # | Việc |
|---|------|
| 3.1 | Key tại [Google AI Studio](https://aistudio.google.com) — dạng `AIza...` |
| 3.2 | Model production: `google/gemini-3.5-flash` (xem [MODELS.md](./MODELS.md)) |
| 3.3 | **Không** dùng OpenAI / DeepSeek trên production |

---

## 4. Railway — project `open_claw`

Chỉ **một** service: `openclaw-gateway`.

| Service | Deploy từ | Root Directory |
|---------|-----------|----------------|
| `openclaw-gateway` | `apps/gateway` | **để trống** |

**Dọn dư thừa:** xóa project Railway cũ `telegram_bot` (trống) trên Dashboard nếu còn.

```powershell
Copy-Item .env.example .env.secrets
# Dien GEMINI_API_KEY, OPENCLAW_GATEWAY_TOKEN
powershell -File tools\set-railway-secrets.ps1

cd apps\gateway
railway up --service openclaw-gateway --environment production --detach
```

Hoặc push `main` → GitHub Actions `deploy-railway.yml`.

**Không** bật GitHub auto-deploy trên Railway Dashboard.

Persona agent: sửa `apps/gateway/workspace/IDENTITY.md` / `SOUL.md` → rebuild gateway.

---

## 5. Biến môi trường gateway

| Biến | Bắt buộc |
|------|----------|
| `GEMINI_API_KEY` | ✅ |
| `GOOGLE_API_KEY` | ✅ (cùng GEMINI) |
| `OPENCLAW_GATEWAY_TOKEN` | ✅ |
| `PORT` | `18789` |

Smoke test:

```powershell
powershell -File tools\smoke-gateway.ps1
```

---

## 6. Thứ tự deploy an toàn

```
1. supabase db push (nếu có migration mới)
2. tools\set-railway-secrets.ps1
3. railway up từ apps/gateway
4. Kiểm tra logs Railway — gateway ready, không lỗi model
```

---

## 7. Giám sát

| Cần xem | Nơi |
|---------|-----|
| Gateway logs | Railway → `openclaw-gateway` |
| Gemini quota | Google AI Studio |
| DB | Supabase Dashboard |

Chi tiết vận hành: [RUNBOOK.md](./RUNBOOK.md)
