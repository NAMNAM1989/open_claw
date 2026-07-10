FROM node:22-bookworm-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/* \
  && npm install -g openclaw@latest

WORKDIR /app

RUN mkdir -p /app/workspace /root/.openclaw

COPY workspace /app/workspace

COPY openclaw.template.json /app/openclaw.template.json
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

ENV NODE_ENV=production

EXPOSE 18789

ENTRYPOINT ["/app/docker-entrypoint.sh"]
