# open_claw — Nền tảng vận hành (Railway + Supabase + GitHub + Gemini)

> **Production:** project `open_claw` — `openclaw-gateway` + `telegram-bot`.

Tài liệu thiết kế cho project thống nhất tên **open_claw** trên GitHub, Railway và Supabase.
Mục tiêu: **OpenClaw Gateway 24/7** + bot Telegram v2 (chat qua gateway), memory persist.

---

## 1. Tổng quan kiến trúc

```
                    ┌─────────────────────────────────────────┐
                    │           GitHub: open_claw               │
                    └─────────────────┬───────────────────────┘
                                      │ push main
                    ┌─────────────────▼───────────────────────┐
                    │         Railway project: open_claw       │
                    │  ┌─────────────────┐ ┌───────────────┐ │
                    │  │ telegram-bot v2 │ │ openclaw-     │ │
                    │  │ /ask · Telegram │ │ gateway       │ │
                    │  └────────┬────────┘ └───────┬───────┘ │
                    │           │  railway.internal │         │
                    │           └────────┬────────┘         │
                    └────────────────────┼──────────────────┘
                                         │
                    ┌────────────────────▼──────────────────┐
                    │      Supabase (tuỳ chọn, schema sẵn)   │
                    └─────────────────────────────────────────┘
```

Telegram ──► telegram-bot v2 ──HTTP──► openclaw-gateway ──► Gemini API

### Phân vai từng tài khoản

| Tài khoản | Vai trò trong open_claw | Không dùng cho |
|-----------|-------------------------|----------------|
| **GitHub** `open_claw` | Source of truth, CI, deploy config | Chạy production |
| **Railway** `open_claw` | `openclaw-gateway` + `telegram-bot` v2 | Database chính |
| **Supabase** `open_claw` | Postgres + Storage (schema sẵn, tuỳ chọn) | Runtime bot/gateway |
| **Gemini** | Model chính OpenClaw: chat | — |

---

## 2. Cấu trúc monorepo GitHub

Project **open_claw** trên GitHub, Railway và Supabase.

```
open_claw/
├── apps/
│   ├── gateway/
│   └── telegram-bot/          # Bot Telegram
├── plugins/cursor-agent/
├── supabase/migrations/
└── docs/
```

| Service | Deploy từ |
|---------|-----------|
| `openclaw-gateway` | `apps/gateway` |
| `telegram-bot` | `apps/telegram-bot` |

---

## 3. Railway services

### 3.1 `openclaw-gateway`
- OpenClaw Gateway HTTP API (`chatCompletions`)
- Agent workspace: `apps/gateway/workspace` (IDENTITY, SOUL)
- Model **Gemini 3.5 Flash** (`google/gemini-3.5-flash`)
- Plugins: `active-memory`, `memory-wiki`, `document-extract` (không `cursor-agent` production)
- **Tắt** `channels.telegram` — tránh trùng bot token

**Biến môi trường:**

```env
GEMINI_API_KEY=
GOOGLE_API_KEY=              # alias, cùng giá trị GEMINI_API_KEY
OPENCLAW_GATEWAY_TOKEN=
PORT=18789
```

### 3.2 `telegram-bot`

- HTTP → gateway (`/ask`, text)
- `ALLOWED_CHAT_IDS` bắt buộc sau `/chatid`

```env
TELEGRAM_BOT_TOKEN=
ALLOWED_CHAT_IDS=
OPENCLAW_BASE_URL=http://openclaw-gateway.railway.internal:18789/v1
OPENCLAW_GATEWAY_TOKEN=
```

### 3.3 Kết nối nội bộ

Railway private networking: các service cùng project `open_claw` gọi nhau qua hostname `.railway.internal` (khi bot được bật lại).

```
telegram-bot  →  http://openclaw-gateway.railway.internal:18789/v1/chat/completions
```

Không cần Tailscale, không public port 18789.

---

## 4. Gemini — LLM duy nhất (thiết kế chốt)

Chi tiết đầy đủ: **[MODELS.md](./MODELS.md)**.

API key từ [Google AI Studio](https://aistudio.google.com) (prefix `AIza`).

**Không** dùng DeepSeek / OpenAI (ChatGPT) cho production NamNam Ops.

**Model routing:**

| Tác vụ | Model | Ghi chú |
|--------|-------|---------|
| Chat `/ask` | `google/gemini-3.5-flash` | Primary |

**Nguồn config:** `apps/gateway/openclaw.template.json` — plugin `google` bật; `openai` / `deepseek` tắt.

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.5-flash" },
      workspace: "/app/workspace",
    },
  },
  channels: { telegram: { enabled: false } },
  plugins: {
    entries: {
      google: { enabled: true },
      openai: { enabled: false },
      deepseek: { enabled: false },
      "cursor-agent": { enabled: false },
      "active-memory": { enabled: true },
      "memory-wiki": { enabled: true },
      "document-extract": { enabled: true },
    },
  },
}
```

Tài liệu provider: https://docs.openclaw.ai/providers/google

---

## 5. Supabase — schema logistics

Project Supabase tên `open_claw`. Chỉ **service role** trên Railway — không expose anon key ra client public.

### 5.1 Bảng core

| Bảng | Mục đích |
|------|----------|
| `bookings` | Booking raw + parsed, trạng thái pending/done/error |
| `job_runs` | Mỗi lần chạy eCargo: reg, vct, lỗi, thời gian |
| `scale_tickets` | Kết quả OCR phiếu cân theo chat/MAWB |
| `tariffs` | Bảng giá sau `/gia` (rows JSON) |
| `quotes` | Báo giá `/bao_gia` có mã quote |
| `customers` | `reg_no` → `customer_name` (thay `reg_customer.json`) |
| `ops_log` | Log lỗi, health, audit |
| `chat_sessions` | Map `chat_id` ↔ OpenClaw `user=tg:{id}` |

### 5.2 Migration khởi tạo

File: `supabase/migrations/20260709100000_initial.sql` (tạo ở phase 2).

### 5.3 Storage bucket (tuỳ chọn)

| Bucket | Nội dung |
|--------|----------|
| `qr-images` | Ảnh QR archive (thay gửi lại từ mail) |
| `documents` | Ảnh chứng từ đã đọc (invoice, tariff) |

---

## 6. Luồng nghiệp vụ sau thiết kế

```
User gửi booking
  → telegram-bot parse + validate
  → Supabase bookings (pending)
  → User "có" / ✅ OK
  → Playwright eCargo + Gmail
  → Supabase job_runs + customers
  → Telegram QR / trạng thái

User /ask
  → telegram-bot → openclaw-gateway → Gemini Flash
  → (memory OpenClaw + ops_log Supabase)

User /gia + ảnh
  → vision Gemini qua gateway
  → Supabase tariffs
  → User "tính cước 120kg SGN-HKG"
  → quote_engine → Supabase quotes
```

---

## 7. GitHub Actions

| Workflow | Trigger | Việc |
|----------|---------|------|
| `ci-plugins.yml` | PR / push `plugins/**` | `npm test`, `npm run build` |
| `deploy-railway.yml` | push `main` | Deploy `openclaw-gateway` |

**GitHub Secrets cần thêm:**

- `RAILWAY_TOKEN`
- `RAILWAY_PROJECT_ID` (project open_claw)
- (Tuỳ chọn) `SUPABASE_ACCESS_TOKEN` cho migration CI

---

## 8. Dev local vs production

| Thành phần | Local (PC) | Production (Railway) |
|------------|------------|---------------------|
| OpenClaw Gateway | `openclaw gateway` loopback | `openclaw-gateway` service |
| Plugin cursor-agent | Bật — `/cursor` dev | Tắt |
| Telegram | Token test hoặc không chạy | Token production |
| Supabase | Dev project hoặc branch | Project `open_claw` |
| Gemini | Cùng API key (giới hạn quota) | Cùng key (monitor usage) |

---

## 9. Bảo mật — checklist

- [ ] Rotate `OPENCLAW_GATEWAY_TOKEN` định kỳ
- [ ] Rotate `TELEGRAM_BOT_TOKEN` khi cần
- [ ] Tắt `channels.telegram` trên Gateway production (dùng `apps/telegram-bot`)
- [ ] Không commit `.env`, Supabase service key
- [ ] Supabase: RLS bật; policy chỉ service role
- [ ] Railway: không public domain cho gateway
- [ ] GitHub: branch protection `main`, secret scanning

---

## 10. Lộ trình triển khai

### Phase 0 — Chuẩn bị (1–2 ngày)

- [ ] Push repo `open_claw` lên GitHub remote
- [ ] Link Railway project `open_claw` ↔ GitHub repo
- [ ] Link Supabase CLI: `supabase link --project-ref <ref>`
- [ ] Tạo Gemini API key, lưu Railway Variables

### Phase 1 — Gateway Railway (tuần 1)

- [ ] Tạo `apps/gateway/Dockerfile` + `openclaw.json`
- [ ] Deploy service `openclaw-gateway`
- [ ] Verify: `GET /v1/models` với Bearer token

### Phase 2 — Bot + Gateway

- [x] `apps/telegram-bot`
- [ ] Smoke test `/ask` trên Railway

### Phase 3 — Supabase (tuần 2–3)

- [ ] Migration initial schema
- [x] `core/supabase_client.py` trong telegram-bot
- [ ] Persist bookings, tariffs, quotes trên Supabase live

### Phase 4 — Gemini vision + quote (tuần 3–4)

- [ ] Route `chat_vision` qua OpenClaw
- [ ] `quote_engine` + `/bao_gia`

### Phase 5 — CI/CD (tuần 4)

- [ ] GitHub Actions deploy Railway on merge main

---

## 11. Trạng thái hiện tại (baseline)

| Hạng mục | Trạng thái |
|----------|------------|
| GitHub `open_claw` | Monorepo có `apps/` + `plugins/` — cần push remote |
| Railway `open_claw` | User đã tạo project — **gateway** đang chạy; bot optional |
| Supabase `open_claw` | User đã tạo project — chưa migration live |
| Gemini | **LLM duy nhất** — gắn `GEMINI_API_KEY` Gateway production |
| `apps/telegram-bot` | Service Telegram trong project `open_claw` |
| OpenClaw local PC | **Cần tắt** `channels.telegram` nếu còn bật (trùng polling) |

---

## 12. Bước tiếp theo đề xuất

1. **Deploy:** gateway + bot — xem [DEPLOY.md](./DEPLOY.md).
2. **Secrets:** điền `.env.secrets` → `tools\set-railway-secrets.ps1`.

Xem thêm:

| Tài liệu | Nội dung |
|----------|----------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Sequence, module map, API contract |
| [MODELS.md](./MODELS.md) | **Gemini only** — routing & env |
| [DATA.md](./DATA.md) | ERD, JSON types, queries |
| [QUOTE_ENGINE.md](./QUOTE_ENGINE.md) | Báo giá deterministic (gói B) |
| [RUNBOOK.md](./RUNBOOK.md) | Vận hành hàng ngày |
| [TEST_REPORT.md](./TEST_REPORT.md) | Kết quả kiểm tra local |
| [../apps/telegram-bot/README.md](../apps/telegram-bot/README.md) | Service `telegram-bot` |
