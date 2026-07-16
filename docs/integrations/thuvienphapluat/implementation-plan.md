# Kế hoạch triển khai

## Đã làm (PoC)

1. Khảo sát repo + điều khoản TVPL
2. Docs đầy đủ dưới `docs/integrations/thuvienphapluat/`
3. Skill `skills/vietnam-legal-research/`
4. Plugin `plugins/vietnam-legal-research/` (link-only MVP)
5. Unit test + fixture HTML
6. Biến môi trường trong `.env.example`

## MVP mapping

| MVP | Trạng thái PoC | Ghi chú |
|---|---|---|
| MVP-1 Tra cứu số hiệu | Done (URL + classifier) | Không scrape live |
| MVP-2 Theo chủ đề | Done (query expand + links) | |
| MVP-3 Tóm tắt có nguồn | Partial | Guardrail bắt buộc nguồn; tóm tắt do model + skill |
| MVP-4 So sánh VB | Stub fields `amendedBy`/`replacedBy` | Cần API/nguồn được phép |
| MVP-5 Theo dõi chủ đề | **Không triển khai** | Chờ RSS/webhook chính thức |

## Giai đoạn tiếp theo (sau xin phép)

1. Liên hệ TVPL (xem `contact-and-licensing-questions.md`)
2. Nếu có API: implement `OfficialApiAdapter`, bật mode có kiểm soát
3. Tăng `maxTokens` cho agent pháp lý (agent riêng hoặc override)
4. Cache metadata trên Supabase với TTL
5. CI riêng cho plugin; bake vào gateway khi `enabled: false` mặc định rồi bật dần
6. E2E thủ công với `RUN_TVPL_LIVE_TESTS=true` trên môi trường được phép

## Rollback

- Xóa/disable plugin path trong config
- Skill không ảnh hưởng runtime nếu không load
- Không đụng `tools.deny` production trong PoC này
