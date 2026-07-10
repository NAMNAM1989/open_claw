import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Dong bo OpenClaw local PC ve Gemini (thong nhat voi apps/gateway).
 * Usage: node tools/set-local-gemini.mjs
 */
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
const MODEL = "google/gemini-3.5-flash";

let raw = fs.readFileSync(configPath);
if (raw[0] === 0xef) raw = raw.subarray(3);
const j = JSON.parse(raw.toString("utf8"));

fs.copyFileSync(configPath, `${configPath}.bak-gemini-${Date.now()}`);

function setModel(obj) {
  if (!obj) return;
  obj.model = { primary: MODEL };
}

if (!j.agents) j.agents = {};
if (!j.agents.defaults) j.agents.defaults = {};
setModel(j.agents.defaults);
j.agents.defaults.workspace = workspace;

if (Array.isArray(j.agents.list)) {
  for (const agent of j.agents.list) {
    setModel(agent);
    agent.workspace = workspace;
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

j.plugins.load = { paths: [path.join(monoRoot, "plugins", "cursor-agent")] };
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
      primary: j.agents.defaults.model,
      workspace,
      telegramEnabled: j.channels.telegram.enabled,
      google: j.plugins.entries.google?.enabled,
      note: "Can GEMINI_API_KEY / GOOGLE_API_KEY trong env. Restart: openclaw gateway restart",
    },
    null,
    2,
  ),
);
