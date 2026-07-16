import type { AuditEntry } from "./types.js";
import { PARSER_VERSION } from "./parser.js";

export function createAuditEntry(partial: Omit<AuditEntry, "parserVersion" | "at"> & { at?: string }): AuditEntry {
  return {
    ...partial,
    at: partial.at ?? new Date().toISOString(),
    parserVersion: PARSER_VERSION,
  };
}

/** Redact secrets if somehow present in query strings. */
export function sanitizeForLog(text: string): string {
  return text
    .replace(/(password|token|cookie|authorization)\s*[:=]\s*\S+/gi, "$1=[REDACTED]")
    .slice(0, 500);
}
