"""Merge evidence classes into the public series-pair lookup table."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "registry"
OVERLAP = ROOT / "data" / "overlap"
RELEASE = ROOT / "release"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pair(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    evidence: dict[tuple[str, str], dict[str, object]] = defaultdict(
        lambda: {
            "exact_gsm_count": 0,
            "exact_title_different_gsm_count": 0,
            "expression_confirmed_count": 0,
            "expression_supported_count": 0,
            "identifier_not_corroborated_count": 0,
            "exact_gsm_overlap_pattern": "",
        }
    )

    for row in read_csv(REGISTRY / "exact_reuse_series_pairs.csv"):
        key = pair(row["series_a"], row["series_b"])
        evidence[key]["exact_gsm_count"] = int(row["shared_sample_accessions"])
        evidence[key]["exact_gsm_overlap_pattern"] = row["overlap_pattern"]
    for row in read_csv(OVERLAP / "exact_title_alias_series_pairs.csv"):
        key = pair(row["series_a"], row["series_b"])
        evidence[key]["exact_title_different_gsm_count"] = int(row["candidate_links"])
    for row in read_csv(OVERLAP / "expression_validated_edges.csv"):
        key = pair(row["series_a"], row["series_b"])
        status = row["expression_evidence"]
        if status == "confirmed":
            evidence[key]["expression_confirmed_count"] = int(evidence[key]["expression_confirmed_count"]) + 1
        elif status == "supported":
            evidence[key]["expression_supported_count"] = int(evidence[key]["expression_supported_count"]) + 1
        else:
            evidence[key]["identifier_not_corroborated_count"] = int(evidence[key]["identifier_not_corroborated_count"]) + 1

    raw = json.loads((ROOT / "data" / "discovery" / "geo_discovery_raw.json").read_text(encoding="utf-8"))
    by_gse = {r["accession"]: r for r in raw["records"]}
    rows = []
    for (a, b), info in sorted(evidence.items()):
        exact = int(info["exact_gsm_count"])
        confirmed = int(info["expression_confirmed_count"])
        supported = int(info["expression_supported_count"])
        title = int(info["exact_title_different_gsm_count"])
        if exact or confirmed:
            tier = "high_confidence_overlap"
        elif supported:
            tier = "probable_overlap"
        elif title or int(info["identifier_not_corroborated_count"]):
            tier = "manual_review_required"
        else:
            tier = "no_detected_evidence"
        rows.append(
            {
                "series_a": a,
                "series_b": b,
                **info,
                "overall_evidence_tier": tier,
                "title_a": by_gse.get(a, {}).get("title", ""),
                "title_b": by_gse.get(b, {}).get("title", ""),
                "geo_url_a": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={a}",
                "geo_url_b": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={b}",
            }
        )

    path = RELEASE / "cohort_overlap_lookup.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    # A compact inventory allows the checker to distinguish out-of-scope accessions.
    inventory_rows = [
        {
            "series_accession": r["accession"],
            "title": r.get("title", ""),
            "sample_count": r.get("n_samples", len(r.get("samples", []))),
            "data_type": r.get("gdstype", ""),
            "platforms": r.get("gpl", ""),
        }
        for r in sorted(raw["records"], key=lambda x: x["accession"])
    ]
    with (RELEASE / "series_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(inventory_rows[0]))
        writer.writeheader()
        writer.writerows(inventory_rows)

    tiers = Counter(str(r["overall_evidence_tier"]) for r in rows)
    summary = {
        "series_inventory": len(inventory_rows),
        "series_pairs_with_evidence": len(rows),
        "evidence_tiers": dict(sorted(tiers.items())),
        "interpretation": "Absence from the edge table means no evidence was detected within this release, not proof of independence.",
    }
    (RELEASE / "release_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
