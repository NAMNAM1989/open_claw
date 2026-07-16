import {
  normalizeDocumentNumber,
  normalizeIsoDate,
  normalizeStatus,
} from "./normalizer.js";
import {
  stripBoilerplateHtml,
  stripPromptInjection,
} from "./prompt-injection.js";
import type { LegalDocumentRecord } from "./types.js";

export const PARSER_VERSION = "0.1.0";

function meta(html: string, key: string): string | undefined {
  const re = new RegExp(
    `<meta[^>]+(?:name|property)=["']${key}["'][^>]+content=["']([^"']+)["']`,
    "i",
  );
  const alt = new RegExp(
    `<meta[^>]+content=["']([^"']+)["'][^>]+(?:name|property)=["']${key}["']`,
    "i",
  );
  return html.match(re)?.[1] ?? html.match(alt)?.[1];
}

function textBetween(html: string, label: string): string | undefined {
  const re = new RegExp(
    `${label}\\s*[:：]</[^>]+>\\s*<[^>]+>([^<]+)`,
    "i",
  );
  const m = html.match(re);
  return m?.[1]?.trim();
}

export function parseDocumentHtml(
  html: string,
  sourceUrl: string,
  now = new Date(),
): LegalDocumentRecord {
  const cleaned = stripBoilerplateHtml(html);
  const titleRaw =
    meta(cleaned, "og:title") ??
    cleaned.match(/<h1[^>]*>([^<]+)<\/h1>/i)?.[1] ??
    cleaned.match(/<title>([^<]+)<\/title>/i)?.[1] ??
    "Untitled";
  const { text: title, flagged } = stripPromptInjection(titleRaw);

  const docNumRaw =
    textBetween(cleaned, "Số hiệu") ??
    textBetween(cleaned, "So hieu") ??
    title;
  const documentNumber = normalizeDocumentNumber(docNumRaw ?? "");

  const statusRaw =
    textBetween(cleaned, "Tình trạng") ??
    textBetween(cleaned, "Tinh trang") ??
    "";
  const issuedRaw =
    textBetween(cleaned, "Ngày ban hành") ??
    textBetween(cleaned, "Ngay ban hanh");
  const effectiveRaw =
    textBetween(cleaned, "Ngày hiệu lực") ??
    textBetween(cleaned, "Ngay hieu luc");

  const bodyText = cleaned
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 500);
  const { text: safeBody, flagged: bodyFlagged } = stripPromptInjection(bodyText);

  const notes: string[] = [];
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
    issuingAuthority: textBetween(cleaned, "Cơ quan ban hành"),
    issuedDate: issuedRaw ? normalizeIsoDate(issuedRaw) : undefined,
    effectiveDate: effectiveRaw ? normalizeIsoDate(effectiveRaw) : undefined,
    status: statusRaw ? normalizeStatus(statusRaw) : "unknown",
    relevantExcerpts: safeBody
      ? [{ text: safeBody.slice(0, 280), sourceUrl }]
      : undefined,
    retrievedAt: now.toISOString(),
    confidence: notes.length ? "low" : "medium",
    verificationNotes: notes.length ? notes : undefined,
  };
}

export function detectStopSignals(html: string): string | undefined {
  if (/captcha/i.test(html)) return "CAPTCHA";
  if (/paywall|nâng cấp tài khoản|nang cap tai khoan|gói pro|goi pro/i.test(html)) {
    return "PAYWALL";
  }
  if (/đăng nhập để|dang nhap de|vui lòng đăng nhập/i.test(html)) {
    return "LOGIN_REQUIRED";
  }
  return undefined;
}
