# Phân tích website Thư Viện Pháp Luật

**URL:** https://thuvienphapluat.vn/  
**Ngày khảo sát:** 2026-07-16  
**Phương pháp:** HTTP fetch công khai + robots.txt + trang thỏa ước; không dùng DevTools live đầy đủ do một số endpoint trả 403/timeout.

## 4.1 Chức năng quan sát được

| Hạng mục | Quan sát |
|---|---|
| Trang chủ | Portal tra cứu VBPL, bản án, tiện ích DN; chào mời gói Free/Basic/Pro |
| Tìm kiếm | Form/query `tim-van-ban` / keyword (URL tìm kiếm timeout khi fetch tự động) |
| Chi tiết văn bản | Metadata: số hiệu, tên, cơ quan, ngày BH, hiệu lực, quan hệ VB (lược đồ) — theo tài liệu marketing |
| Nội dung Free vs trả phí | Free: tra cứu cơ bản; Basic/Pro: tải PDF/Word, lược đồ đầy đủ, tiếng Anh, TCVN… |
| Đăng nhập | Bắt buộc cho nhiều tiện ích thành viên |
| RSS / sitemap | `sitemap.xml`, `resitemap.xml` trong robots.txt |
| API công khai | Thỏa ước nhắc “trang web liên kết API, Iframe” nhưng **không** tìm thấy tài liệu API mở cho bên thứ ba |
| Widget / mobile | Có app / nền tảng liên kết (chưa khảo sát sâu) |

## 4.2 Phân tích kỹ thuật

| Hạng mục | Kết luận tạm thời | Độ tin cậy |
|---|---|---|
| HTML | Hỗn hợp ASP.NET (`.aspx`) + nội dung server-rendered | Trung bình |
| Cloudflare / WAF | Có (robots.txt Cloudflare Managed; một số fetch 403) | Cao |
| CAPTCHA | Có khả năng khi đăng ký/tra cứu nâng cao (chưa bắt live trong PoC) | Thấp–TB |
| Rate limit | Chưa đo được; thiết kế PoC giả định 5 req/phút | Giả định |
| Encoding | Tiếng Việt Unicode | Cao |
| Schema.org / OG | Chưa xác minh đầy đủ do 403 | Chưa xác minh |
| Endpoint JSON nội bộ | **Không** dùng cho production nếu không được công bố | N/A |

**Không khai thác** endpoint nội bộ chưa công bố.

## 4.3 Điểm chưa xác minh

- Selector DOM ổn định trên trang chi tiết
- Cookie/session/CSRF chi tiết của form tìm kiếm
- Hành vi CAPTCHA theo IP/user-agent
- Tồn tại API thương mại / data feed doanh nghiệp (cần hỏi nhà cung cấp)

## Hệ quả cho tích hợp

1. Fetch tự động dễ bị chặn → không dựa vào scrape cho CI/production.
2. Nội dung giá trị (toàn văn, PDF) nằm sau gói trả phí → không lấy khi chưa có quyền.
3. PoC dùng: URL tra cứu có chủ đích + nguồn chính phủ + fixture HTML cho parser.
