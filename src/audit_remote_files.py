"""Inventory remote GEO files without downloading their contents."""
from __future__ import annotations

import csv
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "discovery"


def series_bucket(accession: str) -> str:
    number = int(accession.removeprefix("GSE"))
    return f"GSE{number // 1000}nnn"


def list_files(url: str) -> list[tuple[str, int | None]]:
    req = urllib.request.Request(url, headers={"User-Agent": "breast-cohort-audit/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        html = response.read().decode("utf-8", errors="replace")
    names = sorted(set(re.findall(r'href="([^"?/]+)"', html)))
    results = []
    for name in names:
        if name in {"Name", "Last modified", "Size", "Description"}:
            continue
        target = url + name
        size = None
        try:
            head = urllib.request.Request(target, method="HEAD", headers={"User-Agent": "breast-cohort-audit/0.1"})
            with urllib.request.urlopen(head, timeout=30) as response:
                size = int(response.headers.get("Content-Length", "")) or None
        except Exception:
            pass
        results.append((target, size))
    return results


def main() -> None:
    config = json.loads((ROOT / "config" / "discovery_queries.json").read_text(encoding="utf-8"))
    rows = []
    for accession in config["mandatory_seed_accessions"]:
        base = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{series_bucket(accession)}/{accession}/"
        for category in ("matrix", "miniml", "suppl"):
            url = base + category + "/"
            try:
                files = list_files(url)
                status = "available"
            except Exception as exc:
                files = []
                status = f"unavailable: {type(exc).__name__}"
            if not files:
                rows.append({"accession": accession, "category": category, "url": url,
                             "bytes": "", "status": status})
            for file_url, size in files:
                rows.append({"accession": accession, "category": category, "url": file_url,
                             "bytes": size if size is not None else "", "status": status})
    output = OUT / "mandatory_seed_remote_files.csv"
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    known_bytes = sum(int(r["bytes"] or 0) for r in rows)
    print(json.dumps({"records": len(rows), "known_bytes": known_bytes,
                      "known_gib": round(known_bytes / 2**30, 3), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
