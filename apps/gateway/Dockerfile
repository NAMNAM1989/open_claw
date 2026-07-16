FROM node:22-bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/* \
  && npm install -g openclaw@latest

# DeepSeek plugin baked into image — volume mount /root/.openclaw wipes build-time installs
RUN mkdir -p /app/vendor-plugins \
  && cd /tmp \
  && npm pack @openclaw/deepseek-provider \
  && tar -xzf openclaw-deepseek-provider-*.tgz \
  && mv package /app/vendor-plugins/deepseek-provider \
  && rm -rf /tmp/openclaw-deepseek-provider-*.tgz \
  && node -e "const fs=require('fs'); const p='/app/vendor-plugins/deepseek-provider/package.json'; const j=JSON.parse(fs.readFileSync(p,'utf8')); j.openclaw=j.openclaw||{}; j.openclaw.extensions=['./dist/index.js']; fs.writeFileSync(p, JSON.stringify(j,null,2));"

WORKDIR /app

RUN mkdir -p /app/workspace /root/.openclaw

# Local PoC plugin (link-only legal research) — baked like deepseek, survives volume wipe
# index.js at package root (avoid dist/ being dropped by upload ignore rules)
COPY vendor-plugins/vietnam-legal-research /app/vendor-plugins/vietnam-legal-research
RUN test -f /app/vendor-plugins/vietnam-legal-research/index.js \
  && test -f /app/vendor-plugins/vietnam-legal-research/openclaw.plugin.json

COPY workspace /app/workspace

COPY openclaw.template.json /app/openclaw.template.json
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

ENV NODE_ENV=production

EXPOSE 18789

ENTRYPOINT ["/app/docker-entrypoint.sh"]
