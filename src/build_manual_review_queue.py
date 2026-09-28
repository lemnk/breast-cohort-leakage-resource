"""Create a compact source-verification queue for unresolved series pairs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    raw = json.loads((ROOT / "data" / "discovery" / "geo_discovery_raw.json").read_text(encoding="utf-8"))
    records = {r["accession"]: r for r in raw["records"]}
    examples: dict[tuple[str, str], list[str]] = defaultdict(list)
    with (ROOT / "data" / "overlap" / "exact_title_alias_candidates.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            key = tuple(sorted((row["series_a"], row["series_b"])))
            if len(examples[key]) < 3:
                examples[key].append(f"{row['title_a']} = {row['title_b']}")

    output = []
    with (ROOT / "release" / "cohort_overlap_lookup.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["overall_evidence_tier"] != "manual_review_required":
                continue
            a, b = row["series_a"], row["series_b"]
            shared_pmids = sorted(set(records[a].get("pubmedids", [])) & set(records[b].get("pubmedids", [])))
            candidate_count = int(row["exact_title_different_gsm_count"]) + int(row["identifier_not_corroborated_count"])
            output.append(
                {
                    "series_a": a,
                    "series_b": b,
                    "candidate_links": candidate_count,
                    "shared_pubmed_ids": ";".join(shared_pmids),
                    "example_matches": " | ".join(examples[(a, b)]),
                    "title_a": records[a].get("title", ""),
                    "title_b": records[b].get("title", ""),
                    "review_priority": "high" if candidate_count >= 10 or shared_pmids else "standard",
                    "review_status": "pending_source_verification",
                }
            )
    output.sort(key=lambda r: (r["review_priority"] != "high", -int(r["candidate_links"]), r["series_a"]))
    path = ROOT / "release" / "manual_review_queue.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print(f"Wrote {len(output)} unresolved pairs to {path}")


if __name__ == "__main__":
    main()
