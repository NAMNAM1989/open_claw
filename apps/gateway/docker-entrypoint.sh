#!/bin/sh
# Inject Railway env into OpenClaw config before starting gateway.
set -e

CONFIG="/root/.openclaw/openclaw.json"
TEMPLATE="/app/openclaw.template.json"

if [ ! -f "$TEMPLATE" ]; then
  TEMPLATE="$CONFIG"
fi

cp "$TEMPLATE" /tmp/openclaw.runtime.json

if [ -n "${OPENCLAW_GATEWAY_TOKEN:-}" ]; then
  sed -i "s|REPLACE_GATEWAY_TOKEN|${OPENCLAW_GATEWAY_TOKEN}|g" /tmp/openclaw.runtime.json
fi

export GEMINI_API_KEY="${GEMINI_API_KEY:-}"
export GOOGLE_API_KEY="${GOOGLE_API_KEY:-$GEMINI_API_KEY}"

mv /tmp/openclaw.runtime.json "$CONFIG"

mkdir -p /root/.openclaw/agents/default/sessions

PORT="${PORT:-18789}"
echo "[entrypoint] Starting OpenClaw gateway on :${PORT}"
exec openclaw gateway run --bind lan --port "$PORT"
