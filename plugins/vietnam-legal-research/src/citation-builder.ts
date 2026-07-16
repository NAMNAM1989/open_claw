import type { LegalDocumentRecord, ResearchQuery } from "./types.js";

export const LEGAL_DISCLAIMER =
  "Đây là nội dung hỗ trợ tra cứu, không thay thế ý kiến tư vấn pháp lý chuyên môn. Cần kiểm tra văn bản gốc và tình trạng hiệu lực tại thời điểm áp dụng.";

export function buildMarkdown(params: {
  query: ResearchQuery;
  documents: LegalDocumentRecord[];
  searchUrls: Array<{ label: string; url: string }>;
  checkedAt: string;
  stopReason?: string;
  analysisNotes?: string;
}): string {
  const doc = params.documents[0];
  const lines: string[] = ["## Kết quả tra cứu", ""];

  if (params.stopReason) {
    lines.push(`**Trạng thái:** dừng — ${params.stopReason}`, "");
  }

  lines.push(
    `**Văn bản:** ${doc?.title ?? "(chưa xác minh — mở nguồn bên dưới)"}`,
    `**Số hiệu:** ${doc?.documentNumber ?? params.query.documentNumber ?? "(chưa xác minh)"}`,
    `**Cơ quan ban hành:** ${doc?.issuingAuthority ?? "(chưa xác minh)"}`,
    `**Ngày ban hành:** ${doc?.issuedDate ?? "(chưa xác minh)"}`,
    `**Ngày hiệu lực:** ${doc?.effectiveDate ?? "(chưa xác minh)"}`,
    `**Tình trạng hiệu lực:** ${doc?.status ?? "unknown"}`,
    `**Kiểm tra lúc:** ${params.checkedAt}`,
    "",
    "### Nội dung liên quan",
    "",
  );

  if (doc?.relevantExcerpts?.length) {
    for (const ex of doc.relevantExcerpts) {
      lines.push(`> ${ex.text}`, "");
    }
    lines.push("_Đoạn trên là trích/metadata từ nguồn hoặc fixture; không phải toàn văn._", "");
  } else {
    lines.push(
      "PoC chế độ link-only: chưa tải nội dung từ website. Hãy mở URL nguồn để đọc văn bản gốc.",
      "",
    );
  }

  lines.push("### Phân tích", "");
  lines.push(
    params.analysisNotes ??
      "Phần phân tích của AI (nếu có) phải tách biệt khỏi metadata nguồn và không được khẳng định tuyệt đối.",
    "",
  );

  lines.push("### Văn bản liên quan", "");
  const related = [
    ...(doc?.amendedBy ?? []),
    ...(doc?.replacedBy ?? []),
    ...(doc?.relatedDocuments ?? []),
  ];
  if (related.length === 0) {
    lines.push("- (chưa xác minh từ nguồn)", "");
  } else {
    for (const r of related) {
      lines.push(`- [${r.relation}] ${r.documentNumber ?? ""} ${r.title}`.trim());
    }
    lines.push("");
  }

  lines.push("### Nguồn", "");
  let i = 1;
  for (const u of params.searchUrls) {
    lines.push(`${i}. [${u.label}](${u.url})`);
    i += 1;
  }
  if (doc?.sourceUrl && !params.searchUrls.some((u) => u.url === doc.sourceUrl)) {
    lines.push(`${i}. [Nguồn tài liệu](${doc.sourceUrl})`);
  }

  lines.push("", `> Lưu ý: ${LEGAL_DISCLAIMER}`);
  return lines.join("\n");
}
