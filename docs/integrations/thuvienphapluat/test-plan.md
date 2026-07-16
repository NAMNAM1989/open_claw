# Test plan

## Unit (CI)

- Chuẩn hóa số hiệu / ngày
- Parser metadata từ fixture
- Trạng thái hiệu lực
- Loại bỏ menu/ads + prompt injection
- Citation builder + answer guardrail
- Cache TTL + rate limiter
- Error mapping (CAPTCHA, 403, 429, paywall)
- Source-policy từ chối browser scrape TVPL
- Query classifier (số hiệu vs chủ đề)

## Integration (fixture)

Snapshot HTML trong `plugins/vietnam-legal-research/fixtures/`.  
CI **không** gọi thuvienphapluat.vn.

Kịch bản: tìm đúng số hiệu; không tìm thấy; nhiều kết quả; hết hiệu lực; thay thế; login required; CAPTCHA; 403; 429; timeout; đổi selector; tiếng Việt; redirect URL; nguồn mâu thuẫn; injection trong HTML.

## E2E live

```env
RUN_TVPL_LIVE_TESTS=false
```

Chỉ bật thủ công khi đã có phép và môi trường riêng.
