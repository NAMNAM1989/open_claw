import { LegalIntegrationError } from "./errors.js";
import { assertFetchAllowed } from "./source-policy.js";
import type { IntegrationMode } from "./types.js";

/**
 * Browser adapter intentionally does not automate TVPL.
 * Kept as an explicit refusal surface for future licensed modes.
 */
export async function fetchViaBrowser(_params: {
  url: string;
  mode: IntegrationMode;
  allowBrowser: boolean;
}): Promise<never> {
  const host = (() => {
    try {
      return new URL(_params.url).hostname;
    } catch {
      return "invalid";
    }
  })();

  assertFetchAllowed({
    mode: _params.mode,
    allowBrowser: _params.allowBrowser,
    targetHost: host,
  });

  throw new LegalIntegrationError(
    "BROWSER_BLOCKED_BY_POLICY",
    "Browser automation is not implemented in this PoC.",
    false,
  );
}
