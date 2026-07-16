export interface CacheEntry<T> {
  value: T;
  expiresAt: number;
}

export class TtlCache<T> {
  private readonly store = new Map<string, CacheEntry<T>>();
  hits = 0;
  misses = 0;

  constructor(private readonly ttlSeconds: number) {}

  get(key: string, now = Date.now()): T | undefined {
    const entry = this.store.get(key);
    if (!entry) {
      this.misses += 1;
      return undefined;
    }
    if (entry.expiresAt <= now) {
      this.store.delete(key);
      this.misses += 1;
      return undefined;
    }
    this.hits += 1;
    return entry.value;
  }

  set(key: string, value: T, now = Date.now()): void {
    if (this.ttlSeconds <= 0) return;
    this.store.set(key, {
      value,
      expiresAt: now + this.ttlSeconds * 1000,
    });
  }

  clear(): void {
    this.store.clear();
  }
}
