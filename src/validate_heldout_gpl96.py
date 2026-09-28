"""Apply frozen fingerprint rules to the held-out GPL96-to-GPL570 pair."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from validate_expression_fingerprints import load_fingerprints, percentile, probe_ids


ROOT = Path(__file__).resolve().parents[1]
HELDOUT = ROOT / "data" / "heldout"
MATRICES = HELDOUT / "series_matrix"
SEED = "breast-cohort-leakage-resource-v1"
N_PROBES = 2048
SERIES_A = "GSE16795"
SERIES_B = "GSE21217"
PATHS = {
    SERIES_A: MATRICES / "GSE16795_series_matrix.txt.gz",
    SERIES_B: MATRICES / "GSE21217-GPL570_series_matrix.txt.gz",
}


def classify(rho: float, rank_a: int, rank_b: int, null99: float) -> str:
    margin = rho - null99
    if (rho >= 0.98 and margin >= 0.02) or (rank_a == 1 and rank_b == 1):
        return "confirmed"
    if (rank_a <= 3 and rank_b <= 3) or (rho >= 0.95 and margin >= 0.01):
        return "supported"
    return "not_corroborated"


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    common = probe_ids(PATHS[SERIES_A]) & probe_ids(PATHS[SERIES_B])
    ordered = sorted(common, key=lambda p: hashlib.sha256(f"{SEED}:{p}".encode()).hexdigest())
    chosen = ordered[: min(N_PROBES, len(ordered))]
    selected = set(chosen)
    samples_a, ranks_a = load_fingerprints(PATHS[SERIES_A], selected)
    samples_b, ranks_b = load_fingerprints(PATHS[SERIES_B], selected)
    index_a = {gsm: i for i, gsm in enumerate(samples_a)}
    index_b = {gsm: i for i, gsm in enumerate(samples_b)}

    left = ranks_a.astype(np.float64)
    right = ranks_b.astype(np.float64)
    left -= left.mean(axis=0, keepdims=True)
    right -= right.mean(axis=0, keepdims=True)
    left /= np.sqrt((left * left).sum(axis=0, keepdims=True))
    right /= np.sqrt((right * right).sum(axis=0, keepdims=True))
    matrix = left.T @ right

    with (ROOT / "data" / "comprehensive" / "specific_title_alias_links.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        candidates = [
            r
            for r in csv.DictReader(handle)
            if r["series_a"] == SERIES_A and r["series_b"] == SERIES_B
        ]
    known = {(r["sample_a"], r["sample_b"]) for r in candidates}

    results: list[dict] = []
    controls: list[dict] = []
    for candidate_number, row in enumerate(candidates, start=1):
        a, b = row["sample_a"], row["sample_b"]
        i, j = index_a[a], index_b[b]
        rank_a = int((-matrix[i, :]).argsort(kind="stable").tolist().index(j) + 1)
        rank_b = int((-matrix[:, j]).argsort(kind="stable").tolist().index(i) + 1)
        result = {
            **row,
            "spearman_rho": float(matrix[i, j]),
            "rank_a_to_b": rank_a,
            "rank_b_to_a": rank_b,
            "reciprocal_top1": rank_a == 1 and rank_b == 1,
        }
        results.append(result)

        digest = hashlib.sha256(f"{SEED}:{a}:{b}".encode()).digest()
        start = int.from_bytes(digest[:8], "big") % len(samples_b)
        added = 0
        offset = 0
        while added < 5 and offset < len(samples_b) * 2:
            control_b = samples_b[(start + offset) % len(samples_b)]
            offset += 1
            if control_b == b or (a, control_b) in known:
                continue
            control_j = index_b[control_b]
            control_rank_a = int(
                (-matrix[i, :]).argsort(kind="stable").tolist().index(control_j) + 1
            )
            control_rank_b = int(
                (-matrix[:, control_j]).argsort(kind="stable").tolist().index(i) + 1
            )
            controls.append(
                {
                    "candidate_number": candidate_number,
                    "sample_a": a,
                    "sample_b_control": control_b,
                    "control_number": added + 1,
                    "spearman_rho": float(matrix[i, control_j]),
                    "rank_a_to_b": control_rank_a,
                    "rank_b_to_a": control_rank_b,
                    "reciprocal_top1": control_rank_a == 1 and control_rank_b == 1,
                }
            )
            added += 1

    null99 = percentile([float(r["spearman_rho"]) for r in controls], 0.99)
    for row in results:
        row["pair_null_p99"] = null99
        row["margin_above_null_p99"] = float(row["spearman_rho"]) - null99
        row["expression_evidence"] = classify(
            float(row["spearman_rho"]), int(row["rank_a_to_b"]), int(row["rank_b_to_a"]), null99
        )
    for row in controls:
        row["pair_null_p99"] = null99
        row["margin_above_null_p99"] = float(row["spearman_rho"]) - null99
        row["expression_rule_result"] = classify(
            float(row["spearman_rho"]), int(row["rank_a_to_b"]), int(row["rank_b_to_a"]), null99
        )

    HELDOUT.mkdir(parents=True, exist_ok=True)
    write_csv(HELDOUT / "heldout_crossplatform_candidates.csv", results)
    write_csv(HELDOUT / "heldout_crossplatform_controls.csv", controls)
    (HELDOUT / "heldout_crossplatform_probe_ids.txt").write_text(
        "\n".join(chosen) + "\n", encoding="utf-8"
    )
    evidence_counts = {k: sum(r["expression_evidence"] == k for r in results) for k in ("confirmed", "supported", "not_corroborated")}
    control_counts = {k: sum(r["expression_rule_result"] == k for r in controls) for k in ("confirmed", "supported", "not_corroborated")}
    summary = {
        "selection_status": "metadata-selected and protocol-frozen before expression download",
        "series_pair": f"{SERIES_A}--{SERIES_B}",
        "platform_pair": "GPL96--GPL570",
        "biological_material": "breast cancer cell lines; not patient specimens",
        "candidate_n": len(results),
        "control_n": len(controls),
        "common_probe_count": len(common),
        "fingerprint_probe_count": len(chosen),
        "selection_seed": SEED,
        "control_p99": null99,
        "evidence_counts": evidence_counts,
        "control_rule_counts": control_counts,
        "candidate_results": results,
        "interpretation": "Held-out GPL96-to-GPL570 cell-line transport check; no patient-level or RNA-seq accuracy inference.",
    }
    (HELDOUT / "heldout_crossplatform_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
