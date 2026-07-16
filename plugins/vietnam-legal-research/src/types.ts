export type IntegrationMode =
  | "link-only"
  | "official"
  | "public-search"
  | "browser";

export type LegalConfidence = "high" | "medium" | "low";

export type LegalStatus =
  | "effective"
  | "partially-effective"
  | "expired"
  | "unknown";

export type LegalSource =
  | "thuvienphapluat"
  | "official-government"
  | "other";

export interface RelatedLegalDocument {
  documentNumber?: string;
  title: string;
  relation: "amends" | "replaces" | "guides" | "references" | "related";
  sourceUrl?: string;
}

export interface LegalDocumentRecord {
  source: LegalSource;
  sourceUrl: string;
  canonicalUrl?: string;
  documentNumber?: string;
  title: string;
  documentType?: string;
  issuingAuthority?: string;
  issuedDate?: string;
  effectiveDate?: string;
  expiryDate?: string;
  status?: LegalStatus;
  fields?: string[];
  summary?: string;
  relevantExcerpts?: Array<{
    text: string;
    section?: string;
    sourceUrl: string;
  }>;
  amendedBy?: RelatedLegalDocument[];
  replacedBy?: RelatedLegalDocument[];
  guidedBy?: RelatedLegalDocument[];
  relatedDocuments?: RelatedLegalDocument[];
  retrievedAt: string;
  verifiedAt?: string;
  confidence: LegalConfidence;
  verificationNotes?: string[];
}

export interface ResearchQuery {
  raw: string;
  documentNumber?: string;
  keywords: string[];
  domain?: string;
  asOfDate?: string;
}

export interface ResearchResult {
  mode: IntegrationMode;
  query: ResearchQuery;
  documents: LegalDocumentRecord[];
  searchUrls: Array<{ label: string; url: string }>;
  stopReason?: string;
  requestId: string;
  retrievedAt: string;
  markdown: string;
  audit: AuditEntry;
}

export interface AuditEntry {
  requestId: string;
  at: string;
  query: string;
  adapter: string;
  urls: string[];
  success: boolean;
  stopReason?: string;
  parserVersion: string;
}
