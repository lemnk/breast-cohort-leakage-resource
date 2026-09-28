"""Retrieve a comprehensive metadata-only breast cancer expression universe."""

from __future__ import annotations

import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "comprehensive_discovery.json"
OUT = ROOT / "data" / "discovery_v2"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def get_json(endpoint: str, params: dict[str, object]) -> dict:
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "breast-cohort-overlap-resource/0.2"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    search = get_json(
        "esearch.fcgi",
        {
            "db": config["database"],
            "term": config["query"],
            "retmax": config["retrieval_limit"],
            "retmode": "json",
        },
    )["esearchresult"]
    expected = int(search["count"])
    ids = search["idlist"]
    if len(ids) != expected:
        raise RuntimeError(f"Retrieved {len(ids)} IDs but query reported {expected}")

    records: list[dict] = []
    for start in range(0, len(ids), 100):
        result = get_json(
            "esummary.fcgi",
            {"db": config["database"], "id": ",".join(ids[start : start + 100]), "retmode": "json"},
        )["result"]
        records.extend(result[uid] for uid in result.get("uids", []))
        if start and start % 1000 == 0:
            print(f"Retrieved {start:,}/{len(ids):,} summaries", flush=True)
        time.sleep(0.36)

    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": config,
        "query_count": expected,
        "records": records,
    }
    (OUT / "geo_discovery_raw.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    rows = [
        {
            "accession": r.get("accession", ""),
            "title": r.get("title", ""),
            "data_type": r.get("gdstype", ""),
            "n_samples": r.get("n_samples", ""),
            "platforms": r.get("gpl", ""),
            "publication_date": r.get("pdat", ""),
            "pubmed_ids": ";".join(r.get("pubmedids", [])),
        }
        for r in records
    ]
    with (OUT / "series_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda x: x["accession"]))
    print(json.dumps({"series": len(records), "sample_mentions": sum(len(r.get("samples", [])) for r in records)}, indent=2))


if __name__ == "__main__":
    main()
