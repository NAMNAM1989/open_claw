# Plugin roadmap — open_claw

Lộ trình plugin trong monorepo, tách **local dev** vs **Railway production**.

---

## Hiện có

### `cursor-agent` v0.2.0

| | |
|---|---|
| **Môi trường** | Local PC only |
| **Chức năng** | `/cursor` → Cursor Agent CLI |
| **Production** | `enabled: false` trên gateway Railway |
| **Publish** | npm `openclaw-cursor-agent` (tùy chọn) |

---

## Phase 2 — `namnam-supabase` (đề xuất)

**Mục đích:** OpenClaw agent đọc/ghi context logistics từ Supabase trong hội thoại.

| Tool | Mô tả |
|------|--------|
| `lookup_booking` | Tra booking pending/recent theo chat_id |
| `lookup_quote` | Tra `quote_code` |
| `log_ops_note` | Ghi `ops_log` từ agent |

**Runtime:** Gateway Railway — cần `SUPABASE_URL` + service key (chỉ gateway, không public).

**Rủi ro:** Agent tự ghi DB — giới hạn tool allowlist, read-mostly giai đoạn đầu.

---

## Phase 3 — `logistics-vision` (đề xuất)

**Mục đích:** Prompt template chuẩn cho vision logistics (thay prompt rải rác trong Python).

| Task | Output schema |
|------|---------------|
| `classify_document` | `scale_ticket \| tariff \| invoice \| awb \| unknown` |
| `extract_tariff` | `PriceRow[]` |
| `extract_scale` | `ScaleTicket` |

Bot gọi qua OpenClaw tool hoặc HTTP task endpoint.

---

## Phase 4 — `github-ops` (tùy chọn)

Bật skill `github` bundled OpenClaw:

- Tạo issue từ lỗi eCargo lặp (`ops_log` → issue template)
- Link PR deploy

Cần `GITHUB_TOKEN` read-only trên gateway.

---

## Template mới

```powershell
Copy-Item -Recurse plugins\_template plugins\namnam-supabase
# Sửa openclaw.plugin.json, implement tools
```

Thêm vào `apps/gateway/openclaw.template.json` (runtime: entrypoint ghi `~/.openclaw/openclaw.json`):

```json
"plugins": {
  "load": { "paths": ["/app/plugins/namnam-supabase"] }
}
```

Build gateway Docker: `COPY plugins/ /app/plugins/`.

---

## Ma trận plugin × môi trường

| Plugin | Local | Gateway Railway |
|--------|-------|-----------------|
| cursor-agent | ✅ | ❌ |
| active-memory (bundled) | ✅ | ✅ |
| memory-wiki (bundled) | ✅ | ✅ |
| document-extract (bundled) | ✅ | ✅ |
| namnam-supabase | dev | ✅ (phase 2) |
| logistics-vision | dev | ✅ (phase 3) |
| github skill | dev | optional |

---

## Tiêu chí accept plugin mới

1. Có `npm test` / vitest
2. Không hardcode secret
3. Document trong `plugins/<name>/README.md`
4. `enabled: false` mặc định cho đến khi production-ready
