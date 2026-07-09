#!/usr/bin/env node
/**
 * Live smoke: invoke Cursor Agent CLI the same way the plugin runner does.
 * Usage: node scripts/smoke-live.mjs [workspace]
 */
import { spawn } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { resolve } from "node:path";

const workspace = resolve(process.argv[2] || process.cwd());
const home = process.env.USERPROFILE || process.env.HOME || homedir();

function detectAgentPath() {
  const candidates =
    process.platform === "win32"
      ? [
          resolve(home, "AppData/Local/cursor-agent/agent.cmd"),
          resolve(home, "AppData/Local/cursor-agent/agent.CMD"),
          resolve(home, ".cursor/bin/agent.cmd"),
        ]
      : [
          resolve(home, ".cursor/bin/agent"),
          resolve(home, ".local/bin/agent"),
        ];
  for (const p of candidates) {
    if (existsSync(p)) return p;
  }
  return null;
}

function resolveBinary(agentPath) {
  const versionsDir = resolve(agentPath, "..", "versions");
  if (!existsSync(versionsDir)) return null;
  const dirs = readdirSync(versionsDir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .sort()
    .reverse();
  for (const dir of dirs) {
    const nodeBin = resolve(
      versionsDir,
      dir,
      process.platform === "win32" ? "node.exe" : "node",
    );
    const entryScript = resolve(versionsDir, dir, "index.js");
    if (existsSync(nodeBin) && existsSync(entryScript)) {
      return { nodeBin, entryScript };
    }
  }
  return null;
}

const agentPath = detectAgentPath();
if (!agentPath) {
  console.error("Cursor Agent CLI not found");
  process.exit(1);
}

const resolved = resolveBinary(agentPath);
const prompt = "Reply with exactly: SMOKE_OK and nothing else.";

let cmd;
const args = [];
if (resolved) {
  cmd = resolved.nodeBin;
  args.push(
    resolved.entryScript,
    "-p",
    "--trust",
    "--output-format",
    "text",
    "--mode",
    "ask",
    "--workspace",
    workspace,
    prompt,
  );
} else {
  cmd = agentPath;
  args.push(
    "-p",
    "--trust",
    "--output-format",
    "text",
    "--mode",
    "ask",
    "--workspace",
    workspace,
    prompt,
  );
}

console.log(`[smoke] cmd=${cmd}`);
console.log(`[smoke] workspace=${workspace}`);

const child = spawn(cmd, args, {
  cwd: workspace,
  stdio: ["ignore", "pipe", "pipe"],
  windowsHide: true,
  shell: !resolved && process.platform === "win32" && /\.(cmd|bat)$/i.test(cmd),
});

let out = "";
child.stdout.on("data", (c) => {
  out += c.toString();
  process.stdout.write(c);
});
child.stderr.on("data", (c) => process.stderr.write(c));

child.on("close", (code) => {
  const ok = out.includes("SMOKE_OK") && code === 0;
  console.log(ok ? "\n[smoke] PASS" : `\n[smoke] FAIL exit=${code}`);
  process.exit(ok ? 0 : 1);
});
