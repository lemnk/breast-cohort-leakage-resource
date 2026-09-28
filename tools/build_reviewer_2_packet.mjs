import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/cancer/breast_cohort_leakage_resource";
const input = `${root}/reports/validation/title_candidate_audit_sample.csv`;
const output = `${root}/manuscript/reviewer_2_blinded_review_packet.xlsx`;
const previewDir = `${root}/reports/validation/workbook_preview/reviewer_2`;

const csvText = await fs.readFile(input, "utf8");
const sourceWorkbook = await Workbook.fromCSV(csvText, { sheetName: "Source" });
const source = sourceWorkbook.worksheets.getItem("Source");
const sourceValues = source.getUsedRange().values;
const sourceHeaders = sourceValues[0].map(String);
const records = sourceValues.slice(1).map((row) =>
  Object.fromEntries(sourceHeaders.map((header, index) => [header, row[index] ?? ""])),
);

if (records.length !== 100) {
  throw new Error(`Expected 100 audit records, found ${records.length}.`);
}

const workbook = Workbook.create();
const instructions = workbook.worksheets.add("Instructions");
const review = workbook.worksheets.add("Blinded review");

instructions.getRange("A2:F2").merge();
instructions.getRange("A2").values = [["Independent review of 100 candidate links"]];
instructions.getRange("A2:F2").format.font = {
  name: "Arial",
  size: 15,
  bold: true,
  color: "#17365D",
};
instructions.getRange("A3:F3").format.borders = {
  bottom: { style: "thin", color: "#9CA3AF" },
};

instructions.getRange("A5:B10").values = [
  ["Review status", "Value"],
  ["Candidate links", 100],
  ["Classifications completed", null],
  ["Classifications remaining", null],
  ["Reviewer label", "Reviewer 2"],
  ["Identity publication", "Use Caleb Yitna's name only with the reviewer's consent"],
];
instructions.getRange("B7").formulas = [[
  '=COUNTIFS(\'Blinded review\'!$S$2:$S$101,"confirmed same patient/sample/material")+COUNTIFS(\'Blinded review\'!$S$2:$S$101,"probable same patient/material")+COUNTIFS(\'Blinded review\'!$S$2:$S$101,"related study/model but identity not established")+COUNTIFS(\'Blinded review\'!$S$2:$S$101,"evidence against identity")+COUNTIFS(\'Blinded review\'!$S$2:$S$101,"indeterminate")',
]];
instructions.getRange("B8").formulas = [["=B6-B7"]];

instructions.getRange("D5:F13").values = [
  ["Independent review procedure", null, null],
  ["1", "Review all 100 rows independently. Do not view the sole author's classifications before recording the initial decisions.", null],
  ["2", "Open the two GEO sample links and associated series records. Use linked publications or other public sources when needed.", null],
  ["3", "Choose exactly one of the five allowed classifications for every row. Do not treat uncertainty as evidence against identity.", null],
  ["4", "Record a concise evidence reason and every source URL used. The GEO links already supplied may be repeated in the source-URL field.", null],
  ["5", "Enter the reviewer name or label, review date, and whether the initial decision was made without access to the first reviewer's classification.", null],
  ["6", "Return this completed workbook without replacing initial decisions after discussion. Reconciliation will be recorded in a separate consensus file.", null],
  ["7", "If the original classifications were visible, enter No under initially_blinded. The review remains useful verification but is not a blinded reliability assessment.", null],
  ["8", "If evidence is insufficient or conflicting, use indeterminate. Do not force an affirmative or negative classification.", null],
];

instructions.getRange("A20:F20").merge();
instructions.getRange("A20").values = [["Allowed classification values"]];
instructions.getRange("A21:F25").values = [
  ["confirmed same patient/sample/material", null, null, null, null, null],
  ["probable same patient/material", null, null, null, null, null],
  ["related study/model but identity not established", null, null, null, null, null],
  ["evidence against identity", null, null, null, null, null],
  ["indeterminate", null, null, null, null, null],
];

const headers = [
  "audit_row",
  "normalized_title",
  "series_a",
  "sample_a",
  "title_a",
  "sample_url_a",
  "series_url_a",
  "series_b",
  "sample_b",
  "title_b",
  "sample_url_b",
  "series_url_b",
  "series_title_a",
  "series_title_b",
  "shared_pubmed",
  "shared_bioproject",
  "identical_series_summary",
  "metadata_context_supported",
  "reviewer_2_class",
  "reviewer_2_evidence",
  "reviewer_2_source_urls",
  "reviewer_2_name_or_label",
  "review_date",
  "initially_blinded",
];

const rows = records.map((record, index) => [
  index + 1,
  record.normalized_title,
  record.series_a,
  record.sample_a,
  record.title_a,
  `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=${record.sample_a}`,
  record.geo_url_a,
  record.series_b,
  record.sample_b,
  record.title_b,
  `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=${record.sample_b}`,
  record.geo_url_b,
  record.series_title_a,
  record.series_title_b,
  record.shared_pubmed,
  record.shared_bioproject,
  record.identical_series_summary,
  record.metadata_context_supported,
  "",
  "",
  "",
  "Reviewer 2",
  null,
  "",
]);

review.getRange("A1:X101").values = [headers, ...rows];
review.tables.add("A1:X101", true, "Reviewer2AuditTable");
review.getRange("S2:S101").dataValidation = {
  rule: {
    type: "list",
    values: [
      "confirmed same patient/sample/material",
      "probable same patient/material",
      "related study/model but identity not established",
      "evidence against identity",
      "indeterminate",
    ],
  },
};
review.getRange("X2:X101").dataValidation = {
  rule: { type: "list", values: ["Yes", "No"] },
};
review.getRange("W2:W101").setNumberFormat("yyyy-mm-dd");

review.getRange("A1:X101").format.font = { name: "Arial", size: 9, color: "#1F2937" };
review.getRange("A1:X1").format = {
  fill: "#17365D",
  font: { name: "Arial", size: 9, bold: true, color: "#FFFFFF" },
  verticalAlignment: "center",
  horizontalAlignment: "center",
  wrapText: true,
};
review.getRange("A2:X101").format.verticalAlignment = "top";
review.getRange("E2:N101").format.wrapText = true;
review.getRange("S2:X101").format.fill = "#FFF2CC";
review.getRange("S2:X101").format.wrapText = true;
review.getRange("S2:S101").conditionalFormats.add("containsBlanks", {
  format: { fill: "#FCE8E6", font: { color: "#B91C1C" } },
});
review.getRange("A2:A101").setNumberFormat("0");
review.freezePanes.freezeRows(1);
review.freezePanes.freezeColumns(4);
review.showGridLines = false;

const widths = {
  A: 10, B: 18, C: 12, D: 14, E: 20, F: 42, G: 42, H: 12,
  I: 14, J: 20, K: 42, L: 42, M: 42, N: 42, O: 12, P: 14,
  Q: 18, R: 19, S: 42, T: 58, U: 58, V: 22, W: 13, X: 16,
};
for (const [column, width] of Object.entries(widths)) {
  review.getRange(`${column}:${column}`).format.columnWidth = width;
}
review.getRange("1:1").format.rowHeight = 48;
review.getRange("2:101").format.rowHeight = 54;

instructions.getRange("A5:B5").format = {
  fill: "#17365D",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
};
instructions.getRange("D5:F5").format = {
  fill: "#17365D",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
};
instructions.getRange("A20:F20").format = {
  fill: "#D9EAF7",
  font: { name: "Arial", size: 10, bold: true, color: "#17365D" },
};
instructions.getRange("A5:F25").format.font = { name: "Arial", size: 10, color: "#1F2937" };
instructions.getRange("A5:B5").format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
instructions.getRange("D5:F5").format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
instructions.getRange("A20:F20").format.font = { name: "Arial", size: 10, bold: true, color: "#17365D" };
instructions.getRange("B6:B10").format.wrapText = true;
instructions.getRange("D6:F13").format.wrapText = true;
instructions.getRange("D6:F13").format.verticalAlignment = "top";
instructions.getRange("A:A").format.columnWidth = 42;
instructions.getRange("B:B").format.columnWidth = 28;
instructions.getRange("C:C").format.columnWidth = 3;
instructions.getRange("D:D").format.columnWidth = 8;
instructions.getRange("E:F").format.columnWidth = 40;
instructions.getRange("6:13").format.rowHeight = 40;
instructions.showGridLines = false;
instructions.tabColor = "#17365D";
review.tabColor = "#5B9BD5";

workbook.recalculate();

const summaryCheck = await workbook.inspect({
  kind: "table",
  range: "Instructions!A2:F25",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 6,
});
console.log(summaryCheck.ndjson);

const reviewCheck = await workbook.inspect({
  kind: "table",
  range: "'Blinded review'!A1:X6",
  include: "values,formulas",
  tableMaxRows: 6,
  tableMaxCols: 24,
});
console.log(reviewCheck.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

await fs.mkdir(previewDir, { recursive: true });
for (const [sheetName, range, file] of [
  ["Instructions", "A1:F26", "instructions.png"],
  ["Blinded review", "A1:X8", "blinded_review.png"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/${file}`, new Uint8Array(await preview.arrayBuffer()));
}

const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(output);
console.log(`Saved ${output}`);
