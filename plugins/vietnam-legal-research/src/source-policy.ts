import { LegalIntegrationError } from "./errors.js";
import type { IntegrationMode } from "./types.js";

/** TVPL terms prohibit automated collection tools — enforce in code. */
export function assertFetchAllowed(params: {
  mode: IntegrationMode;
  allowBrowser: boolean;
  targetHost: string;
}): void {
  const host = params.targetHost.toLowerCase();
  const isTvpl =
    host === "thuvienphapluat.vn" || host.endsWith(".thuvienphapluat.vn");

  if (!isTvpl) return;

  if (params.mode === "link-only" || params.mode === "official") {
    throw new LegalIntegrationError(
      "POLICY_BLOCKED",
      "Mode link-only/official does not HTTP-fetch thuvienphapluat.vn. Return search URLs only.",
      false,
    );
  }

  if (params.mode === "browser" && !params.allowBrowser) {
    throw new LegalIntegrationError(
      "BROWSER_BLOCKED_BY_POLICY",
      "Browser fetch to TVPL blocked until TVPL_ALLOW_BROWSER=true and written license.",
      false,
    );
  }

  if (params.mode === "browser" || params.mode === "public-search") {
    throw new LegalIntegrationError(
      "POLICY_BLOCKED",
      "Automated access/collection from Thư Viện Pháp Luật is blocked pending permission (terms + robots Content-Signal).",
      false,
    );
  }
}

export function refuseBulk(query: string): void {
  const lower = query.toLowerCase();
  if (
    /toàn\s*bộ|toan\s*bo|crawl|scrape|dump|mirror|sao\s*chép\s*hàng\s*loạt|sao\s*chep\s*hang\s*loat/.test(
      lower,
    )
  ) {
    throw new LegalIntegrationError(
      "BULK_REQUEST_REFUSED",
      "Bulk copy / crawl requests are refused by policy.",
      false,
    );
  }
}
