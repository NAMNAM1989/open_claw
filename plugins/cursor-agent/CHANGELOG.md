# Changelog

## 0.2.0 — 2026-07-09

### Publish readiness
- Rename npm package to `openclaw-cursor-agent` (plugin id remains `cursor-agent`)
- Add ClawHub/npm metadata: `openclaw.compat`, `openclaw.build`, `openclaw.install`
- Add manifest `activation.onStartup` and `contracts.tools: ["cursor_agent"]`
- Ship `README.md`, `README_CN.md`, and `LICENSE` in the published tarball
- Add `typecheck`, `pack:check`, and `prepublishOnly` scripts
- Document npm / tarball / ClawHub install paths

### Verified
- Unit/integration: 123 passed
- Live Cursor Agent CLI smoke (`--mode ask`) on Windows
- OpenClaw Gateway loads plugin from linked workspace path

## 0.1.0

- Initial release: `/cursor` command, `cursor_agent` tool, project mapping, MCP approve, process registry
