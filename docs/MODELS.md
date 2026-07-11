# Model AI — open_claw

**Chiến lược:** **Gemini** (chính) → **ChatGPT** → **DeepSeek** (fallback lần lượt khi lỗi/quota).

---

## 1. Luồng

```
telegram-bot → openclaw-gateway
                  ├─ google/gemini-3.5-flash     (primary)
                  ├─ openai/gpt-4o-mini          (fallback 1)
                  └─ deepseek/deepseek-v4-flash  (fallback 2)
```

OpenClaw tự chuyển model khi provider báo `rate_limit` / lỗi.

---

## 2. Model routing

| Vai trò | Model | Ghi chú |
|---------|-------|---------|
| Chat chính | `google/gemini-3.5-flash` | Primary |
| Fallback 1 | `openai/gpt-4o-mini` | ChatGPT (rẻ, nhanh) |
| Fallback 2 | `deepseek/deepseek-v4-flash` | Khi Gemini + GPT đều lỗi |

Config: `apps/gateway/openclaw.template.json`

---

## 3. Biến môi trường (Railway `openclaw-gateway`)

```env
GEMINI_API_KEY=AIza...
GOOGLE_API_KEY=AIza...          # cùng giá trị GEMINI
OPENAI_API_KEY=sk-...           # ChatGPT fallback
DEEPSEEK_API_KEY=sk-...         # fallback cuối
OPENCLAW_GATEWAY_TOKEN=...
PORT=18789
```

- OpenAI: [platform.openai.com](https://platform.openai.com)
- DeepSeek: [platform.deepseek.com](https://platform.deepseek.com)

---

## 4. Plugin OpenClaw

| Plugin | Production |
|--------|------------|
| `google` | **enabled** |
| `openai` | **enabled** (ChatGPT fallback) |
| `deepseek` | **enabled** (fallback cuối) |
| `active-memory`, `memory-wiki`, `document-extract` | **disabled** (tiết kiệm token) |
| `cursor-agent` | disabled |
| `channels.telegram` | disabled |

Token tiết kiệm: `thinkingDefault=off`, `maxTokens=250`, `heartbeat.every=0m`,
`contextInjection=continuation-skip`, `bootstrapMaxChars=1200`, `imageMaxDimensionPx=512`.
Bot chỉ gửi 1 tin hiện tại; ảnh dùng session `…:vision` tách biệt; `/baogia` `/pkl` không qua LLM.

Dockerfile cài DeepSeek provider vào `/app/vendor-plugins` (volume-safe). OpenAI đăng ký qua `models.providers.openai`.

---

## 5. Deploy sau khi thêm OpenAI

```powershell
# Thêm OPENAI_API_KEY (+ DEEPSEEK) vào .env.secrets
powershell -File tools\set-railway-secrets.ps1 -SkipTelegramBot

cd apps\gateway
railway up . --path-as-root --service openclaw-gateway --environment production --detach
```

---

## 6. Local PC

```powershell
node tools\set-local-gemini.mjs
openclaw gateway restart
```
