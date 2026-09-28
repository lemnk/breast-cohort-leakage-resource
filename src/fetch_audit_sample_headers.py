"""Fetch GEO SOFT headers (not expression tables) for the frozen 100-link audit."""

from __future__ import annotations

import csv
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "reports" / "validation" / "title_candidate_audit_sample.csv"
OUTPUT = ROOT / "reports" / "validation" / "audit_sample_geo_headers.json"


def fetch(gsm: str) -> tuple[str, dict]:
    url = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gsm}&targ=self&form=text&view=full"
    request = urllib.request.Request(url, headers={"User-Agent": "breast-cohort-overlap-resource/2.0"})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            fields: dict[str, list[str]] = {}
            with urllib.request.urlopen(request, timeout=60) as response:
                for raw in response:
                    line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                    if line == "!sample_table_begin":
                        break
                    if line.startswith("!") and " = " in line:
                        key, value = line[1:].split(" = ", 1)
                        fields.setdefault(key, []).append(value)
            return gsm, {"url": url, "fields": fields}
        except Exception as exc:  # network retry only
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Unable to fetch {gsm}: {last_error}")


def main() -> None:
    with INPUT.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    accessions = sorted({r["sample_a"] for r in rows} | {r["sample_b"] for r in rows})
    output: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch, gsm): gsm for gsm in accessions}
        for number, future in enumerate(as_completed(futures), start=1):
            gsm, record = future.result()
            output[gsm] = record
            if number % 25 == 0:
                print(f"Fetched {number}/{len(accessions)}")
    OUTPUT.write_text(json.dumps(dict(sorted(output.items())), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(output)} GEO sample headers to {OUTPUT}")


if __name__ == "__main__":
    main()
