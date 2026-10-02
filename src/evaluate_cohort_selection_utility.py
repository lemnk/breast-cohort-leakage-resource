"""Run the prespecified release-3 cohort-selection resource evaluation."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "discovery_v2" / "geo_discovery_raw.json"
RELEASE = ROOT / "release_v3"
OUT = ROOT / "reports" / "resource_evaluation"
CACHE = ROOT / "data" / "resource_evaluation" / "geo_series_quick"

INCLUDE_TERMS = (
    "patient", "tumor", "tumour", "cohort", "clinical", "metastatic",
    "neoadjuvant", "survival", "therapy", "biomarker",
)
EXCLUDE_TERMS = (
    "cell line", "cell-line", "xenograft", "organoid", "single-cell",
    "single cell", "crispr", "in vitro", "mouse", "mice", "perturb",
    "kinase inhibitor", "platform evaluation",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows and fieldnames is None:
        raise ValueError(f"No rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def choose_studies(records: list[dict]) -> list[dict]:
    eligible = []
    for row in records:
        title = str(row.get("title", "")).lower()
        n_samples = int(row.get("n_samples") or 0)
        if n_samples < 100:
            continue
        if not any(term in title for term in INCLUDE_TERMS):
            continue
        if any(term in title for term in EXCLUDE_TERMS):
            continue
        data_type = str(row.get("gdstype", ""))
        stratum = "sequencing" if "high throughput sequencing" in data_type.lower() else "array"
        eligible.append({**row, "evaluation_stratum": stratum})
    selected = []
    for stratum in ("array", "sequencing"):
        rows = [row for row in eligible if row["evaluation_stratum"] == stratum]
        rows.sort(key=lambda row: (-int(row.get("n_samples") or 0), row["accession"]))
        selected.extend(rows[:15])
    return sorted(selected, key=lambda row: (row["evaluation_stratum"], -int(row["n_samples"]), row["accession"]))


def fetch_quick(accession: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{accession}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    url = (
        "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?"
        f"acc={accession}&targ=self&form=text&view=quick"
    )
    request = urllib.request.Request(url, headers={"User-Agent": "Onco-research-resource/3.0 contact:naolzed6@gmail.com"})
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                text = response.read().decode("utf-8", errors="replace")
            path.write_text(text, encoding="utf-8")
            time.sleep(0.34)
            return text
        except Exception as exc:  # pragma: no cover - network retry
            last_error = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"Could not fetch {accession}: {last_error}")


def documented_relations(selected: list[dict]) -> tuple[dict[tuple[str, str], set[str]], list[dict[str, object]]]:
    selected_ids = {row["accession"] for row in selected}
    by_pair: dict[tuple[str, str], set[str]] = defaultdict(set)
    raw_rows = []
    for row in selected:
        accession = row["accession"]
        text = fetch_quick(accession)
        relation_lines = [
            line.split("=", 1)[1].strip()
            for line in text.splitlines()
            if line.startswith("!Series_relation") and "=" in line
        ]
        for relation in relation_lines:
            targets = sorted(set(re.findall(r"GSE\d+", relation, flags=re.IGNORECASE)))
            for target in targets:
                target = target.upper()
                raw_rows.append(
                    {
                        "source_series": accession,
                        "target_series": target,
                        "target_in_evaluation": target in selected_ids,
                        "relation_text": relation,
                        "source_url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}",
                    }
                )
                if target in selected_ids and target != accession:
                    by_pair[pair_key(accession, target)].add(relation)
    return by_pair, raw_rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    selected = choose_studies(raw["records"])
    selected_ids = {row["accession"] for row in selected}
    if len(selected) != 30:
        raise RuntimeError(f"Protocol expected 30 selected studies, observed {len(selected)}")

    selected_rows = [
        {
            "accession": row["accession"],
            "stratum": row["evaluation_stratum"],
            "n_samples": row["n_samples"],
            "data_type": row["gdstype"],
            "title": row["title"],
            "geo_url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={row['accession']}",
        }
        for row in selected
    ]
    write_csv(OUT / "selected_studies.csv", selected_rows)

    gsm = {row["accession"]: {sample["accession"] for sample in row.get("samples", [])} for row in selected}
    geo_relations, geo_relation_rows = documented_relations(selected)
    write_csv(
        OUT / "documented_geo_relations.csv",
        geo_relation_rows,
        ["source_series", "target_series", "target_in_evaluation", "relation_text", "source_url"],
    )

    lookup = {
        pair_key(row["series_a"], row["series_b"]): row
        for row in read_csv(RELEASE / "cohort_overlap_lookup.csv")
    }
    explicit_reuse: dict[tuple[str, str], int] = defaultdict(int)
    for row in read_csv(ROOT / "reports" / "validation" / "explicit_geo_reuse_relationships.csv"):
        p = pair_key(row["source_series"], row["referenced_series"])
        if p[0] in selected_ids and p[1] in selected_ids:
            explicit_reuse[p] += 1

    pair_rows: list[dict[str, object]] = []
    for a, b in combinations(sorted(selected_ids), 2):
        p = pair_key(a, b)
        shared = sorted(gsm[a] & gsm[b])
        registry = lookup.get(p, {})
        relation_text = " | ".join(sorted(geo_relations.get(p, set())))
        exact_count = len(shared)
        checker_exact = int(registry.get("exact_gsm_count", 0) or 0)
        documented_count = explicit_reuse.get(p, 0)
        expression_count = int(registry.get("expression_corroborated_candidate_count", 0) or 0)
        expression_supported = int(registry.get("expression_supported_candidate_count", 0) or 0)
        title_count = int(registry.get("specific_title_candidate_count", 0) or 0)
        if exact_count and relation_text:
            finding_type = "declared_superseries_subseries_with_direct_accession_overlap"
            decision = "use one constituent definition or deduplicate shared GSMs before validation"
        elif exact_count:
            finding_type = "direct_GEO_sample_record_overlap"
            decision = "do not call cohorts independent; deduplicate shared GSMs"
        elif documented_count or relation_text:
            finding_type = "documented_reanalysis_or_series_relationship"
            decision = "review declared provenance before combining or separating cohorts"
        elif expression_count or expression_supported:
            finding_type = "expression_corroborated_repeated_material_candidate"
            decision = "manual source review required; identity is not verified"
        elif title_count:
            finding_type = "unresolved_title_identity_candidate"
            decision = "manual source review required; identity is unresolved"
        else:
            finding_type = "no_detected_evidence"
            decision = "no registry finding; independence still requires study-specific review"
        pair_rows.append(
            {
                "series_a": a,
                "series_b": b,
                "direct_gsm_intersection_count": exact_count,
                "checker_exact_gsm_count": checker_exact,
                "checker_matches_direct_intersection": exact_count == checker_exact,
                "documented_geo_relation": relation_text,
                "explicit_reuse_cited_gsm_count": documented_count,
                "expression_corroborated_candidate_count": expression_count,
                "expression_supported_candidate_count": expression_supported,
                "title_candidate_count": title_count,
                "finding_type": finding_type,
                "cohort_selection_action": decision,
            }
        )
    write_csv(OUT / "pairwise_evaluation.csv", pair_rows)

    finding_counts = Counter(str(row["finding_type"]) for row in pair_rows)
    direct_pairs = sum(int(row["direct_gsm_intersection_count"]) > 0 for row in pair_rows)
    checker_exact_pairs = sum(int(row["checker_exact_gsm_count"]) > 0 for row in pair_rows)
    mismatches = sum(row["checker_matches_direct_intersection"] is False for row in pair_rows)
    added_pairs = sum(
        int(row["direct_gsm_intersection_count"]) == 0
        and str(row["finding_type"]) != "no_detected_evidence"
        for row in pair_rows
    )
    actionable = [row for row in pair_rows if row["finding_type"] != "no_detected_evidence"]
    write_csv(OUT / "actionable_findings.csv", actionable)
    summary = {
        "protocol": "PROTOCOL_v3_20261002.md",
        "selected_studies": len(selected),
        "array_studies": sum(row["evaluation_stratum"] == "array" for row in selected),
        "sequencing_studies": sum(row["evaluation_stratum"] == "sequencing" for row in selected),
        "screened_pairs": len(pair_rows),
        "direct_gsm_intersection_pairs": direct_pairs,
        "checker_direct_overlap_pairs": checker_exact_pairs,
        "checker_direct_count_mismatches": mismatches,
        "pairs_added_beyond_direct_intersection": added_pairs,
        "finding_types": dict(sorted(finding_counts.items())),
        "actionable_or_review_required_pairs": len(actionable),
        "interpretation": (
            "Direct GSM intersection is the reference for accession overlap. The resource's "
            "incremental value is limited to consolidated provenance and review-required "
            "candidate evidence; candidate evidence is not verified identity."
        ),
    }
    (OUT / "evaluation_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
