# Plugin template

1. Copy folder: `plugins/_template` → `plugins/<id>`
2. Đổi `id` / `name` trong `openclaw.plugin.json` và `package.json`
3. `npm install && npm run build`
4. Thêm path vào `~/.openclaw/openclaw.json` (`plugins.load.paths` + `plugins.allow`)
5. `openclaw gateway restart`
6. `openclaw plugins inspect <id> --runtime --json`

Xem thêm: https://docs.openclaw.ai/plugins/building-plugins
