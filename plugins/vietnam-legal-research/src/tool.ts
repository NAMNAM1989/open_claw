import { VietnamLegalClient } from "./client.js";
import type { IntegrationMode } from "./types.js";

interface ToolContext {
  config?: Record<string, unknown>;
}

export function createVietnamLegalTool(client?: VietnamLegalClient) {
  return (_ctx: ToolContext) => {
    const cfg = _ctx.config ?? {};
    const mode = (cfg.integrationMode as IntegrationMode | undefined) ?? undefined;
    const active =
      client ??
      new VietnamLegalClient({
        mode,
        requestsPerMinute:
          typeof cfg.requestsPerMinute === "number"
            ? cfg.requestsPerMinute
            : undefined,
        cacheTtlSeconds:
          typeof cfg.cacheTtlSeconds === "number"
            ? cfg.cacheTtlSeconds
            : undefined,
      });

    return {
      name: "vietnam_legal_research",
      label: "Vietnam Legal Research",
      description:
        "Research Vietnamese legal documents for logistics, customs, tax, labor, and business questions. " +
        "Returns search URLs (Thư Viện Pháp Luật + official government), structured citation template, and disclaimers. " +
        "Does NOT scrape thuvienphapluat.vn by default. Never invent document numbers or URLs.",
      parameters: {
        type: "object" as const,
        properties: {
          query: {
            type: "string",
            description:
              "User legal question or document number, e.g. 'Nghị định 123/2020/NĐ-CP hiệu lực?'",
          },
        },
        required: ["query"],
      },
      async execute(_toolCallId: string, params: { query: string }) {
        const result = active.research(params.query);
        return {
          content: [{ type: "text", text: result.markdown }],
          details: {
            mode: result.mode,
            requestId: result.requestId,
            searchUrls: result.searchUrls,
            stopReason: result.stopReason,
            audit: result.audit,
          },
        };
      },
    };
  };
}
