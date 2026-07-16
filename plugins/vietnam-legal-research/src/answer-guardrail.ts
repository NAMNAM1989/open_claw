import { LEGAL_DISCLAIMER } from "./citation-builder.js";

export function enforceAnswerGuardrail(markdown: string): {
  markdown: string;
  violations: string[];
} {
  const violations: string[] = [];
  let out = markdown;

  if (!/https?:\/\//i.test(out)) {
    violations.push("missing_source_url");
    out += "\n\n> Thiếu URL nguồn — không được kết luận pháp lý.";
  }

  if (!out.includes("không thay thế") && !out.includes(LEGAL_DISCLAIMER.slice(0, 20))) {
    violations.push("missing_disclaimer");
    out += `\n\n> Lưu ý: ${LEGAL_DISCLAIMER}`;
  }

  // Reject obviously fabricated TVPL paths with random ids if no http host match
  if (/thuvienphapluat\.vn\/van-ban\/fake-/i.test(out)) {
    violations.push("suspicious_fake_url");
    out = out.replace(/https?:\/\/[^\s)]*fake-[^\s)]*/gi, "[URL đã loại bỏ]");
  }

  return { markdown: out, violations };
}
