import fs from "node:fs";

/**
 * Dong bo OpenClaw local PC ve Gemini (thong nhat voi apps/gateway).
 * Usage: node tools/set-local-gemini.mjs
 */
const path = `${process.env.USERPROFILE || process.env.HOME}/.openclaw/openclaw.json`;
if (!fs.existsSync(path)) {
  console.error("Khong tim thay", path);
  process.exit(1);
}

const BOT_ROOT = "C:\\Project\\open_claw\\apps\\telegram-bot";
const MONO_ROOT = "C:\\Project\\open_claw";
const MODEL = "google/gemini-2.5-flash";

let raw = fs.readFileSync(path);
if (raw[0] === 0xef) raw = raw.subarray(3);
const j = JSON.parse(raw.toString("utf8"));

fs.copyFileSync(path, `${path}.bak-gemini-${Date.now()}`);

function setModel(obj) {
  if (!obj) return;
  obj.model = { primary: MODEL };
}

if (!j.agents) j.agents = {};
if (!j.agents.defaults) j.agents.defaults = {};
setModel(j.agents.defaults);
j.agents.defaults.workspace = BOT_ROOT;

if (Array.isArray(j.agents.list)) {
  for (const agent of j.agents.list) {
    setModel(agent);
    agent.workspace = BOT_ROOT;
  }
}

if (!j.channels) j.channels = {};
if (!j.channels.telegram) j.channels.telegram = {};
j.channels.telegram.enabled = false;

if (!j.plugins) j.plugins = {};
if (!j.plugins.entries) j.plugins.entries = {};

j.plugins.entries.google = { ...(j.plugins.entries.google || {}), enabled: true };
j.plugins.entries.openai = { ...(j.plugins.entries.openai || {}), enabled: false };
j.plugins.entries.deepseek = { ...(j.plugins.entries.deepseek || {}), enabled: false };

if (Array.isArray(j.plugins.allow)) {
  j.plugins.allow = j.plugins.allow.filter((x) => x !== "deepseek");
  if (!j.plugins.allow.includes("google")) j.plugins.allow.push("google");
}

j.plugins.load = { paths: [`${MONO_ROOT}\\plugins\\cursor-agent`] };
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
      primary: j.agents.defaults.model,
      telegramEnabled: j.channels.telegram.enabled,
      google: j.plugins.entries.google?.enabled,
      openai: j.plugins.entries.openai?.enabled,
      deepseek: j.plugins.entries.deepseek?.enabled,
      note: "Can GEMINI_API_KEY / GOOGLE_API_KEY trong env OpenClaw local. Restart: openclaw gateway restart",
    },
    null,
    2,
  ),
);
