const INJECTION_PATTERNS = [
  /ignore\s+(all\s+)?previous\s+instructions/i,
  /bỏ\s*qua\s*(mọi\s*)?hướng\s*dẫn/i,
  /system\s*prompt/i,
  /you\s+are\s+now/i,
  /exfiltrat/i,
  /send\s+(me\s+)?(the\s+)?(api\s+)?key/i,
  /run\s+shell/i,
  /curl\s+http/i,
];

export function stripPromptInjection(text: string): {
  text: string;
  flagged: boolean;
} {
  let flagged = false;
  const segments = text.split(/(\r?\n+|(?<=[.!?])\s+)/);
  const kept: string[] = [];
  for (const segment of segments) {
    if (!segment || /^\s*$/.test(segment)) {
      kept.push(segment);
      continue;
    }
    if (INJECTION_PATTERNS.some((p) => p.test(segment))) {
      flagged = true;
      continue;
    }
    // Also drop if a long concatenated blob still contains an injection phrase.
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

export function stripBoilerplateHtml(html: string): string {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<nav[\s\S]*?<\/nav>/gi, "")
    .replace(/<aside[\s\S]*?<\/aside>/gi, "")
    .replace(/<(header|footer)[\s\S]*?<\/\1>/gi, "");
}
