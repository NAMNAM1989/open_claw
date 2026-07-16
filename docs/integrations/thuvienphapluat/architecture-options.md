# So sánh phương án tích hợp

Thang điểm 1–5 (cao = tốt hơn). “Rủi ro bị khóa / bản quyền”: cao điểm = rủi ro thấp.

## Phương án 1 — API / hợp tác chính thức

| Tiêu chí | Điểm | Ghi chú |
|---|---:|---|
| Hợp pháp | 5 | Có hợp đồng/SLA |
| Ổn định | 5 | Endpoint chính thức |
| Độ chính xác | 5 | Metadata hiệu lực từ nguồn |
| Chi phí | 2 | Có thể trả phí |
| Tốc độ | 5 | |
| Bảo trì | 5 | |
| Mở rộng | 5 | |
| Rủi ro bị khóa | 5 | |
| Rủi ro bản quyền | 5 | |
| Phù hợp OpenClaw | 5 | Plugin adapter sạch |
| **Tổng** | **47** | **Ưu tiên cao nhất — chưa có API xác minh** |

## Phương án 2 — OpenClaw browser tool

| Tiêu chí | Điểm | Ghi chú |
|---|---:|---|
| Hợp pháp | 1 | Thỏa ước cấm công cụ tự động |
| Ổn định | 2 | Cloudflare/CAPTCHA |
| Độ chính xác | 3 | Phụ thuộc DOM |
| Chi phí | 4 | |
| Tốc độ | 2 | |
| Bảo trì | 2 | Selector dễ gãy |
| Mở rộng | 1 | |
| Rủi ro bị khóa | 1 | |
| Rủi ro bản quyền | 1 | |
| Phù hợp OpenClaw | 2 | Production đang deny browser |
| **Tổng** | **19** | **Không dùng mặc định** |

## Phương án 3 — Skill hướng dẫn tra cứu

| Tiêu chí | Điểm | Ghi chú |
|---|---:|---|
| Hợp pháp | 5 | Không scrape |
| Ổn định | 4 | Phụ thuộc model + prompt |
| Độ chính xác | 3 | Cần nguồn + disclaimer |
| Chi phí | 5 | |
| Tốc độ | 4 | |
| Bảo trì | 4 | |
| Mở rộng | 3 | |
| Rủi ro bị khóa | 5 | |
| Rủi ro bản quyền | 5 | |
| Phù hợp OpenClaw | 5 | `skills/` sẵn |
| **Tổng** | **43** | **Phương án chính cho PoC** |

## Phương án 4 — Public search (`site:thuvienphapluat.vn`)

| Tiêu chí | Điểm | Ghi chú |
|---|---:|---|
| Hợp pháp | 3 | Search signal=yes; không thay API |
| Ổn định | 3 | Phụ thuộc công cụ tìm kiếm |
| Độ chính xác | 3 | |
| Chi phí | 5 | |
| Tốc độ | 3 | |
| Bảo trì | 3 | |
| Mở rộng | 2 | Không copy hàng loạt |
| Rủi ro bị khóa | 3 | |
| Rủi ro bản quyền | 3 | Chỉ link + snippet ngắn |
| Phù hợp OpenClaw | 2 | `group:web` đang deny |
| **Tổng** | **30** | **Dự phòng local khi bật web có kiểm soát** |

## Phương án 5 — Nguồn pháp luật chính thức bổ sung

| Tiêu chí | Điểm | Ghi chú |
|---|---:|---|
| Hợp pháp | 5 | Cổng nhà nước công khai |
| Ổn định | 3 | UX/site đa dạng |
| Độ chính xác | 4 | Nguồn gốc; cần đối chiếu |
| Chi phí | 5 | |
| Tốc độ | 3 | |
| Bảo trì | 3 | |
| Mở rộng | 4 | |
| Rủi ro bị khóa | 4 | |
| Rủi ro bản quyền | 4 | |
| Phù hợp OpenClaw | 4 | Adapter URL + skill |
| **Tổng** | **39** | **Luôn kèm theo mọi câu trả lời rủi ro cao** |

## Quyết định

| Vai trò | Phương án |
|---|---|
| **Chính (PoC)** | 3 — Skill + plugin `link-only` / citation guardrail |
| **Bổ trợ** | 5 — Official government source adapter |
| **Dự phòng** | 1 — API chính thức (sau xin phép); 4 — public search local |
| **Không dùng** | 2 — Browser scrape TVPL; crawler; bypass CAPTCHA/paywall |
