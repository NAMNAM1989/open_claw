import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const configPath = path.join(
  process.env.USERPROFILE || process.env.HOME || "",
  ".openclaw",
  "openclaw.json",
);
if (!fs.existsSync(configPath)) {
  console.error("Khong tim thay", configPath);
  process.exit(1);
}

const monoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const workspace = path.join(monoRoot, "apps", "gateway", "workspace");

let raw = fs.readFileSync(configPath);
if (raw[0] === 0xef) raw = raw.subarray(3);
const j = JSON.parse(raw.toString("utf8"));

fs.copyFileSync(configPath, `${configPath}.bak-isolation-${Date.now()}`);

function fixWorkspace(ws) {
  if (typeof ws !== "string") return ws;
  const norm = ws.replace(/\//g, "\\").toLowerCase();
  const openClaw = monoRoot.replace(/\//g, "\\").toLowerCase();
  if (!norm.includes(openClaw) && norm.includes("telegram")) {
    return workspace;
  }
  return ws;
}

if (j.agents?.defaults?.workspace) {
  j.agents.defaults.workspace = fixWorkspace(j.agents.defaults.workspace);
}
if (Array.isArray(j.agents?.list)) {
  for (const agent of j.agents.list) {
    if (agent.workspace) agent.workspace = fixWorkspace(agent.workspace);
  }
}

if (j.channels?.telegram) {
  j.channels.telegram.enabled = false;
}

if (!j.plugins) j.plugins = {};
j.plugins.load = { paths: [path.join(monoRoot, "plugins", "cursor-agent")] };
if (!j.plugins.entries) j.plugins.entries = {};
const existing = j.plugins.entries["cursor-agent"]?.config ?? {};
j.plugins.entries["cursor-agent"] = {
  enabled: true,
  config: {
    ...existing,
    projects: {
      "open-claw": monoRoot,
    },
  },
};

fs.writeFileSync(configPath, JSON.stringify(j, null, 2) + "\n", "utf8");
console.log(
  JSON.stringify(
    {
      telegramChannel: j.channels?.telegram?.enabled,
      defaultWorkspace: j.agents?.defaults?.workspace,
      cursorProjects: j.plugins.entries["cursor-agent"].config.projects,
    },
    null,
    2,
  ),
);
