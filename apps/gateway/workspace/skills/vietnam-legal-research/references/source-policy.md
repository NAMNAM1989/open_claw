# Source policy

## Cho phép (PoC)

- Tạo và chia sẻ URL tra cứu do người dùng yêu cầu
- Dẫn nguồn chính phủ công khai
- Parse HTML fixture nội bộ / dữ liệu đã được cấp phép
- Cache URL + metadata ngắn với TTL (khi được phép)

## Cần xin phép

- Tự động HTTP/browser tới thuvienphapluat.vn
- Cache trích đoạn / tình trạng hiệu lực quy mô lớn
- Tải PDF/Word; theo dõi chủ đề định kỳ

## Cấm

- Công cụ tự động thu thập/tải hàng loạt từ TVPL
- Xây CSDL tra cứu cạnh tranh từ dữ liệu TVPL
- Train/fine-tune model bằng nội dung TVPL (`ai-train=no`)
- Vượt CAPTCHA/paywall; chia sẻ credential

## Attribution

Khi dùng lại thông tin từ TVPL theo điều khoản phi thương mại: ghi rõ  
“Theo www.ThuVienPhapLuat.vn” và URL cụ thể.
