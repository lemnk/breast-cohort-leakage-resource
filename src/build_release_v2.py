"""Build the comprehensive release-2 lookup and inventory."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPREHENSIVE = ROOT / "data" / "comprehensive"
OVERLAP = ROOT / "data" / "overlap"
DISCOVERY = ROOT / "data" / "discovery_v2"
RELEASE = ROOT / "release_v2"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    evidence: dict[tuple[str, str], dict[str, object]] = defaultdict(
        lambda: {
            "exact_gsm_count": 0,
            "exact_gsm_overlap_pattern": "",
            "specific_title_candidate_count": 0,
            "shared_pubmed_ids": "",
            "expression_confirmed_count": 0,
            "expression_supported_count": 0,
            "identifier_not_corroborated_count": 0,
        }
    )
    for row in read_csv(COMPREHENSIVE / "exact_gsm_series_pairs.csv"):
        p = key(row["series_a"], row["series_b"])
        evidence[p]["exact_gsm_count"] = int(row["shared_gsm_count"])
        evidence[p]["exact_gsm_overlap_pattern"] = row["overlap_pattern"]
    for row in read_csv(COMPREHENSIVE / "specific_title_alias_series_pairs.csv"):
        p = key(row["series_a"], row["series_b"])
        evidence[p]["specific_title_candidate_count"] = int(row["candidate_links"])
        evidence[p]["shared_pubmed_ids"] = row["shared_pubmed_ids"]
    for row in read_csv(OVERLAP / "expression_validated_edges.csv"):
        p = key(row["series_a"], row["series_b"])
        status = row["expression_evidence"]
        field = {
            "confirmed": "expression_confirmed_count",
            "supported": "expression_supported_count",
            "not_corroborated": "identifier_not_corroborated_count",
        }[status]
        evidence[p][field] = int(evidence[p][field]) + 1

    raw = json.loads((DISCOVERY / "geo_discovery_raw.json").read_text(encoding="utf-8"))
    by_gse = {r["accession"]: r for r in raw["records"]}
    rows = []
    for (a, b), info in sorted(evidence.items()):
        if int(info["exact_gsm_count"]) or int(info["expression_confirmed_count"]):
            tier = "high_confidence_overlap"
        elif int(info["expression_supported_count"]):
            tier = "probable_overlap"
        else:
            tier = "manual_review_required"
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
    with (RELEASE / "cohort_overlap_lookup.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    inventory = read_csv(DISCOVERY / "series_inventory.csv")
    with (RELEASE / "series_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(inventory[0]))
        writer.writeheader()
        writer.writerows(inventory)
    tiers = Counter(str(r["overall_evidence_tier"]) for r in rows)
    summary = {
        "release": 2,
        "series_inventory": len(inventory),
        "series_pairs_with_evidence": len(rows),
        "evidence_tiers": dict(sorted(tiers.items())),
        "high_confidence_series_involved": len(
            {str(r[side]) for r in rows if r["overall_evidence_tier"] == "high_confidence_overlap" for side in ("series_a", "series_b")}
        ),
        "interpretation": "Exact GSM reuse is direct repository overlap. Candidate aliases require source verification. No edge is not proof of independence.",
    }
    (RELEASE / "release_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
