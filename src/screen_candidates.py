"""Create a conservative human-review queue from broad GEO discovery results."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = ROOT / "data" / "discovery"


def main() -> None:
    config = json.loads((ROOT / "config" / "discovery_queries.json").read_text(encoding="utf-8"))
    raw = json.loads((DISCOVERY / "geo_discovery_raw.json").read_text(encoding="utf-8"))
    seeds = set(config["mandatory_seed_accessions"])
    rows = []
    for record in raw["records"]:
        accession = record.get("accession", "")
        title = str(record.get("title", ""))
        summary = str(record.get("summary", ""))
        text = f"{title} {summary}".lower()
        dtype = str(record.get("gdstype", ""))
        n = int(record.get("n_samples") or 0)
        expression = dtype.startswith("Expression profiling")
        treatment_response = any(x in text for x in (
            "neoadjuvant", "pathologic complete response", "pathological complete response",
            "chemotherapy response", "response to chemotherapy", "predict response",
        ))
        patient_context = any(x in text for x in (
            "patient", "clinical trial", "tumor sample", "tumour sample", "biopsy",
            "breast cancer cohort", "primary breast cancer", "breast tumors", "breast tumours",
        ))
        nonpatient = any(x in text for x in (
            "cell line", "cell lines", "xenograft", "pdx", "organoid", "mouse model",
            "mice", "murine", "mammary epithelial cells",
        ))
        reasons = []
        if accession in seeds:
            status = "mandatory_seed_review"
            reasons.append("known or suspected source/derivative relationship")
        elif expression and n >= 10 and treatment_response and patient_context and not nonpatient:
            status = "priority_review"
            reasons.extend(["human expression series", "response context", "patient/tumor context"])
        elif expression and n >= 10 and treatment_response and not nonpatient:
            status = "secondary_review"
            reasons.extend(["human expression series", "response context", "patient context unclear"])
        else:
            status = "screen_out"
            if not expression: reasons.append("not expression profiling")
            if n < 10: reasons.append("fewer than 10 deposited samples")
            if not treatment_response: reasons.append("no explicit neoadjuvant/response context")
            if nonpatient: reasons.append("cell-line/model-system indication")
        rows.append({
            "accession": accession,
            "screen_status": status,
            "n_samples": n,
            "platforms": f"GPL{record.get('gpl', '')}" if record.get("gpl") else "",
            "data_type": dtype,
            "title": title,
            "pubmed_ids": ";".join(str(x) for x in record.get("pubmedids", [])),
            "supplementary_file_types": record.get("suppfile", ""),
            "screen_reasons": "; ".join(reasons),
            "geo_url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}",
        })
    order = {"mandatory_seed_review": 0, "priority_review": 1, "secondary_review": 2, "screen_out": 3}
    rows.sort(key=lambda x: (order[x["screen_status"]], -x["n_samples"], x["accession"]))
    output = DISCOVERY / "geo_screening_queue.csv"
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    counts = {key: sum(r["screen_status"] == key for r in rows) for key in order}
    samples = {key: sum(r["n_samples"] for r in rows if r["screen_status"] == key) for key in order}
    result = {"counts": counts, "deposited_samples": samples, "output": str(output)}
    (DISCOVERY / "screening_summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
