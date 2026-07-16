# Security review — tích hợp pháp lý PoC

## Credential

- Biến `TVPL_*` trong `.env.example`; không hard-code
- Không bắt buộc username/password ở mode `link-only`
- Cấm log cookie/password/token

## Browser profile

- Browser adapter **disabled** mặc định
- Nếu bật sau này: profile riêng, domain allowlist, không dùng profile cá nhân

## Prompt injection

- Mọi HTML từ web = untrusted
- `stripPromptInjection` / tách menu-ads trong parser
- Tool không thực thi chỉ dẫn trong nội dung trang

## Audit

- `audit-log.ts`: requester, query, adapter, URL, success/fail, stop reason
- Không ghi nội dung nhạy cảm

## Production posture

- Không nới `tools.deny` trong PoC
- Không crawler; circuit breaker sẵn cho 403/429/CAPTCHA khi có fetch
- Rate limit mặc định 5 req/phút; 1 browser task đồng thời (khi được phép)

## Residual risks

| Rủi ro | Giảm thiểu |
|---|---|
| Model bịa văn bản | Citation builder + “không tạo URL giả” |
| User yêu cầu toàn văn trả phí | Stop rule + thông báo |
| Bật nhầm mode browser | Source-policy + env gate kép |
