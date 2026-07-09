# Publish `openclaw-cursor-agent`

Plugin id: `cursor-agent`  
npm / ClawHub package: `openclaw-cursor-agent`  
Current version: see `package.json`

## One-shot (sau khi đã login)

```powershell
cd C:\Project\open_claw\plugins\cursor-agent

# 1) Đăng nhập (chỉ cần làm một lần trên máy)
npm login
clawhub login

# 2) Publish
.\scripts\publish.ps1

# Dry-run trước:
.\scripts\publish.ps1 -DryRun
```

## Thủ công

```powershell
npm run typecheck
npm test
npm run build
npm pack

npm publish --access public

clawhub package publish .\openclaw-cursor-agent-0.2.0.tgz --family code-plugin --dry-run
clawhub package publish .\openclaw-cursor-agent-0.2.0.tgz --family code-plugin
```

## Cài sau khi publish

```powershell
openclaw plugins install npm:openclaw-cursor-agent
# hoặc
openclaw plugins install clawhub:openclaw-cursor-agent

openclaw plugins enable cursor-agent
openclaw gateway restart
```

## Lưu ý

- Tên npm `cursor-agent` đã bị chiếm → dùng `openclaw-cursor-agent`.
- Manifest id vẫn là `cursor-agent` (config key không đổi).
- Publish cần tương tác browser/token; không thể hoàn tất nếu máy chưa `npm login` / `clawhub login`.
