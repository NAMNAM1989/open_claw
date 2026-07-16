// src/client.ts
import { randomUUID } from "node:crypto";

// src/citation-builder.ts
var LEGAL_DISCLAIMER = "\u0110\xE2y l\xE0 n\u1ED9i dung h\u1ED7 tr\u1EE3 tra c\u1EE9u, kh\xF4ng thay th\u1EBF \xFD ki\u1EBFn t\u01B0 v\u1EA5n ph\xE1p l\xFD chuy\xEAn m\xF4n. C\u1EA7n ki\u1EC3m tra v\u0103n b\u1EA3n g\u1ED1c v\xE0 t\xECnh tr\u1EA1ng hi\u1EC7u l\u1EF1c t\u1EA1i th\u1EDDi \u0111i\u1EC3m \xE1p d\u1EE5ng.";
function buildMarkdown(params) {
  const doc = params.documents[0];
  const lines = ["## K\u1EBFt qu\u1EA3 tra c\u1EE9u", ""];
  if (params.stopReason) {
    lines.push(`**Tr\u1EA1ng th\xE1i:** d\u1EEBng \u2014 ${params.stopReason}`, "");
  }
  lines.push(
    `**V\u0103n b\u1EA3n:** ${doc?.title ?? "(ch\u01B0a x\xE1c minh \u2014 m\u1EDF ngu\u1ED3n b\xEAn d\u01B0\u1EDBi)"}`,
    `**S\u1ED1 hi\u1EC7u:** ${doc?.documentNumber ?? params.query.documentNumber ?? "(ch\u01B0a x\xE1c minh)"}`,
    `**C\u01A1 quan ban h\xE0nh:** ${doc?.issuingAuthority ?? "(ch\u01B0a x\xE1c minh)"}`,
    `**Ng\xE0y ban h\xE0nh:** ${doc?.issuedDate ?? "(ch\u01B0a x\xE1c minh)"}`,
    `**Ng\xE0y hi\u1EC7u l\u1EF1c:** ${doc?.effectiveDate ?? "(ch\u01B0a x\xE1c minh)"}`,
    `**T\xECnh tr\u1EA1ng hi\u1EC7u l\u1EF1c:** ${doc?.status ?? "unknown"}`,
    `**Ki\u1EC3m tra l\xFAc:** ${params.checkedAt}`,
    "",
    "### N\u1ED9i dung li\xEAn quan",
    ""
  );
  if (doc?.relevantExcerpts?.length) {
    for (const ex of doc.relevantExcerpts) {
      lines.push(`> ${ex.text}`, "");
    }
    lines.push("_\u0110o\u1EA1n tr\xEAn l\xE0 tr\xEDch/metadata t\u1EEB ngu\u1ED3n ho\u1EB7c fixture; kh\xF4ng ph\u1EA3i to\xE0n v\u0103n._", "");
  } else {
    lines.push(
      "PoC ch\u1EBF \u0111\u1ED9 link-only: ch\u01B0a t\u1EA3i n\u1ED9i dung t\u1EEB website. H\xE3y m\u1EDF URL ngu\u1ED3n \u0111\u1EC3 \u0111\u1ECDc v\u0103n b\u1EA3n g\u1ED1c.",
      ""
    );
  }
  lines.push("### Ph\xE2n t\xEDch", "");
  lines.push(
    params.analysisNotes ?? "Ph\u1EA7n ph\xE2n t\xEDch c\u1EE7a AI (n\u1EBFu c\xF3) ph\u1EA3i t\xE1ch bi\u1EC7t kh\u1ECFi metadata ngu\u1ED3n v\xE0 kh\xF4ng \u0111\u01B0\u1EE3c kh\u1EB3ng \u0111\u1ECBnh tuy\u1EC7t \u0111\u1ED1i.",
    ""
  );
  lines.push("### V\u0103n b\u1EA3n li\xEAn quan", "");
  const related = [
    ...doc?.amendedBy ?? [],
    ...doc?.replacedBy ?? [],
    ...doc?.relatedDocuments ?? []
  ];
  if (related.length === 0) {
    lines.push("- (ch\u01B0a x\xE1c minh t\u1EEB ngu\u1ED3n)", "");
  } else {
    for (const r of related) {
      lines.push(`- [${r.relation}] ${r.documentNumber ?? ""} ${r.title}`.trim());
    }
    lines.push("");
  }
  lines.push("### Ngu\u1ED3n", "");
  let i = 1;
  for (const u of params.searchUrls) {
    lines.push(`${i}. [${u.label}](${u.url})`);
    i += 1;
  }
  if (doc?.sourceUrl && !params.searchUrls.some((u) => u.url === doc.sourceUrl)) {
    lines.push(`${i}. [Ngu\u1ED3n t\xE0i li\u1EC7u](${doc.sourceUrl})`);
  }
  lines.push("", `> L\u01B0u \xFD: ${LEGAL_DISCLAIMER}`);
  return lines.join("\n");
}

// src/answer-guardrail.ts
function enforceAnswerGuardrail(markdown) {
  const violations = [];
  let out = markdown;
  if (!/https?:\/\//i.test(out)) {
    violations.push("missing_source_url");
    out += "\n\n> Thi\u1EBFu URL ngu\u1ED3n \u2014 kh\xF4ng \u0111\u01B0\u1EE3c k\u1EBFt lu\u1EADn ph\xE1p l\xFD.";
  }
  if (!out.includes("kh\xF4ng thay th\u1EBF") && !out.includes(LEGAL_DISCLAIMER.slice(0, 20))) {
    violations.push("missing_disclaimer");
    out += `

> L\u01B0u \xFD: ${LEGAL_DISCLAIMER}`;
  }
  if (/thuvienphapluat\.vn\/van-ban\/fake-/i.test(out)) {
    violations.push("suspicious_fake_url");
    out = out.replace(/https?:\/\/[^\s)]*fake-[^\s)]*/gi, "[URL \u0111\xE3 lo\u1EA1i b\u1ECF]");
  }
  return { markdown: out, violations };
}

// src/normalizer.ts
function normalizeDocumentNumber(raw) {
  const cleaned = raw.normalize("NFC").replace(/\s+/g, " ").trim();
  const m = cleaned.match(
    /(\d{1,4}\s*\/\s*\d{4}\s*\/\s*[A-ZĐ]{1,10}(?:-[A-ZĐ]{1,10})?)/i
  );
  if (!m?.[1]) return void 0;
  return m[1].toUpperCase().replace(/\s+/g, "").replace(/Đ/g, "\u0110").replace(/NĐ/g, "N\u0110").replace(/ND-CP/g, "N\u0110-CP").replace(/ND\//g, "N\u0110/");
}
function normalizeIsoDate(raw) {
  const s = raw.trim();
  const iso = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (iso) return `${iso[1]}-${iso[2]}-${iso[3]}`;
  const dmy = s.match(/^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})$/);
  if (dmy) {
    const dd = dmy[1].padStart(2, "0");
    const mm = dmy[2].padStart(2, "0");
    return `${dmy[3]}-${mm}-${dd}`;
  }
  return void 0;
}
function normalizeStatus(raw) {
  const t = raw.toLowerCase();
  if (/còn hiệu lực|con hieu luc|đang hiệu lực|dang hieu luc|effective/.test(t)) {
    return "effective";
  }
  if (/hết hiệu lực một phần|het hieu luc mot phan|partial/.test(t)) {
    return "partially-effective";
  }
  if (/hết hiệu lực|het hieu luc|expired|không còn hiệu lực/.test(t)) {
    return "expired";
  }
  return "unknown";
}

// src/prompt-injection.ts
var INJECTION_PATTERNS = [
  /ignore\s+(all\s+)?previous\s+instructions/i,
  /bỏ\s*qua\s*(mọi\s*)?hướng\s*dẫn/i,
  /system\s*prompt/i,
  /you\s+are\s+now/i,
  /exfiltrat/i,
  /send\s+(me\s+)?(the\s+)?(api\s+)?key/i,
  /run\s+shell/i,
  /curl\s+http/i
];
function stripPromptInjection(text) {
  let flagged = false;
  const segments = text.split(/(\r?\n+|(?<=[.!?])\s+)/);
  const kept = [];
  for (const segment of segments) {
    if (!segment || /^\s*$/.test(segment)) {
      kept.push(segment);
      continue;
    }
    if (INJECTION_PATTERNS.some((p) => p.test(segment))) {
      flagged = true;
      continue;
    }
    let cleaned = segment;
    for (const p of INJECTION_PATTERNS) {
      if (p.test(cleaned)) {
        flagged = true;
        cleaned = cleaned.replace(p, " ").replace(/\s+/g, " ").trim();
      }
    }
    if (cleaned) kept.push(cleaned);
  }
  return { text: kept.join("").replace(/\s+/g, " ").trim(), flagged };
}
function stripBoilerplateHtml(html) {
  return html.replace(/<script[\s\S]*?<\/script>/gi, "").replace(/<style[\s\S]*?<\/style>/gi, "").replace(/<!--[\s\S]*?-->/g, "").replace(/<nav[\s\S]*?<\/nav>/gi, "").replace(/<aside[\s\S]*?<\/aside>/gi, "").replace(/<(header|footer)[\s\S]*?<\/\1>/gi, "");
}

// src/parser.ts
var PARSER_VERSION = "0.1.0";
function meta(html, key) {
  const re = new RegExp(
    `<meta[^>]+(?:name|property)=["']${key}["'][^>]+content=["']([^"']+)["']`,
    "i"
  );
  const alt = new RegExp(
    `<meta[^>]+content=["']([^"']+)["'][^>]+(?:name|property)=["']${key}["']`,
    "i"
  );
  return html.match(re)?.[1] ?? html.match(alt)?.[1];
}
function textBetween(html, label) {
  const re = new RegExp(
    `${label}\\s*[:\uFF1A]</[^>]+>\\s*<[^>]+>([^<]+)`,
    "i"
  );
  const m = html.match(re);
  return m?.[1]?.trim();
}
function parseDocumentHtml(html, sourceUrl, now = /* @__PURE__ */ new Date()) {
  const cleaned = stripBoilerplateHtml(html);
  const titleRaw = meta(cleaned, "og:title") ?? cleaned.match(/<h1[^>]*>([^<]+)<\/h1>/i)?.[1] ?? cleaned.match(/<title>([^<]+)<\/title>/i)?.[1] ?? "Untitled";
  const { text: title, flagged } = stripPromptInjection(titleRaw);
  const docNumRaw = textBetween(cleaned, "S\u1ED1 hi\u1EC7u") ?? textBetween(cleaned, "So hieu") ?? title;
  const documentNumber = normalizeDocumentNumber(docNumRaw ?? "");
  const statusRaw = textBetween(cleaned, "T\xECnh tr\u1EA1ng") ?? textBetween(cleaned, "Tinh trang") ?? "";
  const issuedRaw = textBetween(cleaned, "Ng\xE0y ban h\xE0nh") ?? textBetween(cleaned, "Ngay ban hanh");
  const effectiveRaw = textBetween(cleaned, "Ng\xE0y hi\u1EC7u l\u1EF1c") ?? textBetween(cleaned, "Ngay hieu luc");
  const bodyText = cleaned.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 500);
  const { text: safeBody, flagged: bodyFlagged } = stripPromptInjection(bodyText);
  const notes = [];
  if (flagged || bodyFlagged) {
    notes.push("Stripped suspected prompt-injection content from HTML.");
  }
  if (/đăng nhập|dang nhap|login required/i.test(cleaned)) {
    notes.push("Page indicates login may be required for full content.");
  }
  if (/captcha/i.test(cleaned)) {
    notes.push("CAPTCHA markers detected in HTML.");
  }
  return {
    source: "thuvienphapluat",
    sourceUrl,
    canonicalUrl: meta(cleaned, "og:url") ?? sourceUrl,
    documentNumber,
    title: title.trim(),
    issuingAuthority: textBetween(cleaned, "C\u01A1 quan ban h\xE0nh"),
    issuedDate: issuedRaw ? normalizeIsoDate(issuedRaw) : void 0,
    effectiveDate: effectiveRaw ? normalizeIsoDate(effectiveRaw) : void 0,
    status: statusRaw ? normalizeStatus(statusRaw) : "unknown",
    relevantExcerpts: safeBody ? [{ text: safeBody.slice(0, 280), sourceUrl }] : void 0,
    retrievedAt: now.toISOString(),
    confidence: notes.length ? "low" : "medium",
    verificationNotes: notes.length ? notes : void 0
  };
}
function detectStopSignals(html) {
  if (/captcha/i.test(html)) return "CAPTCHA";
  if (/paywall|nâng cấp tài khoản|nang cap tai khoan|gói pro|goi pro/i.test(html)) {
    return "PAYWALL";
  }
  if (/đăng nhập để|dang nhap de|vui lòng đăng nhập/i.test(html)) {
    return "LOGIN_REQUIRED";
  }
  return void 0;
}

// src/audit-log.ts
function createAuditEntry(partial) {
  return {
    ...partial,
    at: partial.at ?? (/* @__PURE__ */ new Date()).toISOString(),
    parserVersion: PARSER_VERSION
  };
}
function sanitizeForLog(text) {
  return text.replace(/(password|token|cookie|authorization)\s*[:=]\s*\S+/gi, "$1=[REDACTED]").slice(0, 500);
}

// src/cache.ts
var TtlCache = class {
  constructor(ttlSeconds) {
    this.ttlSeconds = ttlSeconds;
  }
  store = /* @__PURE__ */ new Map();
  hits = 0;
  misses = 0;
  get(key, now = Date.now()) {
    const entry = this.store.get(key);
    if (!entry) {
      this.misses += 1;
      return void 0;
    }
    if (entry.expiresAt <= now) {
      this.store.delete(key);
      this.misses += 1;
      return void 0;
    }
    this.hits += 1;
    return entry.value;
  }
  set(key, value, now = Date.now()) {
    if (this.ttlSeconds <= 0) return;
    this.store.set(key, {
      value,
      expiresAt: now + this.ttlSeconds * 1e3
    });
  }
  clear() {
    this.store.clear();
  }
};

// src/config.ts
var DEFAULT_ALLOWLIST = [
  "thuvienphapluat.vn",
  "www.thuvienphapluat.vn",
  "vbpl.vn",
  "www.vbpl.vn",
  "chinhphu.vn",
  "www.chinhphu.vn",
  "vanban.chinhphu.vn",
  "customs.gov.vn",
  "www.customs.gov.vn",
  "gdt.gov.vn",
  "www.gdt.gov.vn",
  "mof.gov.vn",
  "www.mof.gov.vn",
  "moit.gov.vn",
  "www.moit.gov.vn"
];
function parseMode(raw) {
  const v = (raw ?? "link-only").trim().toLowerCase();
  if (v === "link-only" || v === "official" || v === "public-search" || v === "browser") {
    return v;
  }
  return "link-only";
}
function loadConfig(overrides = {}) {
  return {
    mode: overrides.mode ?? parseMode(process.env.TVPL_INTEGRATION_MODE),
    requestsPerMinute: overrides.requestsPerMinute ?? Number(process.env.TVPL_REQUESTS_PER_MINUTE ?? 5),
    cacheTtlSeconds: overrides.cacheTtlSeconds ?? Number(process.env.TVPL_CACHE_TTL_SECONDS ?? 21600),
    allowBrowser: overrides.allowBrowser ?? process.env.TVPL_ALLOW_BROWSER === "true",
    runLiveTests: overrides.runLiveTests ?? process.env.RUN_TVPL_LIVE_TESTS === "true",
    domainAllowlist: overrides.domainAllowlist ?? DEFAULT_ALLOWLIST,
    maxConcurrentBrowser: overrides.maxConcurrentBrowser ?? 1
  };
}

// src/errors.ts
var LegalIntegrationError = class extends Error {
  code;
  retryable;
  constructor(code, message, retryable = false) {
    super(message);
    this.name = "LegalIntegrationError";
    this.code = code;
    this.retryable = retryable;
  }
};

// src/query-classifier.ts
var DOMAIN_KEYWORDS = [
  { domain: "hai-quan", patterns: [/hải quan|hai quan|xuất nhập khẩu|xnk|hs code/i] },
  { domain: "thue", patterns: [/thuế|thue|hóa đơn|hoa don|gtgt|tncn/i] },
  { domain: "logistics", patterns: [/logistics|vận tải|van tai|kho bãi|kho bai/i] },
  { domain: "lao-dong", patterns: [/lao động|lao dong|bảo hiểm|bao hiem|hợp đồng lao động/i] },
  { domain: "doanh-nghiep", patterns: [/doanh nghiệp|doanh nghiep|đăng ký kinh doanh/i] }
];
function classifyQuery(raw) {
  const documentNumber = normalizeDocumentNumber(raw);
  const domain = DOMAIN_KEYWORDS.find((d) => d.patterns.some((p) => p.test(raw)))?.domain;
  const keywords = raw.replace(/[?!.,;:"']/g, " ").split(/\s+/).map((w) => w.trim()).filter((w) => w.length > 2).slice(0, 12);
  return {
    raw: raw.trim(),
    documentNumber,
    keywords,
    domain
  };
}

// src/rate-limiter.ts
var RateLimiter = class {
  constructor(maxPerMinute, circuitCooldownMs = 6e4) {
    this.maxPerMinute = maxPerMinute;
    this.circuitCooldownMs = circuitCooldownMs;
  }
  timestamps = [];
  circuitOpenUntil = 0;
  tryAcquire(now = Date.now()) {
    if (now < this.circuitOpenUntil) {
      throw new LegalIntegrationError(
        "CIRCUIT_OPEN",
        "Circuit breaker open after 403/429/CAPTCHA",
        true
      );
    }
    const windowStart = now - 6e4;
    this.timestamps = this.timestamps.filter((t) => t >= windowStart);
    if (this.timestamps.length >= this.maxPerMinute) {
      throw new LegalIntegrationError(
        "RATE_LIMITED",
        `Exceeded ${this.maxPerMinute} requests/minute`,
        true
      );
    }
    this.timestamps.push(now);
  }
  tripCircuit(now = Date.now()) {
    this.circuitOpenUntil = now + this.circuitCooldownMs;
  }
  /** Test helper */
  get size() {
    return this.timestamps.length;
  }
};

// src/search-adapter.ts
function buildTvplSearchUrl(query) {
  const q = encodeURIComponent(
    query.documentNumber ?? query.keywords.slice(0, 8).join(" ")
  );
  return `https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword=${q}`;
}
function buildPublicSearchQuery(query) {
  const term = query.documentNumber ?? query.keywords.slice(0, 6).join(" ");
  return `site:thuvienphapluat.vn "${term}"`;
}
function buildOfficialSearchUrls(query) {
  const q = encodeURIComponent(
    query.documentNumber ?? query.keywords.slice(0, 8).join(" ")
  );
  const urls = [
    {
      label: "C\u01A1 s\u1EDF d\u1EEF li\u1EC7u qu\u1ED1c gia v\u1EC1 VBPL (vbpl.vn)",
      url: `https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?keyword=${q}`
    },
    {
      label: "C\u1ED5ng th\xF4ng tin Ch\xEDnh ph\u1EE7",
      url: `https://vanban.chinhphu.vn/?keyword=${q}`
    }
  ];
  if (query.domain === "hai-quan") {
    urls.push({
      label: "C\u1ED5ng th\xF4ng tin H\u1EA3i quan",
      url: "https://www.customs.gov.vn/"
    });
  }
  if (query.domain === "thue") {
    urls.push({
      label: "T\u1ED5ng c\u1EE5c Thu\u1EBF",
      url: "https://www.gdt.gov.vn/"
    });
  }
  if (query.domain === "logistics" || query.domain === "doanh-nghiep") {
    urls.push({
      label: "B\u1ED9 C\xF4ng Th\u01B0\u01A1ng",
      url: "https://www.moit.gov.vn/"
    });
  }
  return urls;
}

// src/source-policy.ts
function assertFetchAllowed(params) {
  const host = params.targetHost.toLowerCase();
  const isTvpl = host === "thuvienphapluat.vn" || host.endsWith(".thuvienphapluat.vn");
  if (!isTvpl) return;
  if (params.mode === "link-only" || params.mode === "official") {
    throw new LegalIntegrationError(
      "POLICY_BLOCKED",
      "Mode link-only/official does not HTTP-fetch thuvienphapluat.vn. Return search URLs only.",
      false
    );
  }
  if (params.mode === "browser" && !params.allowBrowser) {
    throw new LegalIntegrationError(
      "BROWSER_BLOCKED_BY_POLICY",
      "Browser fetch to TVPL blocked until TVPL_ALLOW_BROWSER=true and written license.",
      false
    );
  }
  if (params.mode === "browser" || params.mode === "public-search") {
    throw new LegalIntegrationError(
      "POLICY_BLOCKED",
      "Automated access/collection from Th\u01B0 Vi\u1EC7n Ph\xE1p Lu\u1EADt is blocked pending permission (terms + robots Content-Signal).",
      false
    );
  }
}
function refuseBulk(query) {
  const lower = query.toLowerCase();
  if (/toàn\s*bộ|toan\s*bo|crawl|scrape|dump|mirror|sao\s*chép\s*hàng\s*loạt|sao\s*chep\s*hang\s*loat/.test(
    lower
  )) {
    throw new LegalIntegrationError(
      "BULK_REQUEST_REFUSED",
      "Bulk copy / crawl requests are refused by policy.",
      false
    );
  }
}

// src/client.ts
var VietnamLegalClient = class {
  config;
  limiter;
  cache;
  constructor(config) {
    this.config = loadConfig(config);
    this.limiter = new RateLimiter(this.config.requestsPerMinute);
    this.cache = new TtlCache(this.config.cacheTtlSeconds);
  }
  research(rawQuery) {
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
          success: true
        })
      };
    }
    try {
      refuseBulk(rawQuery);
      this.limiter.tryAcquire();
    } catch (err) {
      const stopReason = err instanceof LegalIntegrationError ? err.code : "UNVERIFIED";
      return this.stopped(rawQuery, requestId, stopReason, String(err));
    }
    const query = classifyQuery(rawQuery);
    const searchUrls = [];
    if (this.config.mode !== "official") {
      searchUrls.push({
        label: "Th\u01B0 Vi\u1EC7n Ph\xE1p Lu\u1EADt (tra c\u1EE9u)",
        url: buildTvplSearchUrl(query)
      });
    }
    searchUrls.push(...buildOfficialSearchUrls(query));
    if (this.config.mode === "public-search") {
      searchUrls.push({
        label: "Public search query (copy v\xE0o c\xF4ng c\u1EE5 t\xECm ki\u1EBFm)",
        url: `https://www.google.com/search?q=${encodeURIComponent(buildPublicSearchQuery(query))}`
      });
    }
    const retrievedAt = (/* @__PURE__ */ new Date()).toISOString();
    const markdownRaw = buildMarkdown({
      query,
      documents: [],
      searchUrls,
      checkedAt: retrievedAt,
      analysisNotes: "Ch\u1EBF \u0111\u1ED9 PoC link-only/official: OpenClaw cung c\u1EA5p \u0111\u01B0\u1EDDng d\u1EABn ngu\u1ED3n \u0111\u1EC3 b\u1EA1n t\u1EF1 x\xE1c minh. Kh\xF4ng scrape n\u1ED9i dung TVPL."
    });
    const { markdown } = enforceAnswerGuardrail(markdownRaw);
    const result = {
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
        success: true
      })
    };
    this.cache.set(cacheKey, result);
    return result;
  }
  stopped(rawQuery, requestId, stopReason, detail) {
    const query = classifyQuery(rawQuery);
    const searchUrls = [
      {
        label: "Th\u01B0 Vi\u1EC7n Ph\xE1p Lu\u1EADt (tra c\u1EE9u th\u1EE7 c\xF4ng)",
        url: buildTvplSearchUrl(query)
      },
      ...buildOfficialSearchUrls(query)
    ];
    const retrievedAt = (/* @__PURE__ */ new Date()).toISOString();
    const { markdown } = enforceAnswerGuardrail(
      buildMarkdown({
        query,
        documents: [],
        searchUrls,
        checkedAt: retrievedAt,
        stopReason: `${stopReason}: ${detail}`
      })
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
        stopReason
      })
    };
  }
};

// src/tool.ts
function createVietnamLegalTool(client) {
  return (_ctx) => {
    const cfg = _ctx.config ?? {};
    const mode = cfg.integrationMode ?? void 0;
    const active = client ?? new VietnamLegalClient({
      mode,
      requestsPerMinute: typeof cfg.requestsPerMinute === "number" ? cfg.requestsPerMinute : void 0,
      cacheTtlSeconds: typeof cfg.cacheTtlSeconds === "number" ? cfg.cacheTtlSeconds : void 0
    });
    return {
      name: "vietnam_legal_research",
      label: "Vietnam Legal Research",
      description: "Research Vietnamese legal documents for logistics, customs, tax, labor, and business questions. Returns search URLs (Th\u01B0 Vi\u1EC7n Ph\xE1p Lu\u1EADt + official government), structured citation template, and disclaimers. Does NOT scrape thuvienphapluat.vn by default. Never invent document numbers or URLs.",
      parameters: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "User legal question or document number, e.g. 'Ngh\u1ECB \u0111\u1ECBnh 123/2020/N\u0110-CP hi\u1EC7u l\u1EF1c?'"
          }
        },
        required: ["query"]
      },
      async execute(_toolCallId, params) {
        const result = active.research(params.query);
        return {
          content: [{ type: "text", text: result.markdown }],
          details: {
            mode: result.mode,
            requestId: result.requestId,
            searchUrls: result.searchUrls,
            stopReason: result.stopReason,
            audit: result.audit
          }
        };
      }
    };
  };
}

// src/index.ts
var PLUGIN_ID = "vietnam-legal-research";
var index_default = {
  id: PLUGIN_ID,
  configSchema: {
    type: "object",
    additionalProperties: false,
    properties: {
      integrationMode: {
        type: "string",
        enum: ["link-only", "official", "public-search", "browser"]
      },
      requestsPerMinute: { type: "number" },
      cacheTtlSeconds: { type: "number" }
    }
  },
  register(api) {
    const log = api.logger?.info?.bind(api.logger) ?? console.log;
    log(`[${PLUGIN_ID}] registered (default mode: link-only; TVPL scrape disabled)`);
    api.registerTool(createVietnamLegalTool(), {
      name: "vietnam_legal_research",
      optional: false
    });
  }
};
export {
  RateLimiter,
  TtlCache,
  VietnamLegalClient,
  assertFetchAllowed,
  classifyQuery,
  createVietnamLegalTool,
  index_default as default,
  detectStopSignals,
  enforceAnswerGuardrail,
  normalizeDocumentNumber,
  normalizeIsoDate,
  normalizeStatus,
  parseDocumentHtml,
  refuseBulk,
  stripPromptInjection
};
