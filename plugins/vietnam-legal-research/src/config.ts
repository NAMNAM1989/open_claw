import type { IntegrationMode } from "./types.js";

export interface TvplConfig {
  mode: IntegrationMode;
  requestsPerMinute: number;
  cacheTtlSeconds: number;
  allowBrowser: boolean;
  runLiveTests: boolean;
  domainAllowlist: string[];
  maxConcurrentBrowser: number;
}

const DEFAULT_ALLOWLIST = [
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
  "www.moit.gov.vn",
];

function parseMode(raw: string | undefined): IntegrationMode {
  const v = (raw ?? "link-only").trim().toLowerCase();
  if (
    v === "link-only" ||
    v === "official" ||
    v === "public-search" ||
    v === "browser"
  ) {
    return v;
  }
  return "link-only";
}

export function loadConfig(
  overrides: Partial<TvplConfig> = {},
): TvplConfig {
  return {
    mode: overrides.mode ?? parseMode(process.env.TVPL_INTEGRATION_MODE),
    requestsPerMinute:
      overrides.requestsPerMinute ??
      Number(process.env.TVPL_REQUESTS_PER_MINUTE ?? 5),
    cacheTtlSeconds:
      overrides.cacheTtlSeconds ??
      Number(process.env.TVPL_CACHE_TTL_SECONDS ?? 21600),
    allowBrowser:
      overrides.allowBrowser ??
      process.env.TVPL_ALLOW_BROWSER === "true",
    runLiveTests:
      overrides.runLiveTests ??
      process.env.RUN_TVPL_LIVE_TESTS === "true",
    domainAllowlist: overrides.domainAllowlist ?? DEFAULT_ALLOWLIST,
    maxConcurrentBrowser: overrides.maxConcurrentBrowser ?? 1,
  };
}

export function isDomainAllowed(url: string, allowlist: string[]): boolean {
  try {
    const host = new URL(url).hostname.toLowerCase();
    return allowlist.some((d) => host === d || host.endsWith(`.${d}`));
  } catch {
    return false;
  }
}
