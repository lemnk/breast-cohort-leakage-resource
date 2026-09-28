"""Build conservative cross-series sample-identity candidates.

Identifier matching is intentionally separated from expression matching.  Only
explicit sample identifiers are used, and an alias must be unique inside each
series before it can support a cross-series edge.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "registry"
OUT = ROOT / "data" / "overlap"

GENERIC_PREFIXES = (
    "pr+nr breast cancer ",
    "pcr+npcr mamma breast cancer ",
    "breast cancer tumor ",
    "breast cancer ",
    "breastcancer_",
    "br_fna_",
    "br ca pt sample #",
)
ID_LABELS = {
    "sample id",
    "sample_id",
    "patient id",
    "patient_id",
    "subject id",
    "subject_id",
    "case id",
    "case_id",
    "patid",
    "centerid",
}


def compact(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"[^a-z0-9]+", "", value)


def title_core(title: str) -> str:
    value = unicodedata.normalize("NFKC", title).casefold().strip()
    for prefix in GENERIC_PREFIXES:
        if value.startswith(prefix):
            value = value[len(prefix) :]
            break
    return compact(value)


def source_identifier(source: str) -> str | None:
    # Require an explicit sample-ID cue; generic tissue descriptions are ignored.
    match = re.search(
        r"\bsample(?:\s+id)?\s*(?:--|#|:)?\s*([a-z0-9]+(?:[-_][a-z0-9]+)*)",
        unicodedata.normalize("NFKC", source).casefold(),
    )
    return compact(match.group(1)) if match else None


def aliases_for_sample(row: dict[str, str], characteristics: list[dict[str, str]]) -> list[tuple[str, str]]:
    gse = row["series_accession"]
    title_alias = title_core(row["sample_title"])
    source_alias = source_identifier(row["source_name_ch1"])
    aliases: list[tuple[str, str]] = []

    if title_alias:
        # In this deposited cohort, numeric GSE20271 titles are the M-series
        # identifiers used in GSE20194/GSE25055.  Other numeric titles are
        # namespaced from their explicit source field instead of guessed.
        if title_alias.isdigit() and gse == "GSE20271":
            aliases.append(("m" + title_alias, "study_aware_title"))
        elif title_alias.isdigit() and source_alias:
            aliases.append((source_alias, "source_namespaced_title"))
        elif not title_alias.isdigit():
            aliases.append((title_alias, "normalized_title"))

    if source_alias and not source_alias.isdigit():
        aliases.append((source_alias, "explicit_source_identifier"))

    for item in characteristics:
        label = compact(item["label"])
        if label not in {compact(x) for x in ID_LABELS}:
            continue
        value = compact(item["value"])
        if value and not value.isdigit():
            aliases.append((value, f"characteristic:{item['label']}"))

    # Short tokens are too collision-prone.  Keep provenance for distinct aliases.
    return sorted({(a, p) for a, p in aliases if len(a) >= 4})


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (REGISTRY / "seed_samples.csv").open(encoding="utf-8", newline="") as handle:
        samples = list(csv.DictReader(handle))
    with (REGISTRY / "sample_characteristics.csv").open(encoding="utf-8", newline="") as handle:
        characteristics = list(csv.DictReader(handle))

    chars_by_sample: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in characteristics:
        chars_by_sample[(row["series_accession"], row["sample_accession"])].append(row)

    alias_rows: list[dict[str, str]] = []
    for row in samples:
        key = (row["series_accession"], row["sample_accession"])
        for alias, provenance in aliases_for_sample(row, chars_by_sample[key]):
            alias_rows.append(
                {
                    "series_accession": row["series_accession"],
                    "sample_accession": row["sample_accession"],
                    "sample_title": row["sample_title"],
                    "alias": alias,
                    "alias_provenance": provenance,
                }
            )

    alias_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    series_alias_samples: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in alias_rows:
        alias_members[row["alias"]].append(row)
        series_alias_samples[(row["series_accession"], row["alias"])].add(row["sample_accession"])

    evidence: dict[tuple[str, str], dict[str, set[str]]] = {}
    ambiguous_aliases: list[dict[str, str | int]] = []
    for alias, members in alias_members.items():
        series = {m["series_accession"] for m in members}
        if len(series) < 2:
            continue
        if any(len(series_alias_samples[(gse, alias)]) != 1 for gse in series):
            ambiguous_aliases.append(
                {"alias": alias, "series_count": len(series), "sample_mentions": len(members)}
            )
            continue
        # Deduplicate the same sample reached through multiple provenance rows.
        unique = {(m["series_accession"], m["sample_accession"]): m for m in members}
        for left, right in combinations(sorted(unique.values(), key=lambda x: x["sample_accession"]), 2):
            if left["series_accession"] == right["series_accession"]:
                continue
            key = tuple(sorted((left["sample_accession"], right["sample_accession"])))
            record = evidence.setdefault(key, {"aliases": set(), "provenance": set()})
            record["aliases"].add(alias)
            record["provenance"].update((left["alias_provenance"], right["alias_provenance"]))

    by_gsm = {r["sample_accession"]: r for r in samples}
    edges: list[dict[str, str]] = []
    uf = UnionFind()
    for (a, b), info in sorted(evidence.items()):
        left, right = by_gsm[a], by_gsm[b]
        edges.append(
            {
                "sample_a": a,
                "series_a": left["series_accession"],
                "title_a": left["sample_title"],
                "sample_b": b,
                "series_b": right["series_accession"],
                "title_b": right["sample_title"],
                "shared_aliases": "|".join(sorted(info["aliases"])),
                "evidence": "|".join(sorted(info["provenance"])),
                "evidence_tier": "identifier_candidate",
            }
        )
        uf.union(a, b)

    components: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        for gsm in (edge["sample_a"], edge["sample_b"]):
            components[uf.find(gsm)].add(gsm)
    component_rows: list[dict[str, str | int]] = []
    for number, members in enumerate(
        sorted(components.values(), key=lambda x: (-len(x), sorted(x))), start=1
    ):
        component_id = f"IDG{number:04d}"
        series = sorted({by_gsm[g]["series_accession"] for g in members})
        for gsm in sorted(members):
            component_rows.append(
                {
                    "component_id": component_id,
                    "sample_accession": gsm,
                    "series_accession": by_gsm[gsm]["series_accession"],
                    "sample_title": by_gsm[gsm]["sample_title"],
                    "component_size": len(members),
                    "series_count": len(series),
                }
            )

    def write_csv(path: Path, rows: list[dict]) -> None:
        if not rows:
            return
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    write_csv(OUT / "sample_aliases.csv", alias_rows)
    write_csv(OUT / "identifier_edges.csv", edges)
    write_csv(OUT / "identity_components.csv", component_rows)
    write_csv(OUT / "ambiguous_aliases.csv", ambiguous_aliases)

    pair_counts: dict[str, int] = defaultdict(int)
    for edge in edges:
        pair = "--".join(sorted((edge["series_a"], edge["series_b"])))
        pair_counts[pair] += 1
    summary = {
        "samples": len(samples),
        "samples_with_alias": len({r["sample_accession"] for r in alias_rows}),
        "distinct_aliases": len(alias_members),
        "identifier_candidate_edges": len(edges),
        "identity_components": len(components),
        "samples_in_components": len({r["sample_accession"] for r in component_rows}),
        "ambiguous_cross_series_aliases": len(ambiguous_aliases),
        "pair_counts": dict(sorted(pair_counts.items())),
        "warning": "Identifier edges are candidates until corroborated by expression fingerprints or source documentation.",
    }
    (OUT / "identifier_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
