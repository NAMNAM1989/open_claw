# Kết quả kiểm tra — open_claw (local)

Chạy ngày: 2026-07-10

## Lệnh kiểm tra

```powershell
cd C:\Project\open_claw

# Plugin cursor-agent
cd plugins\cursor-agent
npm ci
npm test
npm run build

# Scaffold platform
powershell -File tools\check-platform.ps1

# Gateway Docker smoke
powershell -File tools\smoke-gateway.ps1
```

---

## Kết quả

| Hạng mục | Kết quả | Ghi chú |
|----------|---------|---------|
| `cursor-agent` tests | **123 passed** (4 skipped) | vitest |
| `cursor-agent` build | **OK** | dist/index.js |
| `check-platform.ps1` | **OK** | 15/15 file/config |
| Docker build gateway | **OK** | openclaw-gateway-test |
| Gateway startup | **OK** | `[gateway] ready` |
| `GET /health` | **OK** | `{"ok":true}` |
| `GET /v1/models` + Bearer | **OK** | `openclaw/default` |
| `openclaw config validate` | **OK** | sau sửa template |
| `telegram-bot` pytest | **28 passed** | greenfield trong monorepo |
| Supabase migration live | **Chưa chạy** | cần SQL Editor / `supabase db push` |
| Gemini chat thật | **Chưa** | cần `GEMINI_API_KEY` hợp lệ trên Railway |

---

## Lỗi đã sửa trong quá trình test

1. **CRLF** `docker-entrypoint.sh` → Dockerfile `sed -i 's/\r$//'` + `.gitattributes`
2. **openclaw.template.json** invalid:
   - Bỏ `meta.description`
   - Bỏ `model.fallback` (schema không hỗ trợ)
   - Thêm `gateway.mode: local`
   - `memorySearch.enabled: false`
   - Bật plugin `google`
3. **Session dir** — entrypoint `mkdir -p agents/default/sessions`

---

## Trước deploy Railway

- [ ] Đặt `GEMINI_API_KEY` thật trên service `openclaw-gateway`
- [ ] Đặt `OPENCLAW_GATEWAY_TOKEN` (hex/alphanumeric, ≥32 ký tự) — **cùng giá trị** trên bot
- [ ] Chạy Supabase migrations (`initial` + `storage`)
- [ ] `powershell -File tools\check-isolation.ps1` — tắt Telegram channel OpenClaw trên PC local

---

## Script tái kiểm tra

| Script | Mục đích |
|--------|----------|
| `tools/check-platform.ps1` | File + config template |
| `tools/smoke-gateway.ps1` | Docker gateway end-to-end |
