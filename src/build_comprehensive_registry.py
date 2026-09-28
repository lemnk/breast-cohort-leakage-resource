"""Build exact-GSM and conservative title-alias reuse tables for release 2."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from build_title_alias_candidates import has_specific_identifier, normalize_title


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "discovery_v2" / "geo_discovery_raw.json"
OUT = ROOT / "data" / "comprehensive"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    records = json.loads(SOURCE.read_text(encoding="utf-8"))["records"]
    by_gse = {r["accession"]: r for r in records}
    sample_sets = {g: {s["accession"] for s in r.get("samples", [])} for g, r in by_gse.items()}
    gsm_mentions: dict[str, list[tuple[str, str]]] = defaultdict(list)
    title_groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for record in records:
        gse = record["accession"]
        for sample in record.get("samples", []):
            gsm, title = sample["accession"], sample.get("title", "")
            gsm_mentions[gsm].append((gse, title))
            if has_specific_identifier(title):
                title_groups[normalize_title(title)].append((gse, gsm, title))

    exact_pair_gsms: dict[tuple[str, str], list[str]] = defaultdict(list)
    reused_gsms = 0
    for gsm, mentions in gsm_mentions.items():
        series = sorted({g for g, _ in mentions})
        if len(series) > 1:
            reused_gsms += 1
            for p in combinations(series, 2):
                exact_pair_gsms[p].append(gsm)

    exact_rows = []
    for (a, b), gsms in sorted(exact_pair_gsms.items(), key=lambda x: (-len(x[1]), x[0])):
        smaller = min(len(sample_sets[a]), len(sample_sets[b]))
        containment = len(gsms) / smaller if smaller else 0.0
        pattern = "complete_containment" if containment == 1 else ("near_containment" if containment >= 0.8 else "partial_overlap")
        exact_rows.append(
            {
                "series_a": a,
                "series_b": b,
                "shared_gsm_count": len(gsms),
                "samples_a": len(sample_sets[a]),
                "samples_b": len(sample_sets[b]),
                "smaller_set_containment": round(containment, 6),
                "overlap_pattern": pattern,
                "shared_gsms": ";".join(sorted(gsms)),
            }
        )

    title_pair_count: Counter[tuple[str, str]] = Counter()
    title_rows = []
    title_alias_groups = 0
    for alias, mentions in sorted(title_groups.items()):
        series = {g for g, _, _ in mentions}
        gsms = {gsm for _, gsm, _ in mentions}
        if len(series) < 2 or len(gsms) < 2:
            continue
        if any(sum(g == target for g, _, _ in mentions) != 1 for target in series):
            continue
        title_alias_groups += 1
        for left, right in combinations(sorted(mentions), 2):
            if left[0] == right[0] or left[1] == right[1]:
                continue
            p = tuple(sorted((left[0], right[0])))
            title_pair_count[p] += 1
            title_rows.append(
                {
                    "normalized_title": alias,
                    "series_a": left[0],
                    "sample_a": left[1],
                    "title_a": left[2],
                    "series_b": right[0],
                    "sample_b": right[1],
                    "title_b": right[2],
                }
            )

    title_pair_rows = []
    for (a, b), count in title_pair_count.most_common():
        shared_pmids = sorted(set(by_gse[a].get("pubmedids", [])) & set(by_gse[b].get("pubmedids", [])))
        title_pair_rows.append(
            {
                "series_a": a,
                "series_b": b,
                "candidate_links": count,
                "shared_pubmed_ids": ";".join(shared_pmids),
                "title_a": by_gse[a].get("title", ""),
                "title_b": by_gse[b].get("title", ""),
            }
        )

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "exact_gsm_series_pairs.csv", exact_rows)
    write_csv(OUT / "specific_title_alias_links.csv", title_rows)
    write_csv(OUT / "specific_title_alias_series_pairs.csv", title_pair_rows)
    summary = {
        "series": len(records),
        "sample_mentions": sum(len(r.get("samples", [])) for r in records),
        "unique_gsm_accessions": len(gsm_mentions),
        "reused_gsm_accessions": reused_gsms,
        "exact_gsm_series_pairs": len(exact_rows),
        "exact_gsm_series_involved": len({g for p in exact_pair_gsms for g in p}),
        "exact_overlap_patterns": dict(Counter(r["overlap_pattern"] for r in exact_rows)),
        "specific_title_alias_groups": title_alias_groups,
        "specific_title_alias_links": len(title_rows),
        "specific_title_alias_series_pairs": len(title_pair_rows),
        "warning": "Title-alias results are review candidates; exact GSM reuse is direct repository-record overlap.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
