# OpenClaw — Plugin-first workspace

Workspace phát triển **plugin / skill** cho [OpenClaw](https://github.com/openclaw/openclaw), không fork core.

## Cần đăng nhập gì?

**Không cần.** Plugin đã chạy local qua Gateway; npm / ClawHub / GitHub chỉ khi muốn **phát hành công khai**.

| Mục tiêu | Cần login? |
|----------|------------|
| Sửa code, `npm test` / `npm run build`, dùng `/cursor` trên máy | **Không** |
| Người khác cài qua npm | Chỉ `npm login` |
| List trên ClawHub | Thêm `clawhub login` + repo GitHub |

Đừng chạy `tools/finish-publish.ps1` / `tools/login-all.ps1` trừ khi bạn chủ động muốn publish.

## Cấu trúc

```
open_claw/
├── plugins/
│   ├── cursor-agent/     # Plugin chính (đang phát triển)
│   └── _template/        # Scaffold plugin mới
├── skills/               # (tuỳ chọn) skill ClawHub / bundle
└── README.md
```

## Plugin hiện tại: `cursor-agent`

Gọi Cursor Agent CLI từ chat OpenClaw (`/cursor`).

### Dev loop (local — 0 login)

```powershell
cd plugins\cursor-agent
npm ci                 # lần đầu
npm run build
npm test
openclaw gateway restart
```

Gateway load plugin từ:

`C:\Project\open_claw\plugins\cursor-agent`

(`plugins.load.paths` trong `~/.openclaw/openclaw.json`)

`npm run dev` nếu muốn watch rebuild.

### Project mapping

| Alias         | Path                      |
|---------------|---------------------------|
| `telegram-bot`| `C:\Project\telegram_bot` |
| `open-claw`   | `C:\Project\open_claw`    |

Ví dụ:

```text
/cursor open-claw --mode ask tóm tắt cấu trúc plugins/cursor-agent
```

## Tạo plugin mới

```powershell
Copy-Item -Recurse plugins\_template plugins\my-plugin
# Sửa openclaw.plugin.json + package.json + src/index.ts
cd plugins\my-plugin
npm install
npm run build
```

Thêm path vào `~/.openclaw/openclaw.json` → `plugins.load.paths` và `plugins.allow`, rồi restart Gateway.

Tài liệu: [Building plugins](https://docs.openclaw.ai/plugins/building-plugins) · [Plugin SDK](https://docs.openclaw.ai/plugins/sdk-overview)

## Trạng thái `cursor-agent`

- Version: **0.2.0** (`openclaw-cursor-agent`)
- Tests: 123 passed · typecheck OK · live smoke OK
- Đang dùng: **local load path** (không cần publish)
- Publish (tùy chọn): xem [`plugins/cursor-agent/PUBLISH.md`](plugins/cursor-agent/PUBLISH.md)

## Lộ trình gợi ý

1. ~~Hoàn thiện `cursor-agent`~~ — dùng local
2. Tiếp tục phát triển plugin / skill theo nhu cầu
3. Publish npm/ClawHub **chỉ khi** muốn chia sẻ công khai
4. Plugin mới từ `plugins/_template` khi cần

## Lưu ý

- Runtime OpenClaw vẫn là bản npm global (`openclaw@2026.6.11`).
- Agent workspace mặc định vẫn là `C:\Project\telegram_bot`.
- Không commit secrets / `.env`.
