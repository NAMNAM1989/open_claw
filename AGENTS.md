# OpenClaw plugin-first workspace

## Auth
Local development needs **0 logins**. npm / ClawHub / GitHub are optional publish-only steps. See README.md and `plugins/cursor-agent/PUBLISH.md`.

## Layout
- `plugins/cursor-agent` — main plugin under development
- `plugins/_template` — copy to start a new plugin
- `skills/` — optional ClawHub / bundle skills
- `tools/` — local helpers; `finish-publish.ps1` / `login-all.ps1` are optional

## Dev loop (cursor-agent)
```powershell
cd plugins\cursor-agent
npm run build
npm test
openclaw gateway restart
```

Gateway load path: `C:\Project\open_claw\plugins\cursor-agent`
