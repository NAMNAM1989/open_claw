# Runbook vận hành — open_claw

Production Railway: **chỉ `openclaw-gateway`**.

---

## 1. Dashboard nhanh

| Cần xem | Nơi |
|---------|-----|
| Log Gateway | Railway → `openclaw-gateway` → Logs |
| DB / SQL | Supabase Dashboard |
| Gemini quota | [Google AI Studio](https://aistudio.google.com) |
| Code | GitHub → `open_claw` |

---

## 2. Deploy code mới

```powershell
git push origin main
# Hoặc:
cd apps\gateway
npx @railway/cli redeploy --service openclaw-gateway --environment production
```

---

## 3. Gateway không phản hồi / lỗi model

| Bước | Việc |
|------|------|
| 1 | Railway → `openclaw-gateway` → Logs |
| 2 | Kiểm tra `GEMINI_API_KEY` / `GOOGLE_API_KEY` (AI Studio) |
| 3 | Xác nhận model = `google/gemini-3.5-flash` trong template |
| 4 | `powershell -File tools\set-railway-secrets.ps1` + redeploy |
| 5 | Xem [MODELS.md](./MODELS.md) |

---

## 4. Supabase

```bash
supabase link --project-ref ikcavxwchowbgrkhfxra
supabase db push
```

---

## 5. Rotate token gateway

Đổi `OPENCLAW_GATEWAY_TOKEN` trong `.env.secrets` → `set-railway-secrets.ps1` → redeploy.

---

## 6. Dọn Railway cũ

Xóa project **`telegram_bot`** (trống) trên Railway Dashboard nếu chưa xóa.
