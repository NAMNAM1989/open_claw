export type LegalErrorCode =
  | "CAPTCHA"
  | "PAYWALL"
  | "LOGIN_REQUIRED"
  | "HTTP_403"
  | "HTTP_429"
  | "TIMEOUT"
  | "SELECTOR_CHANGED"
  | "POLICY_BLOCKED"
  | "BROWSER_BLOCKED_BY_POLICY"
  | "BULK_REQUEST_REFUSED"
  | "UNVERIFIED"
  | "CONFLICTING_SOURCES"
  | "RATE_LIMITED"
  | "CIRCUIT_OPEN";

export class LegalIntegrationError extends Error {
  readonly code: LegalErrorCode;
  readonly retryable: boolean;

  constructor(code: LegalErrorCode, message: string, retryable = false) {
    super(message);
    this.name = "LegalIntegrationError";
    this.code = code;
    this.retryable = retryable;
  }
}

export function mapHttpStatus(status: number): LegalIntegrationError {
  if (status === 403) {
    return new LegalIntegrationError("HTTP_403", "HTTP 403 from source", true);
  }
  if (status === 429) {
    return new LegalIntegrationError("HTTP_429", "HTTP 429 rate limited", true);
  }
  return new LegalIntegrationError("UNVERIFIED", `HTTP ${status}`, false);
}
