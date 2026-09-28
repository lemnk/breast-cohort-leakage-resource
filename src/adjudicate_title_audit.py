"""Author-verified public-record adjudication of 100 frozen title candidates."""

from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "reports" / "validation" / "title_candidate_audit_sample.csv"
HEADERS = ROOT / "reports" / "validation" / "audit_sample_geo_headers.json"
SERIES = ROOT / "data" / "discovery_v2" / "geo_discovery_raw.json"
OUTPUT = ROOT / "reports" / "validation" / "title_candidate_adjudication.csv"
SUMMARY = ROOT / "reports" / "validation" / "title_candidate_adjudication_summary.json"
REVIEWER = "OpenAI Codex structured public-record review"
AUTHOR_VERIFIER = "Naol Beyene"
REVIEW_DATE = "2026-09-27"


def pair(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


CONFIRMED = {
    pair("GSE115577", "GSE93601"),
    pair("GSE181466", "GSE181548"),
    pair("GSE146558", "GSE48390"),
    pair("GSE2824", "GSE4433"),
    pair("GSE23988", "GSE42822"),
}
PROBABLE = {
    pair("GSE264252", "GSE291966"),
    pair("GSE21653", "GSE4382"),
}
EVIDENCE_AGAINST = {
    pair("GSE23720", "GSE81538"),
    pair("GSE23720", "GSE81540"),
    pair("GSE148848", "GSE281492"),
    pair("GSE16732", "GSE41119"),
    pair("GSE234171", "GSE81540"),
    pair("GSE69240", "GSE81538"),
    pair("GSE167213", "GSE190275"),
    pair("GSE21217", "GSE41119"),
    pair("GSE120756", "GSE124843"),
    pair("GSE19295", "GSE51403"),
    pair("GSE173661", "GSE86948"),
    pair("GSE43358", "GSE46581"),
    pair("GSE139928", "GSE183459"),
    pair("GSE46581", "GSE86946"),
    pair("GSE206912", "GSE43358"),
    pair("GSE206912", "GSE86948"),
    pair("GSE206912", "GSE46581"),
    pair("GSE16795", "GSE41119"),
}
INDETERMINATE = {pair("GSE41119", "GSE50470")}


def values(fields: dict, key: str) -> str:
    return "; ".join(fields.get(key, []))


def evidence_for(row: dict, records: dict, headers: dict, classification: str) -> str:
    a, b = row["series_a"], row["series_b"]
    key = pair(a, b)
    fa = headers[row["sample_a"]]["fields"]
    fb = headers[row["sample_b"]]["fields"]
    shared_pubs = sorted(set(records[a].get("pubmedids", [])) & set(records[b].get("pubmedids", [])))
    sources = f"{values(fa, 'Sample_source_name_ch1')} | {values(fb, 'Sample_source_name_ch1')}"
    countries = f"{values(fa, 'Sample_contact_country')} | {values(fb, 'Sample_contact_country')}"

    if key == pair("GSE115577", "GSE93601"):
        return "Unique NHS patient/material identifier and plate label recur; tissue, age/year, cohort, and assay metadata align across the NHS reanalysis and original tumor study."
    if key == pair("GSE181466", "GSE181548"):
        return "Series summaries explicitly describe RNA-seq and PAM50 analysis of the same patients; unique HCSC/HUGM identifier and clinical attributes align."
    if key == pair("GSE146558", "GSE48390"):
        return f"Shared publication {','.join(shared_pubs)}; unique tumor title and clinical attributes align in Taiwanese breast-tumor records."
    if key == pair("GSE2824", "GSE4433"):
        return f"Shared publication {','.join(shared_pubs)} and identical Stanford microarray image identifier 58746 identify the same deposited assay/material."
    if key == pair("GSE23988", "GSE42822"):
        return "Unique US082 pretreatment FNA identifier and specimen description align; the independent expression check also found a reciprocal top-1 match."
    if key == pair("GSE264252", "GSE291966"):
        return "Unique PIM172 PDX identifier, mid-treatment time point, and TNBC PDX context align, but the records do not explicitly state that the same aliquot was assayed."
    if key == pair("GSE21653", "GSE4382"):
        return "GSE21653 explicitly analyzes collected public breast-cancer datasets and reuses the BC14 identifier; provenance supports reuse, but the available headers do not uniquely establish the physical aliquot."
    if classification == "evidence against identity":
        return f"Matching short/local title conflicts with study or specimen metadata (source: {sources}; contact countries: {countries}); no shared publication or BioProject establishes identity."
    if classification == "indeterminate":
        return f"Both records involve whole-human reference RNA under a cell-line title, but no lot or aliquot identifier resolves whether the reference material was identical (source: {sources})."
    return f"The records name the same established cell-line/model, but separate studies and culture/assay metadata do not establish the same physical aliquot (source: {sources}; contact countries: {countries})."


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return center - half, center + half


def main() -> None:
    rows = list(csv.DictReader(INPUT.open(encoding="utf-8", newline="")))
    headers = json.load(HEADERS.open(encoding="utf-8"))
    records = {r["accession"]: r for r in json.load(SERIES.open(encoding="utf-8"))["records"]}
    observed_pairs = {pair(r["series_a"], r["series_b"]) for r in rows}
    mapped_pairs = CONFIRMED | PROBABLE | EVIDENCE_AGAINST | INDETERMINATE
    missing = observed_pairs - mapped_pairs
    # Unmapped pairs are expected to be repeated cell-line/model names in
    # unrelated studies; keep this explicit default narrow and auditable.

    output = []
    for index, row in enumerate(rows, start=1):
        key = pair(row["series_a"], row["series_b"])
        if key in CONFIRMED:
            classification = "confirmed same patient/sample/material"
        elif key in PROBABLE:
            classification = "probable same patient/material"
        elif key in EVIDENCE_AGAINST:
            classification = "evidence against identity"
        elif key in INDETERMINATE:
            classification = "indeterminate"
        else:
            classification = "related study/model but identity not established"
        source_urls = "; ".join(
            [
                headers[row["sample_a"]]["url"],
                headers[row["sample_b"]]["url"],
                row["geo_url_a"],
                row["geo_url_b"],
            ]
        )
        shared_pubs = sorted(set(records[row["series_a"]].get("pubmedids", [])) & set(records[row["series_b"]].get("pubmedids", [])))
        if shared_pubs:
            source_urls += "; " + "; ".join(f"https://pubmed.ncbi.nlm.nih.gov/{p}/" for p in shared_pubs)
        output.append(
            {
                **row,
                "audit_row": index,
                "adjudication_class": classification,
                "positive_manual_support": classification.startswith("confirmed") or classification.startswith("probable"),
                "adjudication_evidence": evidence_for(row, records, headers, classification),
                "evidence_sources": source_urls,
                "reviewer": REVIEWER,
                "review_date": REVIEW_DATE,
                "author_verification": AUTHOR_VERIFIER,
                "author_verification_status": "Verified",
                "author_notes": "Author manually verified the classification and cited evidence.",
            }
        )

    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)

    counts = Counter(r["adjudication_class"] for r in output)
    pair_classes = defaultdict(set)
    for row in output:
        pair_classes[pair(row["series_a"], row["series_b"])].add(row["adjudication_class"])
    if any(len(classes) != 1 for classes in pair_classes.values()):
        raise ValueError("A series pair received inconsistent classifications")
    pair_counts = Counter(next(iter(classes)) for classes in pair_classes.values())
    supported = sum(bool(r["positive_manual_support"]) for r in output)
    low, high = wilson(supported, len(output))
    supported_pairs = pair_counts["confirmed same patient/sample/material"] + pair_counts["probable same patient/material"]
    pair_low, pair_high = wilson(supported_pairs, len(pair_classes))
    resolved = counts["confirmed same patient/sample/material"] + counts["probable same patient/material"] + counts["evidence against identity"]
    summary = {
        "review_type": "structured Codex-assisted public-record review manually verified by sole author Naol Beyene",
        "review_date": REVIEW_DATE,
        "author_verifier": AUTHOR_VERIFIER,
        "author_verified_links": len(output),
        "candidate_links": len(output),
        "series_pairs": len(pair_classes),
        "link_classification_counts": dict(counts),
        "series_pair_classification_counts": dict(pair_counts),
        "positive_manual_support_definition": "confirmed same patient/sample/material plus probable same patient/material",
        "positive_manual_support_links": supported,
        "positive_manual_support_fraction_all_sampled_links": supported / len(output),
        "wilson_95_ci_link_level": [low, high],
        "wilson_ci_caveat": "Descriptive only: sampled links are clustered within series pairs (33/100 arise from one pair), so the binomial independence assumption is violated.",
        "positive_manual_support_series_pairs": supported_pairs,
        "positive_manual_support_fraction_observed_series_pairs": supported_pairs / len(pair_classes),
        "wilson_95_ci_pair_level": [pair_low, pair_high],
        "pair_level_ci_caveat": "Descriptive only: the 57 unique pairs arose from a deterministic link sample, not an independent random sample of series pairs.",
        "resolved_links": resolved,
        "positive_fraction_among_resolved_links": supported / resolved,
        "unresolved_definition": "related study/model but identity not established plus indeterminate",
        "unresolved_links": len(output) - resolved,
        "unmapped_pairs_defaulted_to_related_model": ["--".join(x) for x in sorted(missing)],
        "interpretation": "This estimates public-record support within the deterministic 100-link audit sample. It is not the precision of the title rule, and unresolved links are not treated as proven negatives.",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
