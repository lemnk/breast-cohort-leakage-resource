"""Build a GEO-wide exact sample-accession reuse registry from discovery data."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ROOT / "data" / "discovery"
OUT = ROOT / "data" / "registry"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    payload = json.loads((DISCOVERY / "geo_discovery_raw.json").read_text(encoding="utf-8"))
    records = payload["records"]
    by_gse = {r["accession"]: r for r in records}
    sample_sets = {
        gse: {s["accession"] for s in record.get("samples", [])}
        for gse, record in by_gse.items()
    }

    mentions: dict[str, list[dict[str, str]]] = defaultdict(list)
    all_rows: list[dict[str, str]] = []
    for record in records:
        for sample in record.get("samples", []):
            row = {
                "series_accession": record["accession"],
                "sample_accession": sample["accession"],
                "sample_title": sample.get("title", ""),
                "series_title": record.get("title", ""),
                "data_type": record.get("gdstype", ""),
                "platforms": record.get("gpl", ""),
                "pubmed_ids": ";".join(record.get("pubmedids", [])),
            }
            all_rows.append(row)
            mentions[sample["accession"]].append(row)

    reused = {gsm: rows for gsm, rows in mentions.items() if len({r["series_accession"] for r in rows}) > 1}
    reuse_rows: list[dict[str, str | int]] = []
    pair_samples: dict[tuple[str, str], list[str]] = defaultdict(list)
    for gsm, rows in sorted(reused.items()):
        unique_series = sorted({r["series_accession"] for r in rows})
        titles = sorted({r["sample_title"] for r in rows if r["sample_title"]})
        reuse_rows.append(
            {
                "sample_accession": gsm,
                "series_count": len(unique_series),
                "series_accessions": ";".join(unique_series),
                "sample_titles": " | ".join(titles),
            }
        )
        for pair in combinations(unique_series, 2):
            pair_samples[pair].append(gsm)

    pair_rows: list[dict[str, str | int | float]] = []
    for (a, b), gsms in sorted(pair_samples.items(), key=lambda x: (-len(x[1]), x[0])):
        set_a, set_b = sample_sets[a], sample_sets[b]
        smaller = min(len(set_a), len(set_b))
        containment = len(gsms) / smaller if smaller else 0.0
        union = len(set_a | set_b)
        jaccard = len(gsms) / union if union else 0.0
        pubmed_a = set(by_gse[a].get("pubmedids", []))
        pubmed_b = set(by_gse[b].get("pubmedids", []))
        if containment == 1.0:
            pattern = "complete_containment"
        elif containment >= 0.8:
            pattern = "near_containment"
        else:
            pattern = "partial_overlap"
        pair_rows.append(
            {
                "series_a": a,
                "series_b": b,
                "shared_sample_accessions": len(gsms),
                "samples_a": len(set_a),
                "samples_b": len(set_b),
                "smaller_set_containment": round(containment, 6),
                "jaccard": round(jaccard, 6),
                "overlap_pattern": pattern,
                "shared_pubmed_ids": ";".join(sorted(pubmed_a & pubmed_b)),
                "title_a": by_gse[a].get("title", ""),
                "title_b": by_gse[b].get("title", ""),
                "sample_accession_list": ";".join(sorted(gsms)),
            }
        )

    write_csv(OUT / "discovery_sample_mentions.csv", all_rows)
    write_csv(OUT / "exact_reused_geo_samples.csv", reuse_rows)
    write_csv(OUT / "exact_reuse_series_pairs.csv", pair_rows)

    pattern_counts = Counter(str(r["overlap_pattern"]) for r in pair_rows)
    summary = {
        "query_defined_series": len(records),
        "sample_mentions": len(all_rows),
        "unique_geo_sample_accessions": len(mentions),
        "reused_geo_sample_accessions": len(reused),
        "series_with_exact_accession_reuse": len(
            {r["series_accession"] for rows in reused.values() for r in rows}
        ),
        "series_pairs_with_exact_accession_reuse": len(pair_rows),
        "pair_overlap_patterns": dict(sorted(pattern_counts.items())),
        "scope_note": "This is a query-defined discovery universe, not all of GEO and not yet a manually adjudicated clinical-cohort set.",
    }
    (OUT / "geo_reuse_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
