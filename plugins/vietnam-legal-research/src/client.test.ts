import { describe, expect, it } from "vitest";
import { enforceAnswerGuardrail } from "./answer-guardrail.js";
import { VietnamLegalClient } from "./client.js";
import { RateLimiter } from "./rate-limiter.js";
import { TtlCache } from "./cache.js";
import { assertFetchAllowed, refuseBulk } from "./source-policy.js";
import { LegalIntegrationError } from "./errors.js";
import { classifyQuery } from "./query-classifier.js";

describe("VietnamLegalClient link-only", () => {
  it("MVP-1: returns TVPL + official URLs for document number", () => {
    const client = new VietnamLegalClient({
      mode: "link-only",
      cacheTtlSeconds: 0,
      requestsPerMinute: 30,
    });
    const result = client.research(
      "Tìm Nghị định 123/2020/NĐ-CP và cho biết tình trạng hiệu lực.",
    );
    expect(result.query.documentNumber).toBe("123/2020/NĐ-CP");
    expect(result.searchUrls.some((u) => u.url.includes("thuvienphapluat.vn"))).toBe(
      true,
    );
    expect(result.searchUrls.some((u) => u.url.includes("vbpl.vn"))).toBe(true);
    expect(result.markdown).toMatch(/không thay thế/i);
    expect(result.documents).toHaveLength(0);
  });

  it("MVP-2: topic query gets domain links", () => {
    const client = new VietnamLegalClient({
      mode: "link-only",
      cacheTtlSeconds: 0,
      requestsPerMinute: 30,
    });
    const result = client.research(
      "quy định hiện hành về hóa đơn đối với khoản chi hộ logistics",
    );
    expect(result.query.domain).toMatch(/thue|logistics/);
    expect(result.markdown).toMatch(/https:\/\//);
  });

  it("refuses bulk copy", () => {
    const client = new VietnamLegalClient({
      mode: "link-only",
      cacheTtlSeconds: 0,
      requestsPerMinute: 30,
    });
    const result = client.research("sao chép hàng loạt toàn bộ cơ sở dữ liệu");
    expect(result.stopReason).toBe("BULK_REQUEST_REFUSED");
  });
});

describe("source-policy", () => {
  it("blocks TVPL fetch in link-only", () => {
    expect(() =>
      assertFetchAllowed({
        mode: "link-only",
        allowBrowser: false,
        targetHost: "thuvienphapluat.vn",
      }),
    ).toThrow(LegalIntegrationError);
  });

  it("refuseBulk throws", () => {
    expect(() => refuseBulk("crawl dump mirror")).toThrow(/Bulk/);
  });
});

describe("rate limiter + cache", () => {
  it("rate limits", () => {
    const rl = new RateLimiter(2);
    rl.tryAcquire(1_000);
    rl.tryAcquire(1_001);
    expect(() => rl.tryAcquire(1_002)).toThrow(/Exceeded/);
  });

  it("cache ttl", () => {
    const cache = new TtlCache<string>(1);
    cache.set("a", "v", 0);
    expect(cache.get("a", 500)).toBe("v");
    expect(cache.get("a", 1_100)).toBeUndefined();
  });
});

describe("guardrail + classifier", () => {
  it("adds disclaimer when missing", () => {
    const { violations, markdown } = enforceAnswerGuardrail("hello https://a.vn");
    expect(violations).toContain("missing_disclaimer");
    expect(markdown).toMatch(/tư vấn pháp lý/i);
  });

  it("classifies hải quan", () => {
    expect(classifyQuery("thủ tục hải quan xuất nhập khẩu").domain).toBe(
      "hai-quan",
    );
  });
});

describe("live tests gate", () => {
  it("keeps RUN_TVPL_LIVE_TESTS off by default", () => {
    expect(process.env.RUN_TVPL_LIVE_TESTS ?? "false").not.toBe("true");
  });
});
