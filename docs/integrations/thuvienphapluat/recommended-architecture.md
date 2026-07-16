# Kiến trúc được chọn

**Trạng thái:** `APPROVED_FOR_LIMITED_POC`

```text
User / Telegram
       |
       v
OpenClaw Gateway (+ skill vietnam-legal-research)
       |
       v
Plugin vietnam-legal-research (default: link-only)
       |
       +--> Official Government Source Adapter  (URL builders)
       |
       +--> Public Search Adapter               (query templates; không scrape TVPL)
       |
       +--> Official API Adapter                (stub — chờ cấp phép)
       |
       +--> Browser Adapter                     (disabled; từ chối theo source-policy)
       |
       v
Normalizer + Citation Builder + Answer Guardrail
       |
       v
Response + nguồn + ngày kiểm tra + disclaimer
```

## Module trong repo

```text
skills/vietnam-legal-research/
plugins/vietnam-legal-research/src/
  integrations/  (logic TVPL + adapters)
  legal/         (citation, guardrail, classifier)
docs/integrations/thuvienphapluat/
```

## Chế độ vận hành (`TVPL_INTEGRATION_MODE`)

| Mode | Mô tả | Mặc định production |
|---|---|---|
| `link-only` | Tạo URL tra cứu TVPL + nguồn chính phủ; không HTTP tới TVPL | **Có** |
| `official` | Ưu tiên URL/cổng nhà nước | Tuỳ chọn |
| `public-search` | Sinh truy vấn `site:` (cần web tool) | Local only |
| `browser` | Bị source-policy chặn trừ khi `TVPL_ALLOW_BROWSER=true` **và** có giấy phép | **Không** |

## Không thay đổi trên production gateway

- Giữ `tools.deny` hiện tại (không bật browser/web hàng loạt).
- Plugin đăng ký tool `vietnam_legal_research` — chỉ trả link/metadata cấu trúc, không fetch TVPL.
- Không bake credential; không tăng crawl.

## Bảo mật tối thiểu

- Domain allowlist cho mọi fetch tương lai
- Rate limit + cache TTL (chỉ metadata/URL)
- Prompt-injection filter trên HTML fixture/parser
- Audit log không ghi secret
- Live tests tắt (`RUN_TVPL_LIVE_TESTS=false`)
