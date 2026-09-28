import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/cancer/breast_cohort_leakage_resource";
const input = `${root}/reports/validation/title_candidate_adjudication.csv`;
const output = `${root}/manuscript/manual_title_audit_workbook.xlsx`;
const previewDir = `${root}/reports/validation/workbook_preview`;

const csvText = await fs.readFile(input, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Audit" });
const audit = workbook.worksheets.getItem("Audit");
const summary = workbook.worksheets.add("Summary");

audit.getRange("Z2:Z101").dataValidation = {
  rule: { type: "list", values: ["Verified", "Revision requested"] },
};
audit.getRange("X2:X101").setNumberFormat("yyyy-mm-dd");
audit.getRange("A1:AA101").format.font = { name: "Arial", size: 9, color: "#1F2937" };
audit.getRange("A1:AA1").format = {
  fill: "#17365D",
  font: { name: "Arial", size: 9, bold: true, color: "#FFFFFF" },
  verticalAlignment: "center",
  horizontalAlignment: "center",
  wrapText: true,
};
audit.getRange("A2:AA101").format.verticalAlignment = "top";
audit.getRange("A2:AA101").format.wrapText = false;
audit.getRange("T2:Y101").format.wrapText = true;
audit.getRange("Z2:AA101").format.fill = "#FFF2CC";
audit.getRange("Z2:AA101").format.wrapText = true;
audit.getRange("Z2:Z101").conditionalFormats.add("containsText", {
  text: "Verified",
  format: { fill: "#E8F5E9", font: { bold: true, color: "#166534" } },
});
audit.getRange("Z2:Z101").conditionalFormats.add("containsText", {
  text: "Revision requested",
  format: { fill: "#FCE8E6", font: { bold: true, color: "#B91C1C" } },
});
audit.freezePanes.freezeRows(1);
audit.freezePanes.freezeColumns(2);
audit.showGridLines = false;

const widths = {
  A: 16, B: 12, C: 14, D: 18, E: 12, F: 14, G: 18,
  H: 11, I: 13, J: 18, K: 18, L: 36, M: 36, N: 34,
  O: 34, P: 18, Q: 42, R: 30, S: 10, T: 34, U: 14,
  V: 68, W: 64, X: 13, Y: 22, Z: 20, AA: 42,
};
for (const [col, width] of Object.entries(widths)) {
  audit.getRange(`${col}:${col}`).format.columnWidth = width;
}
audit.getRange("1:1").format.rowHeight = 48;
audit.getRange("2:101").format.rowHeight = 42;

summary.getRange("A2:F2").merge();
summary.getRange("A2").values = [["Title-candidate structured public-record review"]];
summary.getRange("A2:F2").format.font = { name: "Arial", size: 15, bold: true, color: "#17365D" };
summary.getRange("A3:F3").format.borders = { bottom: { style: "thin", color: "#9CA3AF" } };
summary.getRange("A5:B14").values = [
  ["Review measure", "Value"],
  ["Sampled links", 100],
  ["Confirmed same patient/sample/material", null],
  ["Probable same patient/material", null],
  ["Related study/model; identity not established", null],
  ["Evidence against identity", null],
  ["Indeterminate", null],
  ["Affirmative public-record support", null],
  ["Support fraction in this deterministic sample", null],
  ["Author-verified rows", null],
];
summary.getRange("A15:B15").values = [["Rows not author-verified", null]];
summary.getRange("B7").formulas = [['=COUNTIF(Audit!$T$2:$T$101,"confirmed same patient/sample/material")']];
summary.getRange("B8").formulas = [['=COUNTIF(Audit!$T$2:$T$101,"probable same patient/material")']];
summary.getRange("B9").formulas = [['=COUNTIF(Audit!$T$2:$T$101,"related study/model but identity not established")']];
summary.getRange("B10").formulas = [['=COUNTIF(Audit!$T$2:$T$101,"evidence against identity")']];
summary.getRange("B11").formulas = [['=COUNTIF(Audit!$T$2:$T$101,"indeterminate")']];
summary.getRange("B12").formulas = [["=B7+B8"]];
summary.getRange("B13").formulas = [["=B12/B6"]];
summary.getRange("B14").formulas = [['=COUNTIF(Audit!$Z$2:$Z$101,"Verified")']];
summary.getRange("B15").formulas = [["=B6-B14"]];
summary.getRange("B13").setNumberFormat("0.0%");

summary.getRange("D5:F12").values = [
  ["Review record", null, null],
  ["1", "The structured public-record review contains 100 classifications and cited sources.", null],
  ["2", "Sole author Naol Beyene manually verified every row on 2026-09-27.", null],
  ["3", "Column Z records author verification; column AA preserves the author note.", null],
  ["4", "Do not convert related/model-only or indeterminate records into negatives.", null],
  ["5", "Confirmed plus probable is a support fraction in this deterministic sample, not title-rule precision.", null],
  ["6", "No formal binomial confidence interval is used because links are clustered within series pairs.", null],
  ["7", "The author sign-off verifies the review record; it is not an external accuracy study.", null],
];
summary.getRange("A5:B5").format = { fill: "#17365D", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" } };
summary.getRange("D5:F5").format = { fill: "#17365D", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" } };
summary.getRange("A5:F15").format.font = { name: "Arial", size: 10, color: "#1F2937" };
summary.getRange("A5:B5").format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
summary.getRange("D5:F5").format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
summary.getRange("D6:F12").format.wrapText = true;
summary.getRange("D6:F12").format.verticalAlignment = "top";
summary.getRange("A:A").format.columnWidth = 43;
summary.getRange("B:B").format.columnWidth = 18;
summary.getRange("C:C").format.columnWidth = 3;
summary.getRange("D:D").format.columnWidth = 8;
summary.getRange("E:F").format.columnWidth = 36;
summary.getRange("6:12").format.rowHeight = 37;
summary.showGridLines = false;

workbook.recalculate();
await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range, file] of [
  ["Summary", "A1:F16", "summary.png"],
  ["Audit", "S1:AA8", "audit.png"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/${file}`, new Uint8Array(await preview.arrayBuffer()));
}

const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(output);

const check = await workbook.inspect({
  kind: "table",
  range: "Summary!A2:F15",
  include: "values,formulas",
  tableMaxRows: 15,
  tableMaxCols: 6,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);
console.log(`Saved ${output}`);
