"""Check a proposed set of GEO series for detected sample/patient overlap."""

from __future__ import annotations

import argparse
import csv
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release_v2"


def normalize_gse(value: str) -> str:
    value = value.strip().upper()
    if value.isdigit():
        value = "GSE" + value
    if not (value.startswith("GSE") and value[3:].isdigit()):
        raise ValueError(f"Invalid GEO series accession: {value}")
    return value


def check(accessions: list[str]) -> list[dict[str, str]]:
    requested = sorted(set(normalize_gse(x) for x in accessions))
    with (RELEASE / "series_inventory.csv").open(encoding="utf-8", newline="") as handle:
        inventory = {r.get("series_accession") or r.get("accession") for r in csv.DictReader(handle)}
    with (RELEASE / "cohort_overlap_lookup.csv").open(encoding="utf-8", newline="") as handle:
        lookup = {(r["series_a"], r["series_b"]): r for r in csv.DictReader(handle)}
    results = []
    for a, b in combinations(requested, 2):
        if a not in inventory or b not in inventory:
            results.append({"series_a": a, "series_b": b, "status": "outside_release_scope", "details": ""})
            continue
        row = lookup.get((a, b))
        if not row:
            results.append(
                {
                    "series_a": a,
                    "series_b": b,
                    "status": "no_detected_evidence",
                    "details": "Not proof of independence",
                }
            )
            continue
        details = (
            f"exact_GSM={row['exact_gsm_count']}; "
            f"different_GSM_title={row['specific_title_candidate_count']}; "
            f"expression_confirmed={row['expression_confirmed_count']}; "
            f"expression_supported={row['expression_supported_count']}"
        )
        results.append(
            {
                "series_a": a,
                "series_b": b,
                "status": row["overall_evidence_tier"],
                "details": details,
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accessions", nargs="+", help="Two or more GEO GSE accessions")
    args = parser.parse_args()
    results = check(args.accessions)
    if not results:
        raise SystemExit("Provide at least two distinct accessions")
    for row in results:
        print(f"{row['series_a']} vs {row['series_b']}: {row['status']} {row['details']}")


if __name__ == "__main__":
    main()
