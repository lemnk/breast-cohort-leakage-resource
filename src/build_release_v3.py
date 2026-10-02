"""Build release 3 with direct overlap separated from candidate evidence."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPREHENSIVE = ROOT / "data" / "comprehensive"
EXPRESSION = ROOT / "data" / "overlap_v3"
DISCOVERY = ROOT / "data" / "discovery_v2"
VALIDATION = ROOT / "reports" / "validation"
RELEASE = ROOT / "release_v3"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def blank_evidence() -> dict[str, object]:
    return {
        "exact_gsm_count": 0,
        "exact_gsm_overlap_pattern": "",
        "documented_geo_reuse_count": 0,
        "documented_geo_relationship_types": "",
        "specific_title_candidate_count": 0,
        "shared_pubmed_ids": "",
        "expression_corroborated_candidate_count": 0,
        "expression_supported_candidate_count": 0,
        "identifier_not_corroborated_count": 0,
    }


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    evidence: dict[tuple[str, str], dict[str, object]] = defaultdict(blank_evidence)

    for row in read_csv(COMPREHENSIVE / "exact_gsm_series_pairs.csv"):
        p = pair_key(row["series_a"], row["series_b"])
        evidence[p]["exact_gsm_count"] = int(row["shared_gsm_count"])
        evidence[p]["exact_gsm_overlap_pattern"] = row["overlap_pattern"]

    for row in read_csv(COMPREHENSIVE / "specific_title_alias_series_pairs.csv"):
        p = pair_key(row["series_a"], row["series_b"])
        evidence[p]["specific_title_candidate_count"] = int(row["candidate_links"])
        evidence[p]["shared_pubmed_ids"] = row["shared_pubmed_ids"]

    for row in read_csv(EXPRESSION / "expression_candidate_results.csv"):
        p = pair_key(row["series_a"], row["series_b"])
        field = {
            "corroborated_candidate": "expression_corroborated_candidate_count",
            "supported_candidate": "expression_supported_candidate_count",
            "not_corroborated": "identifier_not_corroborated_count",
        }[row["expression_candidate_result"]]
        evidence[p][field] = int(evidence[p][field]) + 1

    reuse_by_pair: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in read_csv(VALIDATION / "explicit_geo_reuse_relationships.csv"):
        p = pair_key(row["source_series"], row["referenced_series"])
        evidence[p]["documented_geo_reuse_count"] = int(evidence[p]["documented_geo_reuse_count"]) + 1
        reuse_by_pair[p].add(row["relationship_type"])
    for p, kinds in reuse_by_pair.items():
        evidence[p]["documented_geo_relationship_types"] = "; ".join(sorted(kinds))

    raw = json.loads((DISCOVERY / "geo_discovery_raw.json").read_text(encoding="utf-8"))
    by_gse = {row["accession"]: row for row in raw["records"]}
    rows: list[dict[str, object]] = []
    for (a, b), info in sorted(evidence.items()):
        exact = int(info["exact_gsm_count"])
        documented = int(info["documented_geo_reuse_count"])
        candidate = any(
            int(info[field])
            for field in (
                "specific_title_candidate_count",
                "expression_corroborated_candidate_count",
                "expression_supported_candidate_count",
                "identifier_not_corroborated_count",
            )
        )
        if exact:
            evidence_class = "direct_accession_overlap"
            recommended_action = "do_not_treat_as_independent; inspect and deduplicate shared GSM records"
        elif documented:
            evidence_class = "documented_geo_reuse"
            recommended_action = "review declared provenance before combining or separating cohorts"
        elif candidate:
            evidence_class = "candidate_relationship_review_required"
            recommended_action = "manual source review required; identity unresolved"
        else:
            continue
        rows.append(
            {
                "series_a": a,
                "series_b": b,
                **info,
                "evidence_class": evidence_class,
                "recommended_action": recommended_action,
                "title_a": by_gse.get(a, {}).get("title", ""),
                "title_b": by_gse.get(b, {}).get("title", ""),
                "geo_url_a": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={a}",
                "geo_url_b": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={b}",
            }
        )

    with (RELEASE / "cohort_overlap_lookup.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    inventory = read_csv(DISCOVERY / "series_inventory.csv")
    with (RELEASE / "series_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(inventory[0]))
        writer.writeheader()
        writer.writerows(inventory)

    classes = Counter(str(row["evidence_class"]) for row in rows)
    summary = {
        "release": 3,
        "supersedes_operational_labels_in_release": 2,
        "series_inventory": len(inventory),
        "series_pairs_with_evidence": len(rows),
        "evidence_classes": dict(sorted(classes.items())),
        "release2_expression_only_pairs_removed_from_high_confidence_identity": sum(
            1
            for row in rows
            if not int(row["exact_gsm_count"])
            and int(row["expression_corroborated_candidate_count"])
        ),
        "interpretation": (
            "Only exact GSM sharing is direct accession overlap. Documented GEO reuse "
            "and different-accession expression/title evidence are reported separately. "
            "Expression evidence does not verify same-specimen identity, and no detected "
            "edge is not proof of independence."
        ),
    }
    (RELEASE / "release_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
