import { randomUUID } from "node:crypto";
import { enforceAnswerGuardrail } from "./answer-guardrail.js";
import { createAuditEntry, sanitizeForLog } from "./audit-log.js";
import { TtlCache } from "./cache.js";
import { buildMarkdown } from "./citation-builder.js";
import { loadConfig, type TvplConfig } from "./config.js";
import { LegalIntegrationError } from "./errors.js";
import { classifyQuery } from "./query-classifier.js";
import { RateLimiter } from "./rate-limiter.js";
import {
  buildOfficialSearchUrls,
  buildPublicSearchQuery,
  buildTvplSearchUrl,
} from "./search-adapter.js";
import { refuseBulk } from "./source-policy.js";
import type { ResearchResult } from "./types.js";

export class VietnamLegalClient {
  private readonly config: TvplConfig;
  private readonly limiter: RateLimiter;
  private readonly cache: TtlCache<ResearchResult>;

  constructor(config?: Partial<TvplConfig>) {
    this.config = loadConfig(config);
    this.limiter = new RateLimiter(this.config.requestsPerMinute);
    this.cache = new TtlCache<ResearchResult>(this.config.cacheTtlSeconds);
  }

  research(rawQuery: string): ResearchResult {
    const requestId = randomUUID();
    const cacheKey = `${this.config.mode}:${rawQuery.trim().toLowerCase()}`;
    const cached = this.cache.get(cacheKey);
    if (cached) {
      return {
        ...cached,
        requestId,
        audit: createAuditEntry({
          requestId,
          query: sanitizeForLog(rawQuery),
          adapter: "cache",
          urls: cached.searchUrls.map((u) => u.url),
          success: true,
        }),
      };
    }

    try {
      refuseBulk(rawQuery);
      this.limiter.tryAcquire();
    } catch (err) {
      const stopReason =
        err instanceof LegalIntegrationError ? err.code : "UNVERIFIED";
      return this.stopped(rawQuery, requestId, stopReason, String(err));
    }

    const query = classifyQuery(rawQuery);
    const searchUrls: Array<{ label: string; url: string }> = [];

    if (this.config.mode !== "official") {
      searchUrls.push({
        label: "Thư Viện Pháp Luật (tra cứu)",
        url: buildTvplSearchUrl(query),
      });
    }

    searchUrls.push(...buildOfficialSearchUrls(query));

    if (this.config.mode === "public-search") {
      searchUrls.push({
        label: "Public search query (copy vào công cụ tìm kiếm)",
        url: `https://www.google.com/search?q=${encodeURIComponent(buildPublicSearchQuery(query))}`,
      });
    }

    const retrievedAt = new Date().toISOString();
    const markdownRaw = buildMarkdown({
      query,
      documents: [],
      searchUrls,
      checkedAt: retrievedAt,
      analysisNotes:
        "Chế độ PoC link-only/official: OpenClaw cung cấp đường dẫn nguồn để bạn tự xác minh. Không scrape nội dung TVPL.",
    });
    const { markdown } = enforceAnswerGuardrail(markdownRaw);

    const result: ResearchResult = {
      mode: this.config.mode,
      query,
      documents: [],
      searchUrls,
      requestId,
      retrievedAt,
      markdown,
      audit: createAuditEntry({
        requestId,
        query: sanitizeForLog(rawQuery),
        adapter: this.config.mode,
        urls: searchUrls.map((u) => u.url),
        success: true,
      }),
    };

    this.cache.set(cacheKey, result);
    return result;
  }

  private stopped(
    rawQuery: string,
    requestId: string,
    stopReason: string,
    detail: string,
  ): ResearchResult {
    const query = classifyQuery(rawQuery);
    const searchUrls = [
      {
        label: "Thư Viện Pháp Luật (tra cứu thủ công)",
        url: buildTvplSearchUrl(query),
      },
      ...buildOfficialSearchUrls(query),
    ];
    const retrievedAt = new Date().toISOString();
    const { markdown } = enforceAnswerGuardrail(
      buildMarkdown({
        query,
        documents: [],
        searchUrls,
        checkedAt: retrievedAt,
        stopReason: `${stopReason}: ${detail}`,
      }),
    );
    return {
      mode: this.config.mode,
      query,
      documents: [],
      searchUrls,
      stopReason,
      requestId,
      retrievedAt,
      markdown,
      audit: createAuditEntry({
        requestId,
        query: sanitizeForLog(rawQuery),
        adapter: this.config.mode,
        urls: searchUrls.map((u) => u.url),
        success: false,
        stopReason,
      }),
    };
  }
}
