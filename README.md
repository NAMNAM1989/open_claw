# OpenClaw — Plugin-first workspace

Workspace phát triển **plugin / skill** cho [OpenClaw](https://github.com/openclaw/openclaw), không fork core.

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

```powershell
cd plugins\cursor-agent
npm ci
npm run build
npm test
npm run dev          # watch rebuild
```

Gateway đang load plugin từ:

`C:\Project\open_claw\plugins\cursor-agent`

(đã cập nhật `plugins.load.paths` trong `~/.openclaw/openclaw.json`)

Sau khi sửa code: `npm run build` rồi `openclaw gateway restart`.

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
- Tarball: `plugins/cursor-agent/openclaw-cursor-agent-0.2.0.tgz`
- Publish: `npm login` rồi `npm publish --access public` (hoặc ClawHub)

## Lộ trình gợi ý

1. ~~Hoàn thiện `cursor-agent`~~ → sẵn sàng publish
2. `npm publish` / ClawHub (cần đăng nhập npm)
3. Skill cho workflow `telegram_bot` (nếu cần)
4. Plugin mới khi có nhu cầu runtime (tool/channel/provider)

## Lưu ý

- Runtime OpenClaw vẫn là bản npm global (`openclaw@2026.6.11`).
- Agent workspace mặc định vẫn là `C:\Project\telegram_bot`.
- Không commit secrets / `.env`.
