"""Describe platform coverage and the scope of expression validation."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "discovery_v2" / "geo_discovery_raw.json"
OUT = ROOT / "reports" / "validation" / "platform_coverage.json"


def main() -> None:
    records = json.loads(RAW.read_text(encoding="utf-8"))["records"]
    types = Counter(r.get("gdstype", "unknown") for r in records)
    platform_series = Counter()
    platform_samples = Counter()
    for record in records:
        platforms = [f"GPL{x}" for x in str(record.get("gpl", "")).split(";") if x]
        for platform in platforms:
            platform_series[platform] += 1
            platform_samples[platform] += int(record.get("n_samples") or 0)
    gpl96_series = platform_series["GPL96"]
    summary = {
        "total_series": len(records),
        "data_types": dict(types.most_common()),
        "unique_platform_ids": len(platform_series),
        "top_platforms_by_series": [
            {"platform": p, "series": n, "deposited_samples": platform_samples[p]}
            for p, n in platform_series.most_common(20)
        ],
        "gpl96_series_in_universe": gpl96_series,
        "gpl96_series_fraction": gpl96_series / len(records),
        "expression_validation_series": 7,
        "expression_validation_fraction_of_universe": 7 / len(records),
        "scope_warning": "Expression-rule validation is confined to seven GPL96 series and does not establish RNA-seq or cross-platform accuracy.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
