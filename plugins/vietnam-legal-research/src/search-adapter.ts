import type { ResearchQuery } from "./types.js";

export function buildTvplSearchUrl(query: ResearchQuery): string {
  const q = encodeURIComponent(
    query.documentNumber ?? query.keywords.slice(0, 8).join(" "),
  );
  return `https://thuvienphapluat.vn/page/tim-van-ban.aspx?keyword=${q}`;
}

export function buildPublicSearchQuery(query: ResearchQuery): string {
  const term = query.documentNumber ?? query.keywords.slice(0, 6).join(" ");
  return `site:thuvienphapluat.vn "${term}"`;
}

export function buildOfficialSearchUrls(
  query: ResearchQuery,
): Array<{ label: string; url: string }> {
  const q = encodeURIComponent(
    query.documentNumber ?? query.keywords.slice(0, 8).join(" "),
  );
  const urls: Array<{ label: string; url: string }> = [
    {
      label: "Cơ sở dữ liệu quốc gia về VBPL (vbpl.vn)",
      url: `https://vbpl.vn/TW/Pages/vbpq-timkiem.aspx?keyword=${q}`,
    },
    {
      label: "Cổng thông tin Chính phủ",
      url: `https://vanban.chinhphu.vn/?keyword=${q}`,
    },
  ];

  if (query.domain === "hai-quan") {
    urls.push({
      label: "Cổng thông tin Hải quan",
      url: "https://www.customs.gov.vn/",
    });
  }
  if (query.domain === "thue") {
    urls.push({
      label: "Tổng cục Thuế",
      url: "https://www.gdt.gov.vn/",
    });
  }
  if (query.domain === "logistics" || query.domain === "doanh-nghiep") {
    urls.push({
      label: "Bộ Công Thương",
      url: "https://www.moit.gov.vn/",
    });
  }

  return urls;
}
