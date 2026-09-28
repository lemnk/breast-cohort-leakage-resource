"""Print a compact review dossier for each frozen manual-audit series pair."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "reports/validation/title_candidate_audit_sample.csv").open(encoding="utf-8")))
records = {x["accession"]: x for x in json.load((ROOT / "data/discovery_v2/geo_discovery_raw.json").open(encoding="utf-8"))["records"]}
headers = json.load((ROOT / "reports/validation/audit_sample_geo_headers.json").open(encoding="utf-8"))
groups = defaultdict(list)
for index, row in enumerate(rows, 1):
    groups[(row["series_a"], row["series_b"])].append((index, row))

def field(record, key):
    return "; ".join(record.get(key, []))[:220]

for (a, b), items in groups.items():
    ra, rb = records[a], records[b]
    publications = sorted(set(ra["pubmedids"]) & set(rb["pubmedids"]))
    row = items[0][1]
    fa = headers[row["sample_a"]]["fields"]
    fb = headers[row["sample_b"]]["fields"]
    print(f"PAIR {a} {b} n={len(items)} rows={[i for i, _ in items]}")
    print(f"PUBS {publications} PROJECTS {ra['bioproject']} / {rb['bioproject']}")
    print("A", ra["title"][:110])
    print("B", rb["title"][:110])
    print("EX", row["title_a"], "|", row["title_b"])
    print("SRC", field(fa, "Sample_source_name_ch1"), "|", field(fb, "Sample_source_name_ch1"))
    print("CHAR", field(fa, "Sample_characteristics_ch1"), "|", field(fb, "Sample_characteristics_ch1"))
    print("DESC", field(fa, "Sample_description"), "|", field(fb, "Sample_description"))
    print("COUNTRY", field(fa, "Sample_contact_country"), "|", field(fb, "Sample_contact_country"))
    print()
