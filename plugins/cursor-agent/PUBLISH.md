# Publish `openclaw-cursor-agent` (tùy chọn)

Plugin id: `cursor-agent`  
npm / ClawHub package: `openclaw-cursor-agent`  
Current version: see `package.json`

## Bạn có cần bước này không?

**Không**, nếu chỉ phát triển và dùng trên máy này.

Gateway đã load từ thư mục workspace (`plugins.load.paths`). Dev loop:

```powershell
npm run build
openclaw gateway restart
```

Chỉ publish khi muốn **người khác** cài mà không copy source.

## Cần đăng nhập gì khi publish?

| Mục tiêu | Login cần thiết |
|----------|-----------------|
| Publish npm (tối thiểu) | Chỉ `npm login` |
| Thêm ClawHub | `clawhub login` + repo GitHub (source attribution) |
| Remote / CI release | `gh auth login` |

Khuyến nghị: publish **npm trước** (1 tài khoản). ClawHub/GitHub để sau.

Không cần chạy `tools/login-all.ps1` (login cả 3) trừ khi bạn muốn đủ cả npm + ClawHub + GitHub cùng lúc.

## One-shot (sau khi đã login đủ)

```powershell
cd C:\Project\open_claw\plugins\cursor-agent

# Tối thiểu: npm
npm login
.\scripts\publish.ps1 -SkipClawhub

# Đủ npm + ClawHub (cần git remote GitHub):
# clawhub login
# gh auth login   # rồi push repo
# .\scripts\publish.ps1

# Dry-run:
.\scripts\publish.ps1 -DryRun
```

Hoặc từ root (login + push + publish đầy đủ — chỉ khi chủ động muốn):

```powershell
powershell -ExecutionPolicy Bypass -File C:\Project\open_claw\tools\finish-publish.ps1
```

## Thủ công

```powershell
npm run typecheck
npm test
npm run build
npm pack

npm publish --access public

# ClawHub (cần --source-repo / --source-commit từ GitHub):
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
- Publish cần browser/token; máy chưa login thì bỏ qua — dùng local là đủ.
