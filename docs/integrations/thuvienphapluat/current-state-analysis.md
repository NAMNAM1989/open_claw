# Hiện trạng OpenClaw — tích hợp Thư Viện Pháp Luật

**Ngày khảo sát:** 2026-07-16  
**Trạng thái tích hợp đề xuất:** `APPROVED_FOR_LIMITED_POC`

## Kiến trúc OpenClaw hiện tại

```
Telegram → apps/telegram-bot (Python) → HTTP /v1/chat/completions
         → openclaw-gateway (Railway, openclaw@latest / template 2026.6.11)
         → Gemini → GPT-4o-mini → DeepSeek
```

| Thành phần | Path | Ghi chú |
|---|---|---|
| Gateway | `apps/gateway/` | Docker Node 22, volume `/root/.openclaw` |
| Telegram bot | `apps/telegram-bot/` | Thin client; không gọi web trực tiếp |
| Plugin local | `plugins/cursor-agent/` | Chỉ local, tắt trên Railway |
| Plugin template | `plugins/_template/` | Scaffold |
| Skills | `skills/` | Trống trước tích hợp này |
| Supabase | `supabase/migrations/` | Schema logistics; chưa có bảng pháp lý |

## Công nghệ

- Gateway: Node.js 22, OpenClaw CLI, config `openclaw.template.json`
- Bot: Python 3.12, pytest
- Plugin: TypeScript ESM, esbuild, vitest
- CI: GitHub Actions → Railway deploy
- Không có monorepo package manager ở root

## Công cụ có thể tái sử dụng

- Pattern plugin + vitest (`plugins/cursor-agent`, `plugins/_template`)
- HTTP client bot → gateway (`openclaw_client.py`)
- Allowlist Telegram (`ALLOWED_CHAT_IDS`)
- Workspace persona (`apps/gateway/workspace/`)
- Deploy bake plugin vào Docker (pattern deepseek-provider)

## Khoảng trống

1. Không có skill/plugin pháp lý trước đây
2. Production **deny** `group:web`, `browser`, `exec`, `process`, `canvas`, `group:ui`
3. `maxTokens: 250` — quá thấp cho phân tích pháp lý dài
4. Không queue/cron theo dõi văn bản
5. Không API client TVPL; không corpus nội bộ
6. Supabase chưa wired cho cache tra cứu pháp lý

## Rủi ro

| Rủi ro | Mức | Ghi chú |
|---|---|---|
| Điều khoản TVPL cấm công cụ tự động thu thập | Cao | Không scrape/crawler mặc định |
| Cloudflare / 403 khi fetch tự động | Trung bình | Đã quan sát khi fetch một số URL |
| Bật `browser`/`group:web` trên production | Cao | Phá mô hình bảo mật hiện tại |
| AI bịa số hiệu / hiệu lực | Cao | Cần citation + disclaimer bắt buộc |
| Prompt injection từ HTML | Trung bình | Nội dung web = untrusted |

## Giới hạn kỹ thuật

- Không dùng browser tool OpenClaw trên Railway hiện tại
- Live fetch TVPL không chạy trong CI
- PoC chỉ tạo link tra cứu + đối chiếu nguồn chính thức + parse fixture

## Giới hạn pháp lý (tóm tắt)

- Thỏa ước TVPL: cấm phần mềm/công cụ tự động truy cập, thu thập, tải hàng loạt
- robots.txt Content-Signal: `search=yes`, `ai-train=no`, `use=reference`
- Nhiều bot AI bị `Disallow`
- Chưa có API công khai đã xác minh cho tích hợp doanh nghiệp

## Đề xuất phương án tích hợp

**Chính:** Skill `vietnam-legal-research` + plugin chế độ `link-only` / nguồn chính phủ công khai.  
**Dự phòng:** API/data feed chính thức sau khi xin phép.  
**Không dùng:** Scraper/browser hàng loạt TVPL; lưu toàn văn; bypass CAPTCHA/paywall.

Chi tiết: `architecture-options.md`, `recommended-architecture.md`.
