import fs from "node:fs";

const path = "C:/Users/namna/.openclaw/openclaw.json";
let raw = fs.readFileSync(path);
if (raw[0] === 0xef) raw = raw.subarray(3);
const j = JSON.parse(raw.toString("utf8"));

fs.copyFileSync(path, `${path}.bak-restore-cursor-${Date.now()}`);

if (!j.plugins) j.plugins = {};
if (!Array.isArray(j.plugins.allow)) j.plugins.allow = [];
if (!j.plugins.allow.includes("cursor-agent")) {
  j.plugins.allow.unshift("cursor-agent");
}
j.plugins.load = { paths: ["C:\\Project\\open_claw\\plugins\\cursor-agent"] };
if (!j.plugins.entries) j.plugins.entries = {};
j.plugins.entries["cursor-agent"] = {
  enabled: true,
  config: {
    projects: {
      "telegram-bot": "C:\\Project\\telegram_bot",
      "open-claw": "C:\\Project\\open_claw",
    },
    agentPath: "C:\\Users\\namna\\AppData\\Local\\cursor-agent\\agent.CMD",
    defaultTimeoutSec: 600,
    noOutputTimeoutSec: 180,
    enableMcp: true,
    maxConcurrent: 2,
    enableAgentTool: true,
  },
};

fs.writeFileSync(path, JSON.stringify(j, null, 2) + "\n", "utf8");
console.log(
  JSON.stringify(
    {
      allowHead: j.plugins.allow.slice(0, 3),
      load: j.plugins.load,
      projects: j.plugins.entries["cursor-agent"].config.projects,
    },
    null,
    2,
  ),
);
