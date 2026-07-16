# Runbook vận hành — Vietnam Legal Research PoC

## Cấu hình

1. Copy biến `TVPL_*` từ `.env.example` (tuỳ chọn; mode mặc định `link-only`).
2. Production Railway (`openclaw-gateway`): plugin bake tại `/app/vendor-plugins/vietnam-legal-research`, skill tại `/app/workspace/skills/vietnam-legal-research`, `plugins.entries.vietnam-legal-research.enabled=true`, mode `link-only`.
3. Local OpenClaw: thêm plugin path `plugins/vietnam-legal-research` vào `plugins.load.paths` và allowlist tool nếu cần.
4. **Không** set `TVPL_ALLOW_BROWSER=true` trừ khi có giấy phép bằng văn bản.

## Sử dụng

Người dùng hỏi về luật/nghị định/thuế/hải quan… → skill kích hoạt → tool `vietnam_legal_research` trả:

- URL tra cứu TVPL (link)
- URL nguồn chính phủ liên quan
- Mẫu câu trả lời có disclaimer
- Ghi rõ phần chưa xác minh

## Sự cố

| Triệu chứng | Hành động |
|---|---|
| Tool báo `BROWSER_BLOCKED_BY_POLICY` | Đúng thiết kế; dùng link-only hoặc xin phép API |
| CAPTCHA / 403 / 429 (nếu fetch sau này) | Circuit breaker; thông báo user mở URL thủ công |
| Model bịa số hiệu | Nhắc skill: chỉ dùng URL tool trả về; không bịa |
| Paywall | Dừng; hướng dẫn đăng nhập thủ công trên TVPL |

## Observability

Log cấu trúc: requestId, latency, adapter, cacheHit, stopReason.  
Không log credential.
