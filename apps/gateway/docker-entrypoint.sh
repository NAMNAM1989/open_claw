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
else
  echo "[entrypoint] ERROR: OPENCLAW_GATEWAY_TOKEN is required" >&2
  exit 1
fi

export GEMINI_API_KEY="${GEMINI_API_KEY:-}"
export GOOGLE_API_KEY="${GOOGLE_API_KEY:-$GEMINI_API_KEY}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"

if [ -n "${OPENAI_API_KEY:-}" ]; then
  echo "[entrypoint] OpenAI (ChatGPT) fallback enabled"
else
  echo "[entrypoint] WARN: OPENAI_API_KEY unset — Gemini failover to GPT skipped" >&2
fi

if [ -n "${DEEPSEEK_API_KEY:-}" ]; then
  echo "[entrypoint] DeepSeek fallback enabled"
else
  echo "[entrypoint] WARN: DEEPSEEK_API_KEY unset — last-resort DeepSeek failover unavailable" >&2
fi

mv /tmp/openclaw.runtime.json "$CONFIG"

mkdir -p /root/.openclaw/agents/default/sessions /root/.openclaw/extensions

# Volume at /root/.openclaw wipes extensions from image — install DeepSeek from vendor copy
if [ -d /app/vendor-plugins/deepseek-provider ]; then
  echo "[entrypoint] Ensuring DeepSeek provider plugin is installed"
  openclaw plugins install --link /app/vendor-plugins/deepseek-provider 2>&1 || \
    openclaw plugins install /app/vendor-plugins/deepseek-provider 2>&1 || \
    echo "[entrypoint] WARN: deepseek plugin install failed" >&2
  openclaw plugins enable deepseek 2>&1 || true
  openclaw plugins list 2>&1 | head -n 40 || true
fi

PORT="${PORT:-18789}"
echo "[entrypoint] Starting OpenClaw gateway on :${PORT}"
exec openclaw gateway run --bind lan --port "$PORT"
