# Checklist deploy — open_claw (Railway + Supabase)

Hướng dẫn deploy lần đầu và mỗi lần release. Thứ tự: **Supabase → Gateway → Bot**.

---

## 0. Trước khi deploy (local)

### Test tu dong

```powershell
cd C:\Project\open_claw
powershell -File tools\local-test.ps1          # day du (co Docker)
powershell -File tools\local-test.ps1 -SkipDocker   # nhanh (~30s)
```

Ky vong: **28 pytest pass**, cursor-agent 123 pass.

### Tach biet khoi bot cu (telegram_bot)

Project `open_claw` **doc lap** — khong migrate/copy tu `C:\Project\telegram_bot`.

```powershell
powershell -File tools\check-isolation.ps1
```

| Rui ro | Cach tranh |
|--------|------------|
| 2 bot cung `TELEGRAM_BOT_TOKEN` | Chi **mot** process poll Telegram: `apps/telegram-bot` tren Railway |
| OpenClaw local + Railway cung token | Tat `channels.telegram` trong `~/.openclaw/openclaw.json` tren PC |
| Gateway Railway bat Telegram channel | Template da `enabled: false` — khong bat them |
| Token cu trong OpenClaw channel | Tao token **moi** BotFather cho Railway bot |

Sua config local (neu `check-isolation` WARN):

```powershell
node tools\restore-cursor-agent-config.mjs   # tro project map ve apps\telegram-bot
# Mo ~/.openclaw/openclaw.json -> channels.telegram.enabled = false
openclaw gateway restart
```

### Test thu cong Telegram

```powershell
Copy-Item .env.example apps\telegram-bot\.env
# Sua TELEGRAM_BOT_TOKEN, OPENCLAW_*, SUPABASE_* trong .env

cd apps\telegram-bot
python scripts\check_config.py
python -m bot.main
```

Gateway local: `powershell -File tools\smoke-gateway.ps1` (port 18792)

---

## 1. GitHub

| # | Việc | Xong |
|---|------|------|
| 1.1 | Push repo `open_claw` lên GitHub | ☐ |
| 1.2 | Branch `main` protected (khuyến nghị) | ☐ |
| 1.3 | GitHub Secrets: `RAILWAY_TOKEN` | ☐ |
| 1.4 | GitHub Secrets: `RAILWAY_PROJECT_ID` | ☐ |

---

## 2. Supabase (project `open_claw`)

| # | Việc | Lệnh / ghi chú |
|---|------|----------------|
| 2.1 | Tạo project Supabase tên `open_claw` | Dashboard |
| 2.2 | Cài Supabase CLI | `npm i -g supabase` |
| 2.3 | Link project | `supabase link --project-ref <REF>` |
| 2.4 | Chạy migration | `supabase db push` |
| 2.5 | Xác nhận bảng | `bookings`, `job_runs`, `tariffs`, `quotes`, `scale_tickets`, `ops_log` |
| 2.6 | Lưu credentials | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (chỉ Railway bot) |

**Hoặc** copy SQL từ `supabase/migrations/*.sql` vào SQL Editor.

RLS đã bật — chỉ **service role** trên bot production.

---

## 3. Gemini API (LLM duy nhất)

| # | Việc |
|---|------|
| 3.1 | Tạo key tại [Google AI Studio](https://aistudio.google.com) |
| 3.2 | Lưu `GEMINI_API_KEY` + `GOOGLE_API_KEY` (cùng giá trị) trên gateway Railway |
| 3.3 | **Không** cấu hình OpenAI / DeepSeek trên production |
| 3.4 | Xem [MODELS.md](./MODELS.md) — thiết kế model |

Local PC đồng bộ Gemini:

```powershell
node tools\set-local-gemini.mjs
openclaw gateway restart
```

---

## 4. Railway — project `open_claw`

Tạo **2 service** trong cùng project:

| Service | Root Directory | Public |
|---------|----------------|--------|
| `openclaw-gateway` | `apps/gateway` | **Không** |
| `telegram-bot` | `apps/telegram-bot` | **Không** |

Link GitHub repo → Railway auto-deploy (hoặc dùng workflow `deploy-railway.yml`).

### 4.1 Sync workspace (nếu đổi persona)

```powershell
Copy-Item apps\telegram-bot\workspace\* apps\gateway\workspace\ -Force
```

Rebuild **gateway** sau khi đổi `IDENTITY.md` / `SOUL.md`.

---

## 5. Service `openclaw-gateway` — biến môi trường

| Biến | Bắt buộc | Ghi chú |
|------|----------|---------|
| `GEMINI_API_KEY` | ✅ | |
| `GOOGLE_API_KEY` | ✅ | Cùng giá trị GEMINI |
| `OPENCLAW_GATEWAY_TOKEN` | ✅ | Chuỗi random ≥ 32 ký tự |
| `PORT` | ✅ | `18789` |

**Không** bật `channels.telegram` trên gateway (tránh trùng bot token).

### Smoke test gateway

```powershell
powershell -File tools\smoke-gateway.ps1
```

Hoặc sau deploy:

```bash
curl -sS http://<internal>:18789/v1/models -H "Authorization: Bearer $TOKEN"
```

---

## 6. Service `telegram-bot` — biến môi trường

### Bắt buộc

| Biến | Ví dụ |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | BotFather |
| `ALLOWED_CHAT_IDS` | `-1001234567890` (lấy bằng `/chatid`) |
| `SUPABASE_URL` | `https://xxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | service role |
| `OPENCLAW_BASE_URL` | `http://openclaw-gateway.railway.internal:18789/v1` |
| `OPENCLAW_GATEWAY_TOKEN` | **Cùng** token gateway |
| `AI_PROVIDER` | `openclaw` |

### Ops eCargo

| Biến | Production |
|------|------------|
| `ECARGO_DRY_RUN` | `false` khi sẵn sàng chạy thật |
| `ECARGO_STORAGE_STATE` | `data/ecargo_storage.json` |
| `GMAIL_USER` | Email ops |
| `GMAIL_APP_PASSWORD` | App password Google |
| `MAIL_WATCH_ENABLED` | `true` khi cần auto QR mail |

### Feature flags

| Biến | Mặc định |
|------|----------|
| `OPS_ENABLED` | `true` |
| `CHAT_ENABLED` | `true` |
| `IMAGE_READER_ENABLED` | `true` |
| `SCALE_TICKET_OCR_ENABLED` | `true` |
| `QUOTE_ENGINE_ENABLED` | `true` |

### Volume Railway

Mount volume → `/app/data` cho:

- `ecargo_storage.json` (session eCargo)
- (tuỳ chọn) `allowed_chat_ids.txt`

**Lưu session eCargo (máy dev):**

```powershell
cd apps\telegram-bot
python scripts\save_ecargo_session.py
# Upload data/ecargo_storage.json lên Railway Volume
```

---

## 7. Thứ tự deploy an toàn

```
1. supabase db push
2. Deploy openclaw-gateway  → verify /v1/models
3. Set OPENCLAW_GATEWAY_TOKEN trên CẢ HAI service
4. Deploy telegram-bot
5. Smoke test Telegram
```

**Rotate token:** đổi `OPENCLAW_GATEWAY_TOKEN` trên cả 2 service cùng lúc, redeploy cả hai.

---

## 8. Smoke test production (Telegram)

Gửi trong nhóm đã allowlist:

| # | Lệnh / hành động | Kỳ vọng |
|---|------------------|---------|
| 8.1 | `/ping` | `pong` |
| 8.2 | `/chatid` | Trả ID nhóm |
| 8.3 | `/import_gia` + Excel mẫu | Import tariff OK |
| 8.4 | `/bao_gia SGN-HKG 120` | Quote + mã Q-xxx |
| 8.5 | Gửi booking 5 dòng → `có` | Job eCargo (dry-run hoặc thật) |
| 8.6 | `/status` | Job gần nhất |
| 8.7 | Ảnh + `/gia` | Tariff từ vision (cần Gemini) |
| 8.8 | `/ask Trạng thái booking?` | Trả lời có context |
| 8.9 | `/ops tuan` | Báo cáo ops |
| 8.10 | `/sales tuan` | Báo cáo sales |

---

## 9. Giám sát sau deploy

| Nơi | Xem gì |
|-----|--------|
| Railway → `telegram-bot` logs | Startup health, OpenClaw, eCargo session |
| Railway → `openclaw-gateway` logs | Gateway crash, Gemini quota |
| Supabase → `ops_log` | `source=openclaw`, `ecargo`, `gmail` |
| Google AI Studio | Quota Gemini |

---

## 10. Rollback nhanh

| Sự cố | Xử lý |
|-------|-------|
| Bot im lặng | Kiểm tra 2 instance cùng `TELEGRAM_BOT_TOKEN` |
| `/ask` / `/gia` lỗi | Gateway down hoặc token sai |
| eCargo fail | Session hết hạn → `save_ecargo_session.py` |
| Quote sai | Tariff OCR lỗi → `/import_gia` Excel |

Redeploy bản trước: Railway → Deployment → Rollback.

---

## 11. Liên quan

- [PLATFORM.md](./PLATFORM.md) — kiến trúc
- [RUNBOOK.md](./RUNBOOK.md) — vận hành hàng ngày
- [DATA.md](./DATA.md) — schema Supabase
- `tools/check-platform.ps1` — kiểm tra scaffold
- `tools/smoke-gateway.ps1` — smoke gateway Docker
