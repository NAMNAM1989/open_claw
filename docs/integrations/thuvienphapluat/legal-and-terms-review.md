# Kiểm tra điều khoản & quyền sử dụng — Thư Viện Pháp Luật

**Nguồn chính:** [Thỏa ước dịch vụ](https://thuvienphapluat.vn/page/viewcontentleft.aspx?key=20) (khảo sát 2026-07-16)  
**robots.txt:** https://thuvienphapluat.vn/robots.txt

## Tóm tắt điều khoản quan trọng

1. Dùng lại thông tin **phi thương mại** phải ghi nguồn: “Theo www.ThuVienPhapLuat.vn”.
2. **Cấm** dùng dữ liệu để phát triển hệ thống lưu trữ/tra cứu khác nhằm mục đích thương mại.
3. **Cấm** phần mềm hoặc công cụ tự động truy cập, thu thập hoặc tải xuống nội dung.
4. **Cấm** tải xuống liên tục/lặp lại mang tính hệ thống (thủ công hoặc tự động) để sao chép CSDL.
5. Không chia sẻ tài khoản/mật khẩu; giới hạn số người dùng đồng thời theo gói.
6. Bản quyền đã đăng ký (theo thỏa ước: GCN bản quyền số 416/2021/QTG).

## robots.txt / Content-Signal

```
Content-Signal: search=yes, ai-train=no, use=reference
Allow: /
```

- Nhiều bot AI (`GPTBot`, `ClaudeBot`, `Google-Extended`, …) bị `Disallow: /`.
- `ai-train=no` — không dùng nội dung để train/fine-tune.
- `use=reference` — tín hiệu tham chiếu; **không** đồng nghĩa được phép RAG hàng loạt.
- `ai-input` không khai báo → không suy diễn là được phép grounding AI tự động.

## Bảng đánh giá quyền sử dụng

| Hạng mục | Có thể dùng | Cần xin phép | Không nên dùng | Ghi chú |
|---|---:|---:|---:|---|
| Link tới văn bản | ✓ | | | Ưu tiên; dẫn nguồn rõ |
| Metadata văn bản | | ✓ | | Cache metadata ngắn cần làm rõ với NCC |
| Trích đoạn ngắn | | ✓ | | Phi thương mại + attribution; AI tóm tắt cần hỏi |
| Nội dung toàn văn | | ✓ | ✓* | *Không lưu DB nội bộ |
| File Word/PDF | | ✓ | ✓* | Thường thuộc gói trả phí |
| Nội dung trả phí | | ✓ | ✓ | Không vượt paywall |
| Tự động tìm kiếm | | ✓ | ✓* | Thỏa ước cấm công cụ tự động |
| Theo dõi thay đổi | | ✓ | ✓* | Cần RSS/webhook chính thức |
| Lưu cache | | ✓ | | Chỉ URL/metadata/TTL ngắn nếu được phép |
| Tái phân phối | | | ✓ | Cấm hệ thống tra cứu cạnh tranh |

\*Mặc định PoC: **không triển khai** cho đến khi có văn bản đồng ý.

## Kết luận pháp lý cho OpenClaw

- **Không** `APPROVED_FOR_PRODUCTION` khi chưa có thỏa thuận cấp phép.
- PoC chỉ được: skill hướng dẫn, tạo link tra cứu do người dùng yêu cầu, đối chiếu nguồn chính phủ công khai, parse fixture nội bộ, disclaimer pháp lý.
- Trạng thái: `APPROVED_FOR_LIMITED_POC` (và các phần scrape TVPL = `BLOCKED_PENDING_PERMISSION`).
