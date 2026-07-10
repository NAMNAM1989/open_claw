import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const home = process.env.USERPROFILE || process.env.HOME || os.homedir();
const configPath = path.join(home, ".openclaw", "openclaw.json");
const monoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

let raw = fs.readFileSync(configPath);
if (raw[0] === 0xef) raw = raw.subarray(3);
const j = JSON.parse(raw.toString("utf8"));

fs.copyFileSync(configPath, `${configPath}.bak-restore-cursor-${Date.now()}`);

if (!j.plugins) j.plugins = {};
if (!Array.isArray(j.plugins.allow)) j.plugins.allow = [];
if (!j.plugins.allow.includes("cursor-agent")) {
  j.plugins.allow.unshift("cursor-agent");
}
j.plugins.load = { paths: [path.join(monoRoot, "plugins", "cursor-agent")] };
if (!j.plugins.entries) j.plugins.entries = {};
const agentCmd = process.platform === "win32"
  ? path.join(home, "AppData", "Local", "cursor-agent", "agent.CMD")
  : path.join(home, ".local", "bin", "cursor-agent");
j.plugins.entries["cursor-agent"] = {
  enabled: true,
  config: {
    projects: {
      "open-claw": monoRoot,
    },
    agentPath: agentCmd,
    defaultTimeoutSec: 600,
    noOutputTimeoutSec: 180,
    enableMcp: true,
    maxConcurrent: 2,
    enableAgentTool: true,
  },
};

fs.writeFileSync(configPath, JSON.stringify(j, null, 2) + "\n", "utf8");
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
