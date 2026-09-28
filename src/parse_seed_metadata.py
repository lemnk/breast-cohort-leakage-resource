"""Stream GEO series-matrix headers into a lossless sample registry.

The expression tables are deliberately not decompressed to disk.  GEO header
rows are aligned to ``!Sample_geo_accession`` and repeated fields (especially
characteristics) are retained as long-form records.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source" / "series_matrix"
OUT = ROOT / "data" / "registry"

SERIES_FIELDS = {
    "!Series_geo_accession",
    "!Series_title",
    "!Series_summary",
    "!Series_overall_design",
    "!Series_pubmed_id",
    "!Series_platform_id",
    "!Series_relation",
    "!Series_type",
}

SAMPLE_FIELDS = {
    "!Sample_title",
    "!Sample_geo_accession",
    "!Sample_status",
    "!Sample_submission_date",
    "!Sample_last_update_date",
    "!Sample_type",
    "!Sample_channel_count",
    "!Sample_source_name_ch1",
    "!Sample_organism_ch1",
    "!Sample_description",
    "!Sample_relation",
    "!Sample_platform_id",
}


def parse_row(line: str) -> list[str]:
    return next(csv.reader([line.rstrip("\r\n")], delimiter="\t", quotechar='"'))


def parse_matrix(path: Path) -> tuple[dict[str, list[str]], dict[str, list[list[str]]]]:
    series: dict[str, list[str]] = defaultdict(list)
    sample_rows: dict[str, list[list[str]]] = defaultdict(list)
    with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                break
            if not line.startswith("!"):
                continue
            row = parse_row(line)
            key, values = row[0], row[1:]
            if key in SERIES_FIELDS:
                series[key].extend(values)
            elif key in SAMPLE_FIELDS or key.startswith("!Sample_characteristics_ch"):
                sample_rows[key].append(values)
    return dict(series), dict(sample_rows)


def join(values: list[str]) -> str:
    return " | ".join(v for v in values if v)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    series_out: list[dict[str, str | int]] = []
    samples_out: list[dict[str, str | int]] = []
    characteristics_out: list[dict[str, str | int]] = []
    descriptions_out: list[dict[str, str | int]] = []

    for path in sorted(SOURCE.glob("GSE*_series_matrix.txt.gz")):
        series, sample_rows = parse_matrix(path)
        accessions_rows = sample_rows.get("!Sample_geo_accession", [])
        if len(accessions_rows) != 1:
            raise ValueError(f"{path.name}: expected one sample accession row, got {len(accessions_rows)}")
        accessions = accessions_rows[0]
        n = len(accessions)

        for key, rows in sample_rows.items():
            for row_index, values in enumerate(rows, start=1):
                if len(values) != n:
                    raise ValueError(
                        f"{path.name}: {key} row {row_index} has {len(values)} values; expected {n}"
                    )

        gse = (series.get("!Series_geo_accession") or [path.name.split("_")[0]])[0]
        series_out.append(
            {
                "series_accession": gse,
                "title": join(series.get("!Series_title", [])),
                "summary": join(series.get("!Series_summary", [])),
                "overall_design": join(series.get("!Series_overall_design", [])),
                "pubmed_ids": join(series.get("!Series_pubmed_id", [])),
                "platform_ids": join(series.get("!Series_platform_id", [])),
                "relations": join(series.get("!Series_relation", [])),
                "series_types": join(series.get("!Series_type", [])),
                "sample_count": n,
                "source_file": path.name,
            }
        )

        scalar_rows = {}
        for key in SAMPLE_FIELDS:
            rows = sample_rows.get(key, [])
            scalar_rows[key] = rows[0] if rows else [""] * n
            for extra_index, values in enumerate(rows[1:], start=2):
                for i, value in enumerate(values):
                    if value:
                        descriptions_out.append(
                            {
                                "series_accession": gse,
                                "sample_accession": accessions[i],
                                "field": key.removeprefix("!Sample_"),
                                "row_index": extra_index,
                                "value": value,
                            }
                        )

        for i, gsm in enumerate(accessions):
            samples_out.append(
                {
                    "series_accession": gse,
                    "sample_accession": gsm,
                    "sample_title": scalar_rows["!Sample_title"][i],
                    "source_name_ch1": scalar_rows["!Sample_source_name_ch1"][i],
                    "organism_ch1": scalar_rows["!Sample_organism_ch1"][i],
                    "platform_id": scalar_rows["!Sample_platform_id"][i],
                    "description": scalar_rows["!Sample_description"][i],
                    "sample_relations": scalar_rows["!Sample_relation"][i],
                    "status": scalar_rows["!Sample_status"][i],
                    "submission_date": scalar_rows["!Sample_submission_date"][i],
                    "last_update_date": scalar_rows["!Sample_last_update_date"][i],
                }
            )

        for field, rows in sample_rows.items():
            if not field.startswith("!Sample_characteristics_ch"):
                continue
            for row_index, values in enumerate(rows, start=1):
                for i, raw in enumerate(values):
                    label, value = "", raw
                    if ":" in raw:
                        label, value = raw.split(":", 1)
                    characteristics_out.append(
                        {
                            "series_accession": gse,
                            "sample_accession": accessions[i],
                            "channel_field": field.removeprefix("!Sample_"),
                            "row_index": row_index,
                            "label": label.strip(),
                            "value": value.strip(),
                            "raw_value": raw,
                        }
                    )

    def write_csv(name: str, rows: list[dict]) -> None:
        if not rows:
            return
        with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    write_csv("seed_series.csv", series_out)
    write_csv("seed_samples.csv", samples_out)
    write_csv("sample_characteristics.csv", characteristics_out)
    write_csv("additional_sample_fields.csv", descriptions_out)
    summary = {
        "series": len(series_out),
        "samples": len(samples_out),
        "characteristic_values": len(characteristics_out),
        "additional_repeated_values": len(descriptions_out),
    }
    (OUT / "registry_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
