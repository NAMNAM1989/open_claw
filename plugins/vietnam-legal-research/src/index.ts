import { createVietnamLegalTool } from "./tool.js";

const PLUGIN_ID = "vietnam-legal-research";

export default {
  id: PLUGIN_ID,
  configSchema: {
    type: "object" as const,
    additionalProperties: false,
    properties: {
      integrationMode: {
        type: "string",
        enum: ["link-only", "official", "public-search", "browser"],
      },
      requestsPerMinute: { type: "number" },
      cacheTtlSeconds: { type: "number" },
    },
  },

  register(api: {
    logger?: { info: (...args: unknown[]) => void };
    pluginConfig?: Record<string, unknown>;
    registerTool: (
      factory: ReturnType<typeof createVietnamLegalTool>,
      opts?: { name?: string; optional?: boolean },
    ) => void;
  }) {
    const log = api.logger?.info?.bind(api.logger) ?? console.log;
    log(`[${PLUGIN_ID}] registered (default mode: link-only; TVPL scrape disabled)`);

    api.registerTool(createVietnamLegalTool(), {
      name: "vietnam_legal_research",
      optional: false,
    });
  },
};

export { VietnamLegalClient } from "./client.js";
export { createVietnamLegalTool } from "./tool.js";
export { parseDocumentHtml, detectStopSignals } from "./parser.js";
export { classifyQuery } from "./query-classifier.js";
export {
  normalizeDocumentNumber,
  normalizeIsoDate,
  normalizeStatus,
} from "./normalizer.js";
export { enforceAnswerGuardrail } from "./answer-guardrail.js";
export { assertFetchAllowed, refuseBulk } from "./source-policy.js";
export { RateLimiter } from "./rate-limiter.js";
export { TtlCache } from "./cache.js";
export { stripPromptInjection } from "./prompt-injection.js";
