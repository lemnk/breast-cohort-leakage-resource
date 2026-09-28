"""Reproducible, metadata-only discovery of candidate GEO breast-cancer series."""
from __future__ import annotations

import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "discovery_queries.json"
OUT = ROOT / "data" / "discovery"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def get_json(endpoint: str, params: dict[str, object]) -> dict:
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "breast-cohort-audit/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def search(term: str, limit: int) -> list[str]:
    payload = get_json("esearch.fcgi", {
        "db": "gds", "term": term, "retmax": limit, "retmode": "json"
    })
    return payload["esearchresult"]["idlist"]


def summaries(ids: list[str]) -> list[dict]:
    rows: list[dict] = []
    for start in range(0, len(ids), 100):
        batch = ids[start:start + 100]
        payload = get_json("esummary.fcgi", {
            "db": "gds", "id": ",".join(batch), "retmode": "json"
        })["result"]
        for uid in payload.get("uids", []):
            rows.append(payload[uid])
        time.sleep(0.4)
    return rows


def relevance(row: dict) -> tuple[bool, list[str]]:
    text = " ".join(str(row.get(k, "")) for k in ("title", "summary", "gdstype")).lower()
    reasons = []
    for needle, label in (
        ("neoadjuvant", "neoadjuvant"),
        ("pathologic complete response", "pCR"),
        ("pathological complete response", "pCR"),
        ("chemotherapy", "chemotherapy"),
        ("treatment response", "treatment response"),
        ("gene expression", "gene expression"),
        ("transcript", "transcriptomic"),
    ):
        if needle in text and label not in reasons:
            reasons.append(label)
    human = str(row.get("taxon", "")).lower() == "homo sapiens"
    series = row.get("entrytype") == "GSE"
    breast = "breast" in text
    response_context = bool({"neoadjuvant", "pCR", "treatment response"} & set(reasons))
    return human and series and breast and response_context, reasons


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    query_hits: dict[str, list[str]] = {}
    all_ids: set[str] = set()
    for term in config["queries"]:
        ids = search(term, int(config["retrieval_limit_per_query"]))
        query_hits[term] = ids
        all_ids.update(ids)
        time.sleep(0.4)

    records = summaries(sorted(all_ids))
    rows = []
    for record in records:
        keep, reasons = relevance(record)
        rows.append({
            "accession": record.get("accession", ""),
            "title": record.get("title", ""),
            "organism": record.get("taxon", ""),
            "platform": f"GPL{record.get('gpl', '')}" if record.get("gpl") else "",
            "data_type": record.get("gdstype", ""),
            "n_samples": record.get("n_samples", ""),
            "publication_date": record.get("pdat", ""),
            "pubmed_ids": ";".join(str(x) for x in record.get("pubmedids", [])),
            "supplementary_file_types": record.get("suppfile", ""),
            "ftp": record.get("ftplink", ""),
            "candidate": keep,
            "relevance_reasons": ";".join(reasons),
        })
    rows.sort(key=lambda x: (not x["candidate"], x["accession"]))

    OUT.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with (OUT / "geo_candidates.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "geo_discovery_raw.json").write_text(
        json.dumps({"config": config, "query_hits": query_hits, "records": records}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "unique_geo_records": len(rows),
        "candidate_series": sum(bool(r["candidate"]) for r in rows),
        "candidate_samples": sum(int(r["n_samples"] or 0) for r in rows if r["candidate"]),
        "output": str(OUT / "geo_candidates.csv"),
    }, indent=2))


if __name__ == "__main__":
    main()
