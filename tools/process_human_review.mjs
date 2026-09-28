import crypto from "node:crypto";
import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/cancer/breast_cohort_leakage_resource";
const sourcePath = "C:/Users/zewud/Downloads/caleb.xlsx";
const adjudicationPath = `${root}/reports/validation/title_candidate_adjudication.csv`;
const outputPath = `${root}/manuscript/reviewer_2_human_verification.xlsx`;
const summaryPath = `${root}/reports/validation/reviewer_2_human_verification_summary.json`;
const previewDir = `${root}/reports/validation/workbook_preview/caleb_corrected`;

const sourceBytes = await fs.readFile(sourcePath);
const sourceSha256 = crypto.createHash("sha256").update(sourceBytes).digest("hex");
const sourceBook = await SpreadsheetFile.importXlsx(await FileBlob.load(sourcePath));
const sourceSheet = sourceBook.worksheets.getItem("AI review 2");
const sourceValues = sourceSheet.getRange("A1:Z101").values;
const sourceHeaders = sourceValues[0].map(String);
const sourceRows = sourceValues.slice(1).map((row) =>
  Object.fromEntries(sourceHeaders.map((header, index) => [header, row[index] ?? ""])),
);

const adjudicationText = await fs.readFile(adjudicationPath, "utf8");
const adjudicationBook = await Workbook.fromCSV(adjudicationText, { sheetName: "Adjudication" });
const adjudicationSheet = adjudicationBook.worksheets.getItem("Adjudication");
const adjudicationValues = adjudicationSheet.getUsedRange().values;
const adjudicationHeaders = adjudicationValues[0].map(String);
const adjudicationRows = adjudicationValues.slice(1).map((row) =>
  Object.fromEntries(adjudicationHeaders.map((header, index) => [header, row[index] ?? ""])),
);

if (sourceRows.length !== 100 || adjudicationRows.length !== 100) {
  throw new Error(`Expected 100 rows in both files; found ${sourceRows.length} and ${adjudicationRows.length}.`);
}

const allowedClasses = [
  "confirmed same patient/sample/material",
  "probable same patient/material",
  "related study/model but identity not established",
  "evidence against identity",
  "indeterminate",
];
const adjudicationByRow = new Map(adjudicationRows.map((row) => [String(row.audit_row), row]));
const classCounts = Object.fromEntries(allowedClasses.map((label) => [label, 0]));
const mismatches = [];

for (const row of sourceRows) {
  const auditRow = String(row.audit_row);
  const expected = adjudicationByRow.get(auditRow);
  if (!expected) {
    mismatches.push({ audit_row: auditRow, issue: "missing adjudication row" });
    continue;
  }
  for (const field of ["series_a", "sample_a", "series_b", "sample_b"]) {
    if (String(row[field]) !== String(expected[field])) {
      mismatches.push({ audit_row: auditRow, field, source: row[field], expected: expected[field] });
    }
  }
  if (row.original_class !== expected.adjudication_class) {
    mismatches.push({ audit_row: auditRow, field: "original_class", source: row.original_class, expected: expected.adjudication_class });
  }
  if (row.second_ai_class !== expected.adjudication_class) {
    mismatches.push({ audit_row: auditRow, field: "reviewer_2_class", source: row.second_ai_class, expected: expected.adjudication_class });
  }
  if (!String(row.source_urls).trim()) {
    mismatches.push({ audit_row: auditRow, field: "source_urls", issue: "missing" });
  }
  if (!String(row.second_ai_evidence).trim()) {
    mismatches.push({ audit_row: auditRow, field: "reviewer_2_evidence", issue: "missing" });
  }
  if (String(row.same_class).toLowerCase() !== "yes") {
    mismatches.push({ audit_row: auditRow, field: "same_class", value: row.same_class });
  }
  if (!allowedClasses.includes(row.second_ai_class)) {
    mismatches.push({ audit_row: auditRow, field: "reviewer_2_class", issue: "invalid class", value: row.second_ai_class });
  } else {
    classCounts[row.second_ai_class] += 1;
  }
}

const expectedCounts = {
  "confirmed same patient/sample/material": 40,
  "probable same patient/material": 2,
  "related study/model but identity not established": 34,
  "evidence against identity": 23,
  indeterminate: 1,
};
for (const [label, expected] of Object.entries(expectedCounts)) {
  if (classCounts[label] !== expected) {
    mismatches.push({ field: "class_count", class: label, source: classCounts[label], expected });
  }
}
if (mismatches.length) {
  throw new Error(`Review cross-check failed: ${JSON.stringify(mismatches.slice(0, 20))}`);
}

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const review = workbook.worksheets.add("Reviewer 2 verification");

summary.getRange("A2:E2").merge();
summary.getRange("A2").values = [["Second human verification of 100 candidate links"]];
summary.getRange("A2:E2").format.font = { name: "Arial", size: 15, bold: true, color: "#17365D" };
summary.getRange("A3:E3").format.borders = { bottom: { style: "thin", color: "#9CA3AF" } };
summary.getRange("A5:B16").values = [
  ["Review measure", "Value"],
  ["Rows reviewed", 100],
  ["Confirmed same patient/sample/material", 40],
  ["Probable same patient/material", 2],
  ["Related study/model but identity not established", 34],
  ["Evidence against identity", 23],
  ["Indeterminate", 1],
  ["Rows consistent with existing classifications", 100],
  ["Independent review", "No"],
  ["Blinded to original classifications", "No"],
  ["Raw exact agreement", 1],
  ["Cohen's kappa", "Not reported"],
];
summary.getRange("B15").setNumberFormat("0.0%");
summary.getRange("D5:E12").values = [
  ["Interpretation", null],
  ["1", "The sole author reports that Caleb Yitna cross-checked all 100 candidate links against the cited public evidence."],
  ["2", "The supplied workbook exposed the original classifications and supporting evidence. The verification was therefore not blinded."],
  ["3", "All 100 reviewer classifications matched the existing row-level classifications."],
  ["4", "Raw agreement is descriptive. Cohen's kappa is not presented as an independent inter-reviewer reliability estimate."],
  ["5", "This verification does not create new ground truth and does not convert unresolved links into negatives."],
  ["6", "The reviewer name should appear publicly only with the reviewer's consent."],
  ["7", "The source workbook's obsolete AI labels were corrected based on the sole author's attribution of the completed review to Caleb Yitna."],
];

const outputHeaders = [
  "audit_row", "series_a", "sample_a", "title_a", "series_b", "sample_b", "title_b",
  "series_title_a", "series_title_b", "shared_pubmed", "shared_bioproject",
  "identical_series_summary", "metadata_context_supported", "source_urls", "original_class",
  "original_evidence", "author_verification_status", "reviewer_2_class", "reviewer_2_evidence",
  "exact_agreement", "reviewer_2_assessment", "reviewer_2_label", "review_date",
  "independent_review", "initially_blinded", "permitted_use",
];
const outputRows = sourceRows.map((row) => [
  Number(row.audit_row), row.series_a, row.sample_a, row.title_a, row.series_b, row.sample_b,
  row.title_b, row.series_title_a, row.series_title_b, row.shared_pubmed, row.shared_bioproject,
  row.identical_series_summary, row.metadata_context_supported, row.source_urls, row.original_class,
  row.original_evidence, row.author_verification_status, row.second_ai_class, row.second_ai_evidence,
  "Yes", "Consistent with existing classification and cited evidence", "Caleb Yitna",
  new Date("2026-09-27T12:00:00-05:00"), "No", "No",
  "Human verification of existing classifications; not a blinded inter-reviewer reliability assessment",
]);
review.getRange("A1:Z101").values = [outputHeaders, ...outputRows];
review.tables.add("A1:Z101", true, "Reviewer2VerificationTable");

for (const sheet of [summary, review]) sheet.showGridLines = false;
summary.tabColor = "#17365D";
review.tabColor = "#5B9BD5";

summary.getRange("A5:B5").format = { fill: "#17365D", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" } };
summary.getRange("D5:E5").format = { fill: "#17365D", font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" } };
summary.getRange("A5:E16").format.font = { name: "Arial", size: 10, color: "#1F2937" };
summary.getRange("A5:B5").format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
summary.getRange("D5:E5").format.font = { name: "Arial", size: 10, bold: true, color: "#FFFFFF" };
summary.getRange("D6:E12").format.wrapText = true;
summary.getRange("D6:E12").format.verticalAlignment = "top";
summary.getRange("A:A").format.columnWidth = 45;
summary.getRange("B:B").format.columnWidth = 18;
summary.getRange("C:C").format.columnWidth = 3;
summary.getRange("D:D").format.columnWidth = 8;
summary.getRange("E:E").format.columnWidth = 58;
summary.getRange("6:12").format.rowHeight = 42;

review.getRange("A1:Z101").format.font = { name: "Arial", size: 9, color: "#1F2937" };
review.getRange("A1:Z1").format = {
  fill: "#17365D",
  font: { name: "Arial", size: 9, bold: true, color: "#FFFFFF" },
  verticalAlignment: "center",
  horizontalAlignment: "center",
  wrapText: true,
};
review.getRange("A2:Z101").format.verticalAlignment = "top";
review.getRange("D2:I101").format.wrapText = true;
review.getRange("N2:S101").format.wrapText = true;
review.getRange("U2:Z101").format.wrapText = true;
review.getRange("W2:W101").setNumberFormat("yyyy-mm-dd");
review.freezePanes.freezeRows(1);
review.freezePanes.freezeColumns(2);

const widths = {
  A: 10, B: 12, C: 14, D: 20, E: 12, F: 14, G: 20, H: 42, I: 42,
  J: 12, K: 14, L: 18, M: 19, N: 58, O: 42, P: 58, Q: 18, R: 42,
  S: 58, T: 16, U: 34, V: 20, W: 13, X: 16, Y: 16, Z: 58,
};
for (const [column, width] of Object.entries(widths)) {
  review.getRange(`${column}:${column}`).format.columnWidth = width;
}
review.getRange("1:1").format.rowHeight = 48;
review.getRange("2:101").format.rowHeight = 54;

workbook.recalculate();

const summaryCheck = await workbook.inspect({
  kind: "table",
  range: "Summary!A2:E16",
  include: "values,formulas",
  tableMaxRows: 16,
  tableMaxCols: 5,
});
console.log(summaryCheck.ndjson);
const reviewCheck = await workbook.inspect({
  kind: "table",
  range: "'Reviewer 2 verification'!A1:Z6",
  include: "values,formulas",
  tableMaxRows: 6,
  tableMaxCols: 26,
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
  ["Summary", "A1:E17", "summary.png"],
  ["Reviewer 2 verification", "A1:Z8", "review.png"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  await fs.writeFile(`${previewDir}/${file}`, new Uint8Array(await preview.arrayBuffer()));
}

const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(outputPath);

const verificationSummary = {
  review_type: "unblinded human verification of existing classifications",
  reviewer: "Caleb Yitna",
  reviewer_identity_publication_requires_consent: true,
  author_attribution: "Naol Beyene stated that the completed review in caleb.xlsx was performed by Caleb Yitna and that the AI labels were obsolete template text.",
  source_workbook: "caleb.xlsx",
  source_sha256: sourceSha256,
  review_date: "2026-09-27",
  rows_cross_checked: 100,
  rows_matching_existing_classification: 100,
  rows_with_source_urls: 100,
  rows_with_reviewer_evidence: 100,
  raw_exact_agreement: 1.0,
  initially_blinded: false,
  independent_reliability_estimate: false,
  cohen_kappa_reported: false,
  class_counts: classCounts,
  cross_check_mismatches: 0,
};
await fs.writeFile(summaryPath, `${JSON.stringify(verificationSummary, null, 2)}\n`, "utf8");
console.log(JSON.stringify(verificationSummary, null, 2));
console.log(`Saved ${outputPath}`);
console.log(`Saved ${summaryPath}`);
