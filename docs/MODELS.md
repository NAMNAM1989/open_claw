# Model AI — open_claw (Gemini only)

**Quyết định thiết kế:** toàn bộ LLM của nền tảng NamNam Ops dùng **Google Gemini** qua OpenClaw Gateway.

Không dùng DeepSeek / ChatGPT (OpenAI) cho production hay bot logistics.

---

## 1. Vai trò từng tầng

```
Telegram user
    → apps/telegram-bot          (không gọi LLM trực tiếp)
        → openclaw-gateway       (OpenClaw HTTP /v1)
            → Google Gemini API  (GEMINI_API_KEY)
```

| Thành phần | Gọi LLM? | Provider |
|------------|----------|----------|
| `telegram-bot` | Không | Chỉ HTTP tới Gateway (`AI_PROVIDER=openclaw`) |
| `openclaw-gateway` | Có | **Gemini only** |
| `quote_engine` | Không | Python deterministic — không tin LLM nhân giá |
| `cursor-agent` (local) | N/A | Dev tool; không phải production AI |

---

## 2. Model routing

| Tác vụ | Model | Env / ghi chú |
|--------|-------|---------------|
| Chat `/ask`, intent | `google/gemini-2.5-flash` | Primary mặc định |
| Vision `/can`, `/gia` | `google/gemini-2.5-flash` | Multimodal native |
| Task nặng (tuỳ chọn) | `google/gemini-2.5-pro` | Đổi tay trên agent nếu cần — không commit fallback schema nếu OpenClaw reject |

Config nguồn sự thật: `apps/gateway/openclaw.template.json`

---

## 3. Biến môi trường (Railway `openclaw-gateway`)

```env
GEMINI_API_KEY=AIza...          # bắt buộc — Google AI Studio
GOOGLE_API_KEY=AIza...          # cùng giá trị (alias OpenClaw)
OPENCLAW_GATEWAY_TOKEN=...      # shared với telegram-bot (khi có bot; hiện chỉ cần trên gateway)
PORT=18789
```

**Không** set `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` trên service production.

Bot chỉ cần:

```env
AI_PROVIDER=openclaw
OPENCLAW_BASE_URL=http://openclaw-gateway.railway.internal:18789/v1
OPENCLAW_GATEWAY_TOKEN=...      # cùng gateway
```

---

## 4. Plugin OpenClaw

| Plugin | Production |
|--------|------------|
| `google` | **enabled** |
| `active-memory`, `memory-wiki`, `document-extract` | enabled |
| `openai`, `deepseek` | **disabled** |
| `cursor-agent` | **disabled** (chỉ PC local) |
| `channels.telegram` | **disabled** |

---

## 5. Local PC (đồng bộ với production)

```powershell
node tools\set-local-gemini.mjs
openclaw gateway restart
powershell -File tools\check-isolation.ps1
```

Script đặt primary = `google/gemini-2.5-flash`, tắt telegram channel trùng bot, tắt openai/deepseek entries nếu có.

---

## 6. Ranh giới thiết kế

1. **Một provider LLM** — Gemini — dễ audit quota và chi phí.
2. **Bot không bypass Gateway** — memory / persona thống nhất (IDENTITY, SOUL).
3. **Tiền cước không do Gemini tính** — chỉ extract → `quote_engine`.
4. **Không fallback DeepSeek** khi Gateway lỗi — sửa Gateway / key Gemini, không đổi provider.

Xem thêm: [PLATFORM.md](./PLATFORM.md) §4 · [DEPLOY.md](./DEPLOY.md) · [ARCHITECTURE.md](./ARCHITECTURE.md)
