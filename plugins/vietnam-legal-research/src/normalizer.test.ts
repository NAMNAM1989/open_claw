import { describe, expect, it } from "vitest";
import {
  normalizeDocumentNumber,
  normalizeIsoDate,
  normalizeStatus,
} from "./normalizer.js";

describe("normalizeDocumentNumber", () => {
  it("parses nghị định số hiệu", () => {
    expect(normalizeDocumentNumber("Tìm Nghị định 123/2020/NĐ-CP")).toBe(
      "123/2020/NĐ-CP",
    );
  });

  it("returns undefined when missing", () => {
    expect(normalizeDocumentNumber("hóa đơn chi hộ logistics")).toBeUndefined();
  });
});

describe("normalizeIsoDate", () => {
  it("parses DD/MM/YYYY", () => {
    expect(normalizeIsoDate("19/10/2020")).toBe("2020-10-19");
  });

  it("keeps ISO", () => {
    expect(normalizeIsoDate("2022-07-01")).toBe("2022-07-01");
  });
});

describe("normalizeStatus", () => {
  it("maps còn hiệu lực", () => {
    expect(normalizeStatus("Còn hiệu lực")).toBe("effective");
  });

  it("maps hết hiệu lực", () => {
    expect(normalizeStatus("Hết hiệu lực")).toBe("expired");
  });
});
