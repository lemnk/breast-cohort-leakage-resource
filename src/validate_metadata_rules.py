"""Evaluate metadata rules against exact-GSM positives and background pairs."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from build_title_alias_candidates import has_specific_identifier, normalize_title


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "discovery_v2" / "geo_discovery_raw.json"
COMPREHENSIVE = ROOT / "data" / "comprehensive"
OUT = ROOT / "reports" / "validation"
SEED = "metadata-validation-v1"
N_BACKGROUND = 100_000
N_AUDIT = 100


def strict_match(title_a: str, title_b: str) -> bool:
    return (
        has_specific_identifier(title_a)
        and has_specific_identifier(title_b)
        and normalize_title(title_a) == normalize_title(title_b)
    )


def main() -> None:
    payload = json.loads(RAW.read_text(encoding="utf-8"))
    records = payload["records"]
    by_gse = {r["accession"]: r for r in records}
    mentions_by_gsm: dict[str, list[tuple[str, str]]] = defaultdict(list)
    all_mentions: list[tuple[str, str, str]] = []
    for record in records:
        for sample in record.get("samples", []):
            item = (record["accession"], sample["accession"], sample.get("title", ""))
            all_mentions.append(item)
            mentions_by_gsm[sample["accession"]].append((record["accession"], sample.get("title", "")))

    positive_pairs = 0
    positive_normalized_equal = 0
    positive_strict_recovered = 0
    for mentions in mentions_by_gsm.values():
        unique = list({(g, t) for g, t in mentions})
        for left, right in combinations(unique, 2):
            if left[0] == right[0]:
                continue
            positive_pairs += 1
            positive_normalized_equal += normalize_title(left[1]) == normalize_title(right[1])
            positive_strict_recovered += strict_match(left[1], right[1])

    rng = random.Random(SEED)
    background = 0
    background_normalized_equal = 0
    background_strict_collision = 0
    attempts = 0
    while background < N_BACKGROUND:
        left = all_mentions[rng.randrange(len(all_mentions))]
        right = all_mentions[rng.randrange(len(all_mentions))]
        attempts += 1
        if left[0] == right[0] or left[1] == right[1]:
            continue
        background += 1
        background_normalized_equal += normalize_title(left[2]) == normalize_title(right[2])
        background_strict_collision += strict_match(left[2], right[2])

    candidate_links = []
    with (COMPREHENSIVE / "specific_title_alias_links.csv").open(encoding="utf-8", newline="") as handle:
        candidate_links = list(csv.DictReader(handle))
    metadata_support = 0
    support_reasons = defaultdict(int)
    enriched = []
    for row in candidate_links:
        a, b = by_gse[row["series_a"]], by_gse[row["series_b"]]
        pmid = bool(set(a.get("pubmedids", [])) & set(b.get("pubmedids", [])))
        bioproject = bool(a.get("bioproject") and a.get("bioproject") == b.get("bioproject"))
        summaries_equal = bool(a.get("summary") and a.get("summary") == b.get("summary"))
        supported = pmid or bioproject or summaries_equal
        metadata_support += supported
        if pmid:
            support_reasons["shared_pubmed"] += 1
        if bioproject:
            support_reasons["shared_bioproject"] += 1
        if summaries_equal:
            support_reasons["identical_series_summary"] += 1
        enriched.append(
            {
                **row,
                "shared_pubmed": pmid,
                "shared_bioproject": bioproject,
                "identical_series_summary": summaries_equal,
                "metadata_context_supported": supported,
                "series_title_a": a.get("title", ""),
                "series_title_b": b.get("title", ""),
                "geo_url_a": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={row['series_a']}",
                "geo_url_b": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={row['series_b']}",
            }
        )

    audit = sorted(
        enriched,
        key=lambda r: hashlib.sha256(f"{SEED}:{r['series_a']}:{r['sample_a']}:{r['series_b']}:{r['sample_b']}".encode()).hexdigest(),
    )[:N_AUDIT]
    for row in audit:
        row["manual_same_patient_or_specimen"] = ""
        row["manual_evidence"] = ""
        row["reviewer"] = ""

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "title_candidate_audit_sample.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audit[0]))
        writer.writeheader()
        writer.writerows(audit)

    summary = {
        "known_positive_exact_gsm_mention_pairs": positive_pairs,
        "positive_normalized_title_equal": positive_normalized_equal,
        "positive_normalized_title_equal_rate": positive_normalized_equal / positive_pairs,
        "positive_strict_rule_recovered": positive_strict_recovered,
        "positive_strict_rule_recovery_rate_within_exact_gsm_reuse": positive_strict_recovered / positive_pairs,
        "deterministic_background_pairs": background,
        "background_normalized_title_equal": background_normalized_equal,
        "background_strict_rule_collisions": background_strict_collision,
        "background_strict_collision_rate": background_strict_collision / background,
        "candidate_links": len(candidate_links),
        "candidate_links_with_context_support": metadata_support,
        "candidate_context_support_rate": metadata_support / len(candidate_links),
        "context_support_reasons": dict(support_reasons),
        "audit_sample_n": N_AUDIT,
        "audit_status": "frozen worksheet generated; structured public-record review is regenerated separately when cached GEO headers are present",
        "caveat": "Background pairs are presumed nonmatches, not a patient-identity gold standard. Metadata context supports study relatedness, not identity by itself.",
    }
    (OUT / "metadata_rule_validation.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
