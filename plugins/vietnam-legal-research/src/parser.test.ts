import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { detectStopSignals, parseDocumentHtml } from "./parser.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..", "fixtures");

describe("parseDocumentHtml", () => {
  it("extracts metadata from fixture", () => {
    const html = readFileSync(join(root, "sample-document.html"), "utf8");
    const doc = parseDocumentHtml(
      html,
      "https://thuvienphapluat.vn/van-ban/fixture-123-2020-nd-cp",
    );
    expect(doc.documentNumber).toBe("123/2020/NĐ-CP");
    expect(doc.status).toBe("effective");
    expect(doc.issuedDate).toBe("2020-10-19");
    expect(doc.effectiveDate).toBe("2022-07-01");
    expect(doc.issuingAuthority).toBe("Chính phủ");
  });

  it("strips prompt injection lines", () => {
    const html = readFileSync(join(root, "injection.html"), "utf8");
    const doc = parseDocumentHtml(html, "https://example.com/x");
    expect(doc.verificationNotes?.some((n) => /injection/i.test(n))).toBe(true);
    const excerpt = doc.relevantExcerpts?.[0]?.text ?? "";
    expect(excerpt).not.toMatch(/API key/i);
    expect(excerpt).toMatch(/thủ tục|pháp lý/i);
  });
});

describe("detectStopSignals", () => {
  it("detects captcha", () => {
    const html = readFileSync(join(root, "captcha.html"), "utf8");
    expect(detectStopSignals(html)).toBe("CAPTCHA");
  });

  it("detects paywall", () => {
    const html = readFileSync(join(root, "paywall.html"), "utf8");
    expect(detectStopSignals(html)).toBe("PAYWALL");
  });
});
