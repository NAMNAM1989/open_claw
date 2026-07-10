import fs from "node:fs";

const path = `${process.env.USERPROFILE || process.env.HOME}/.openclaw/openclaw.json`;
if (!fs.existsSync(path)) {
  console.error("Khong tim thay", path);
  process.exit(1);
}

const BOT_ROOT = "C:\\Project\\open_claw\\apps\\telegram-bot";
const MONO_ROOT = "C:\\Project\\open_claw";
const OLD_BOT = "C:\\Project\\telegram_bot";

let raw = fs.readFileSync(path);
if (raw[0] === 0xef) raw = raw.subarray(3);
const j = JSON.parse(raw.toString("utf8"));

fs.copyFileSync(path, `${path}.bak-isolation-${Date.now()}`);

function fixWorkspace(ws) {
  if (typeof ws !== "string") return ws;
  if (ws.replace(/\//g, "\\") === OLD_BOT.replace(/\//g, "\\")) return BOT_ROOT;
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
j.plugins.load = { paths: [`${MONO_ROOT}\\plugins\\cursor-agent`] };
if (!j.plugins.entries) j.plugins.entries = {};
const existing = j.plugins.entries["cursor-agent"]?.config ?? {};
j.plugins.entries["cursor-agent"] = {
  enabled: true,
  config: {
    ...existing,
    projects: {
      "telegram-bot": BOT_ROOT,
      "open-claw": MONO_ROOT,
    },
  },
};

fs.writeFileSync(path, JSON.stringify(j, null, 2) + "\n", "utf8");
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
