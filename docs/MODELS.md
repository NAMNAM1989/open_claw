# Model AI — open_claw (Gemini only)

**Quyết định thiết kế:** LLM của nền tảng NamNam Ops dùng **Google Gemini** qua OpenClaw Gateway.

Không dùng DeepSeek / ChatGPT (OpenAI) cho production.

---

## 1. Vai trò

```
Client (HTTP / plugin / Cursor)
    → openclaw-gateway       (OpenClaw HTTP /v1)
        → Google Gemini API  (GEMINI_API_KEY)
```

| Thành phần | Gọi LLM? | Provider |
|------------|----------|----------|
| `openclaw-gateway` | Có | **Gemini only** |
| `cursor-agent` (local) | N/A | Dev tool |

---

## 2. Model routing

| Tác vụ | Model | Ghi chú |
|--------|-------|---------|
| Chat, intent | `google/gemini-3.5-flash` | Primary mặc định |
| Vision / extract | `google/gemini-3.5-flash` | Multimodal |
| Task nặng (tuỳ chọn) | `google/gemini-2.5-pro` hoặc `google/gemini-3.5-flash` thinking=high | Đổi trên agent nếu cần |

Config: `apps/gateway/openclaw.template.json`

> `gemini-2.5-flash` không còn cho user API mới — đã migrate sang **3.5 Flash**.

---

## 3. Biến môi trường (Railway `openclaw-gateway`)

```env
GEMINI_API_KEY=AIza...
GOOGLE_API_KEY=AIza...          # cùng giá trị
OPENCLAW_GATEWAY_TOKEN=...
PORT=18789
```

**Không** set `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` trên production.

---

## 4. Plugin OpenClaw

| Plugin | Production |
|--------|------------|
| `google` | **enabled** |
| `active-memory`, `memory-wiki`, `document-extract` | enabled |
| `openai`, `deepseek`, `cursor-agent` | **disabled** |
| `channels.telegram` | **disabled** |

---

## 5. Local PC

```powershell
node tools\set-local-gemini.mjs
openclaw gateway restart
powershell -File tools\check-isolation.ps1
```
