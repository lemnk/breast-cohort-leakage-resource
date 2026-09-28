"""Find conservative cross-series sample-title reuse with different GSM IDs.

These links are candidates, not confirmed identities.  Titles must contain both
letters and digits, be at least six normalized characters, and be unique within
every implicated series.  Exact-GSM reuse is excluded from this table.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ROOT / "data" / "discovery"
OUT = ROOT / "data" / "overlap"


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    # Preserve terminal assay/phenotype polarity (eg, PanCK+ vs PanCK-).
    value = re.sub(r"(?<=\w)\+$", "positive", value)
    value = re.sub(r"(?<=\w)-$", "negative", value)
    return re.sub(r"[^a-z0-9]+", "", value)


CELL_LINE_TOKENS = {
    "mdamb231", "mdamb361", "hcc1806", "bt549", "hs578t", "mcf7", "t47d",
}


def has_specific_identifier(title: str) -> bool:
    """Require a namespaced alphanumeric token, not 'patient 10' or 'tumor 1'."""
    value = unicodedata.normalize("NFKC", title).casefold()
    compacted = re.sub(r"[^a-z0-9]+", "", value)
    if any(token in compacted for token in CELL_LINE_TOKENS):
        return False
    if re.fullmatch(r"(?:sample|patient|tumou?r|breasttumou?r|breastcancer|normalbreast)\d+", compacted):
        return False
    patterns = (
        r"\b[a-z]{2,}[-_]\d{2,}[a-z]*\b",  # HCSC-0003, PDX_044
        r"\b[a-z]+\d{2,}[a-z]*\b",         # P101T, M098T, PIM010
        r"\b[a-z]+[-_][a-z]+\d+[a-z]*(?:[-_]\d+)?\b",  # CTR_d14_1
    )
    return any(re.search(pattern, value) for pattern in patterns)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    records = json.loads((DISCOVERY / "geo_discovery_raw.json").read_text(encoding="utf-8"))["records"]
    by_gse = {r["accession"]: r for r in records}
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        for sample in record.get("samples", []):
            normalized = normalize_title(sample.get("title", ""))
            if (
                len(normalized) >= 6
                and re.search(r"[a-z]", normalized)
                and re.search(r"[0-9]", normalized)
                and has_specific_identifier(sample.get("title", ""))
            ):
                groups[normalized].append(
                    {
                        "series_accession": record["accession"],
                        "sample_accession": sample["accession"],
                        "sample_title": sample.get("title", ""),
                    }
                )

    candidate_rows: list[dict[str, str | int]] = []
    pair_counts: Counter[tuple[str, str]] = Counter()
    accepted_groups = 0
    for alias, members in sorted(groups.items()):
        series = sorted({m["series_accession"] for m in members})
        gsms = {m["sample_accession"] for m in members}
        if len(series) < 2 or len(gsms) < 2:
            continue
        if any(sum(m["series_accession"] == gse for m in members) != 1 for gse in series):
            continue
        accepted_groups += 1
        for left, right in combinations(sorted(members, key=lambda x: (x["series_accession"], x["sample_accession"])), 2):
            if left["series_accession"] == right["series_accession"]:
                continue
            pair = tuple(sorted((left["series_accession"], right["series_accession"])))
            pair_counts[pair] += 1
            shared_publications = sorted(
                set(by_gse[pair[0]].get("pubmedids", [])) & set(by_gse[pair[1]].get("pubmedids", []))
            )
            candidate_rows.append(
                {
                    "normalized_title": alias,
                    "series_a": left["series_accession"],
                    "sample_a": left["sample_accession"],
                    "title_a": left["sample_title"],
                    "series_b": right["series_accession"],
                    "sample_b": right["sample_accession"],
                    "title_b": right["sample_title"],
                    "shared_pubmed_ids": ";".join(shared_publications),
                    "evidence_tier": "exact_specific_title_candidate",
                }
            )

    pair_rows = [
        {
            "series_a": pair[0],
            "series_b": pair[1],
            "candidate_links": count,
            "shared_pubmed_ids": ";".join(
                sorted(set(by_gse[pair[0]].get("pubmedids", [])) & set(by_gse[pair[1]].get("pubmedids", [])))
            ),
            "title_a": by_gse[pair[0]].get("title", ""),
            "title_b": by_gse[pair[1]].get("title", ""),
        }
        for pair, count in pair_counts.most_common()
    ]
    write_csv(OUT / "exact_title_alias_candidates.csv", candidate_rows)
    write_csv(OUT / "exact_title_alias_series_pairs.csv", pair_rows)
    summary = {
        "candidate_alias_groups": accepted_groups,
        "candidate_cross_series_links": len(candidate_rows),
        "series_pairs": len(pair_rows),
        "series_involved": len(
            {str(r["series_a"]) for r in pair_rows} | {str(r["series_b"]) for r in pair_rows}
        ),
        "warning": "Exact specific titles with different GSM accessions are identity candidates, not proof of patient identity.",
    }
    (OUT / "title_alias_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
