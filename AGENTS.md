# OpenClaw plugin-first workspace

## Layout
- `plugins/cursor-agent` — main plugin under development
- `plugins/_template` — copy to start a new plugin
- `skills/` — optional ClawHub / bundle skills
- `tools/` — local helper scripts

## Dev loop (cursor-agent)
```powershell
cd plugins\cursor-agent
npm run build
npm test
openclaw gateway restart
```

Gateway load path: `C:\Project\open_claw\plugins\cursor-agent`
