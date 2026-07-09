import fs from "node:fs";

const path = process.argv[2];
if (!path) {
  console.error("Usage: node patch-openclaw-load.mjs <openclaw.json>");
  process.exit(1);
}

let raw = fs.readFileSync(path);
if (raw[0] === 0xef && raw[1] === 0xbb && raw[2] === 0xbf) {
  raw = raw.subarray(3);
}

const j = JSON.parse(raw.toString("utf8"));
j.plugins.load.paths = ["C:\\Project\\open_claw\\plugins\\cursor-agent"];
j.plugins.entries["cursor-agent"].config.projects = {
  "telegram-bot": "C:\\Project\\telegram_bot",
  "open-claw": "C:\\Project\\open_claw",
};
fs.writeFileSync(path, JSON.stringify(j, null, 2) + "\n", "utf8");
console.log(
  JSON.stringify(
    {
      paths: j.plugins.load.paths,
      projects: j.plugins.entries["cursor-agent"].config.projects,
    },
    null,
    2,
  ),
);
