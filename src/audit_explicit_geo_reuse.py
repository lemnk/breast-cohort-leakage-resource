"""Audit explicit GEO reanalysis and cross-series GSM references."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "discovery_v2" / "geo_discovery_raw.json"
OUT = ROOT / "reports" / "validation"
CSV_OUT = OUT / "explicit_geo_reuse_relationships.csv"
JSON_OUT = OUT / "explicit_geo_reuse_summary.json"
TEXT_FIELDS = ("title", "summary", "ssinfo", "subsetinfo", "pdat")


def main() -> None:
    records = json.loads(INPUT.read_text(encoding="utf-8"))["records"]
    by_accession = {row["accession"]: row for row in records}
    gsm_owners: dict[str, list[str]] = defaultdict(list)
    for record in records:
        for sample in record.get("samples", []):
            gsm_owners[sample["accession"]].append(record["accession"])

    third_party = [
        record["accession"]
        for record in records
        if "Third-party reanalysis" in record.get("gdstype", "")
    ]
    rows: list[dict[str, object]] = []
    explicit_references = 0
    own_references = 0
    unmapped_references = 0

    for record in records:
        text = " ".join(str(record.get(field, "")) for field in TEXT_FIELDS)
        own_samples = {sample["accession"] for sample in record.get("samples", [])}
        for gsm in sorted(set(re.findall(r"\bGSM\d+\b", text, flags=re.IGNORECASE))):
            gsm = gsm.upper()
            explicit_references += 1
            if gsm in own_samples:
                own_references += 1
                continue
            owners = [owner for owner in gsm_owners.get(gsm, []) if owner != record["accession"]]
            if not owners:
                unmapped_references += 1
                continue
            use_context = (
                "explicit normalization data reuse"
                if re.search(r"normali[sz]", text, flags=re.IGNORECASE)
                else "explicit series-level GSM reference"
            )
            for owner in owners:
                rows.append(
                    {
                        "source_series": record["accession"],
                        "referenced_gsm": gsm,
                        "referenced_series": owner,
                        "relationship_type": use_context,
                        "source_series_title": record.get("title", ""),
                        "referenced_series_title": by_accession[owner].get("title", ""),
                        "source_geo_url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={record['accession']}",
                        "referenced_gsm_url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gsm}",
                        "referenced_series_url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={owner}",
                    }
                )

    OUT.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else [
        "source_series", "referenced_gsm", "referenced_series", "relationship_type",
        "source_series_title", "referenced_series_title", "source_geo_url",
        "referenced_gsm_url", "referenced_series_url",
    ]
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    pair_counts = Counter((row["source_series"], row["referenced_series"]) for row in rows)
    summary = {
        "query_defined_series": len(records),
        "third_party_reanalysis_series": len(third_party),
        "third_party_reanalysis_accessions": sorted(third_party),
        "series_level_unique_gsm_references": explicit_references,
        "references_to_own_series_samples": own_references,
        "references_not_mapped_inside_query_universe": unmapped_references,
        "cross_series_referenced_gsms_mapped_inside_query_universe": len(rows),
        "explicit_cross_series_relationships": len(pair_counts),
        "pair_counts": {f"{a}--{b}": count for (a, b), count in sorted(pair_counts.items())},
        "interpretation": (
            "These are explicit data-use or reanalysis relationships stated in GEO metadata. "
            "They do not by themselves establish shared patients or physical specimens and are "
            "kept separate from the overlap evidence tiers."
        ),
    }
    JSON_OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
