import { LegalIntegrationError } from "./errors.js";

export class RateLimiter {
  private timestamps: number[] = [];
  private circuitOpenUntil = 0;

  constructor(
    private readonly maxPerMinute: number,
    private readonly circuitCooldownMs = 60_000,
  ) {}

  tryAcquire(now = Date.now()): void {
    if (now < this.circuitOpenUntil) {
      throw new LegalIntegrationError(
        "CIRCUIT_OPEN",
        "Circuit breaker open after 403/429/CAPTCHA",
        true,
      );
    }
    const windowStart = now - 60_000;
    this.timestamps = this.timestamps.filter((t) => t >= windowStart);
    if (this.timestamps.length >= this.maxPerMinute) {
      throw new LegalIntegrationError(
        "RATE_LIMITED",
        `Exceeded ${this.maxPerMinute} requests/minute`,
        true,
      );
    }
    this.timestamps.push(now);
  }

  tripCircuit(now = Date.now()): void {
    this.circuitOpenUntil = now + this.circuitCooldownMs;
  }

  /** Test helper */
  get size(): number {
    return this.timestamps.length;
  }
}

export function jitterDelayMs(baseMs = 200, jitterMs = 300): number {
  return baseMs + Math.floor(Math.random() * jitterMs);
}
