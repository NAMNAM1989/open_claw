import { normalizeDocumentNumber } from "./normalizer.js";
import type { ResearchQuery } from "./types.js";

const DOMAIN_KEYWORDS: Array<{ domain: string; patterns: RegExp[] }> = [
  { domain: "hai-quan", patterns: [/hải quan|hai quan|xuất nhập khẩu|xnk|hs code/i] },
  { domain: "thue", patterns: [/thuế|thue|hóa đơn|hoa don|gtgt|tncn/i] },
  { domain: "logistics", patterns: [/logistics|vận tải|van tai|kho bãi|kho bai/i] },
  { domain: "lao-dong", patterns: [/lao động|lao dong|bảo hiểm|bao hiem|hợp đồng lao động/i] },
  { domain: "doanh-nghiep", patterns: [/doanh nghiệp|doanh nghiep|đăng ký kinh doanh/i] },
];

export function classifyQuery(raw: string): ResearchQuery {
  const documentNumber = normalizeDocumentNumber(raw);
  const domain =
    DOMAIN_KEYWORDS.find((d) => d.patterns.some((p) => p.test(raw)))?.domain;

  const keywords = raw
    .replace(/[?!.,;:"']/g, " ")
    .split(/\s+/)
    .map((w) => w.trim())
    .filter((w) => w.length > 2)
    .slice(0, 12);

  return {
    raw: raw.trim(),
    documentNumber,
    keywords,
    domain,
  };
}
