/** Normalize Vietnamese legal document numbers to a compact form. */
export function normalizeDocumentNumber(raw: string): string | undefined {
  const cleaned = raw
    .normalize("NFC")
    .replace(/\s+/g, " ")
    .trim();

  // e.g. Nghị định 123/2020/NĐ-CP, Thông tư 219/2013/TT-BTC
  const m = cleaned.match(
    /(\d{1,4}\s*\/\s*\d{4}\s*\/\s*[A-ZĐ]{1,10}(?:-[A-ZĐ]{1,10})?)/i,
  );
  if (!m?.[1]) return undefined;
  return m[1]
    .toUpperCase()
    .replace(/\s+/g, "")
    .replace(/Đ/g, "Đ")
    .replace(/NĐ/g, "NĐ")
    .replace(/ND-CP/g, "NĐ-CP")
    .replace(/ND\//g, "NĐ/");
}

export function normalizeIsoDate(raw: string): string | undefined {
  const s = raw.trim();
  const iso = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (iso) return `${iso[1]}-${iso[2]}-${iso[3]}`;

  const dmy = s.match(/^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{4})$/);
  if (dmy) {
    const dd = dmy[1]!.padStart(2, "0");
    const mm = dmy[2]!.padStart(2, "0");
    return `${dmy[3]}-${mm}-${dd}`;
  }
  return undefined;
}

export function normalizeStatus(raw: string): "effective" | "partially-effective" | "expired" | "unknown" {
  const t = raw.toLowerCase();
  if (/còn hiệu lực|con hieu luc|đang hiệu lực|dang hieu luc|effective/.test(t)) {
    return "effective";
  }
  if (/hết hiệu lực một phần|het hieu luc mot phan|partial/.test(t)) {
    return "partially-effective";
  }
  if (/hết hiệu lực|het hieu luc|expired|không còn hiệu lực/.test(t)) {
    return "expired";
  }
  return "unknown";
}
