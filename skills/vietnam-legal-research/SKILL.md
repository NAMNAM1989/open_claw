---
name: vietnam-legal-research
description: >
  Tra cứu và trả lời câu hỏi pháp lý Việt Nam (luật, nghị định, thông tư, thuế,
  hải quan, logistics, lao động, doanh nghiệp). Dùng khi người dùng hỏi hiệu lực
  văn bản, nghĩa vụ pháp lý, hoặc cần nguồn dẫn chiếu. Ưu tiên link nguồn chính
  thức và Thư Viện Pháp Luật; không scrape hàng loạt; không khẳng định tư vấn luật sư.
---

# Vietnam Legal Research

## Trigger

Kích hoạt khi người dùng hỏi về: luật, nghị định, thông tư, quyết định, công văn,
hiệu lực văn bản, thuế, hóa đơn, hải quan, xuất nhập khẩu, logistics, vận tải,
lao động, bảo hiểm, doanh nghiệp, hợp đồng, xử phạt, thủ tục hành chính.

## Quy trình

1. Chuẩn hóa câu hỏi; xác định lĩnh vực và mốc thời gian áp dụng.
2. Tìm số hiệu hoặc từ khóa.
3. Gọi tool `vietnam_legal_research` nếu có (mode `link-only` mặc định).
4. Ưu tiên nguồn chính phủ công khai; kèm link Thư Viện Pháp Luật để người dùng tự mở.
5. Thu thập metadata **chỉ khi** tool/adapter trả về hợp lệ — không bịa.
6. Kiểm tra hiệu lực nếu dữ liệu có; nếu không chắc → ghi `unknown`.
7. Với câu hỏi rủi ro cao: đối chiếu ít nhất một nguồn khác (cổng nhà nước).
8. Trả lời theo `references/response-format.md`.
9. Nêu rõ phần chưa xác minh; phân biệt dữ liệu nguồn / tóm tắt / suy luận AI.
10. Không đưa hành động pháp lý quan trọng chỉ dựa trên tóm tắt AI.

## Quy tắc dừng

Dừng và thông báo khi: CAPTCHA, paywall, cần đăng nhập không có phiên hợp lệ,
điều khoản không cho phép tự động hóa, không xác minh được, nguồn mâu thuẫn,
không xác định hiệu lực, user yêu cầu sao chép hàng loạt / toàn bộ CSDL.

## Cấm

- Vượt CAPTCHA / paywall; xoay proxy; giả mạo trình duyệt
- Hard-code tài khoản; lưu toàn văn vào DB
- Tạo URL giả hoặc số hiệu bịa
- Tự nhận là luật sư hoặc kết luận pháp lý tuyệt đối

Xem thêm: `references/source-policy.md`, `references/legal-disclaimer.md`.
