"""Corroborate identifier links with label-independent expression fingerprints.

For the GPL96 Hatzis-family series, this script selects 2,048 probes by a
fixed cryptographic ordering from the common probe intersection.  It compares
within-sample probe ranks, which are insensitive to monotone rescaling between
deposited matrices.  Deterministic nonmatched pairs provide an empirical null.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source" / "series_matrix"
OVERLAP = ROOT / "data" / "overlap"
SEED = "breast-cohort-leakage-resource-v1"
N_PROBES = 2048


def matrix_path(gse: str) -> Path:
    return SOURCE / f"{gse}_series_matrix.txt.gz"


def table_rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
        in_table = False
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                return
            if in_table:
                yield next(csv.reader([line.rstrip("\r\n")], delimiter="\t", quotechar='"'))


def probe_ids(path: Path) -> set[str]:
    rows = table_rows(path)
    next(rows)  # ID_REF plus GSM accessions
    return {row[0] for row in rows if row}


def rank_columns(values: np.ndarray) -> np.ndarray:
    """Ordinal ranks are sufficient because exact ties are uncommon here."""
    order = np.argsort(values, axis=0, kind="stable")
    ranks = np.empty_like(order, dtype=np.int16)
    columns = np.arange(values.shape[1])
    ranks[order, columns] = np.arange(values.shape[0], dtype=np.int16)[:, None]
    return ranks


def load_fingerprints(path: Path, selected: set[str]) -> tuple[list[str], np.ndarray]:
    rows = table_rows(path)
    header = next(rows)
    samples = header[1:]
    selected_rows: dict[str, list[float]] = {}
    for row in rows:
        if row and row[0] in selected:
            try:
                selected_rows[row[0]] = [float(x) for x in row[1:]]
            except ValueError as exc:
                raise ValueError(f"Non-numeric selected row {row[0]} in {path.name}") from exc
    missing = selected - selected_rows.keys()
    if missing:
        raise ValueError(f"{path.name}: {len(missing)} selected probes missing")
    values = np.asarray([selected_rows[p] for p in sorted(selected)], dtype=np.float32)
    return samples, rank_columns(values)


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    af = a.astype(np.float64)
    bf = b.astype(np.float64)
    af -= af.mean()
    bf -= bf.mean()
    denominator = np.sqrt(np.dot(af, af) * np.dot(bf, bf))
    return float(np.dot(af, bf) / denominator) if denominator else float("nan")


def percentile(values: list[float], q: float) -> float:
    return float(np.quantile(np.asarray(values), q)) if values else float("nan")


def main() -> None:
    with (OVERLAP / "identifier_edges.csv").open(encoding="utf-8", newline="") as handle:
        edges = list(csv.DictReader(handle))
    series = sorted({e["series_a"] for e in edges} | {e["series_b"] for e in edges})

    common: set[str] | None = None
    for gse in series:
        probes = probe_ids(matrix_path(gse))
        common = probes if common is None else common & probes
    assert common is not None
    ordered = sorted(common, key=lambda p: hashlib.sha256(f"{SEED}:{p}".encode()).hexdigest())
    chosen = ordered[: min(N_PROBES, len(ordered))]
    selected = set(chosen)

    fingerprints: dict[str, np.ndarray] = {}
    samples_by_series: dict[str, list[str]] = {}
    ranks_by_series: dict[str, np.ndarray] = {}
    for gse in series:
        samples, ranks = load_fingerprints(matrix_path(gse), selected)
        samples_by_series[gse] = samples
        ranks_by_series[gse] = ranks
        for index, gsm in enumerate(samples):
            fingerprints[gsm] = ranks[:, index]

    sample_index = {gse: {gsm: i for i, gsm in enumerate(gsms)} for gse, gsms in samples_by_series.items()}
    correlation_matrices: dict[tuple[str, str], np.ndarray] = {}
    for edge in edges:
        key = (edge["series_a"], edge["series_b"])
        if key in correlation_matrices:
            continue
        left = ranks_by_series[key[0]].astype(np.float64)
        right = ranks_by_series[key[1]].astype(np.float64)
        left -= left.mean(axis=0, keepdims=True)
        right -= right.mean(axis=0, keepdims=True)
        left /= np.sqrt((left * left).sum(axis=0, keepdims=True))
        right /= np.sqrt((right * right).sum(axis=0, keepdims=True))
        correlation_matrices[key] = left.T @ right

    known_pairs = {frozenset((e["sample_a"], e["sample_b"])) for e in edges}
    positives: list[dict[str, str | float]] = []
    controls: list[dict[str, str | float | int]] = []
    controls_by_pair: dict[str, list[float]] = defaultdict(list)
    for edge_index, edge in enumerate(edges):
        a, b = edge["sample_a"], edge["sample_b"]
        pair = "--".join(sorted((edge["series_a"], edge["series_b"])))
        matrix = correlation_matrices[(edge["series_a"], edge["series_b"])]
        i = sample_index[edge["series_a"]][a]
        j = sample_index[edge["series_b"]][b]
        rho = float(matrix[i, j])
        rank_a_to_b = int((-matrix[i, :]).argsort(kind="stable").tolist().index(j) + 1)
        rank_b_to_a = int((-matrix[:, j]).argsort(kind="stable").tolist().index(i) + 1)
        positives.append(
            {
                **edge,
                "spearman_rho": rho,
                "rank_a_to_b": rank_a_to_b,
                "rank_b_to_a": rank_b_to_a,
                "reciprocal_top1": rank_a_to_b == 1 and rank_b_to_a == 1,
            }
        )

        # Five deterministic, nonlinked samples from series B for each candidate.
        pool = samples_by_series[edge["series_b"]]
        digest = hashlib.sha256(f"{SEED}:{a}:{b}".encode()).digest()
        start = int.from_bytes(digest[:8], "big") % len(pool)
        added = 0
        offset = 0
        while added < min(5, max(0, len(pool) - 1)) and offset < len(pool) * 2:
            control_b = pool[(start + offset) % len(pool)]
            offset += 1
            if control_b == b or frozenset((a, control_b)) in known_pairs:
                continue
            control_j = sample_index[edge["series_b"]][control_b]
            control_rho = float(matrix[i, control_j])
            control_rank_a_to_b = int(
                (-matrix[i, :]).argsort(kind="stable").tolist().index(control_j) + 1
            )
            control_rank_b_to_a = int(
                (-matrix[:, control_j]).argsort(kind="stable").tolist().index(i) + 1
            )
            controls.append(
                {
                    "candidate_edge_index": edge_index,
                    "series_pair": pair,
                    "sample_a": a,
                    "sample_b_control": control_b,
                    "control_number": added + 1,
                    "spearman_rho": control_rho,
                    "rank_a_to_b": control_rank_a_to_b,
                    "rank_b_to_a": control_rank_b_to_a,
                    "reciprocal_top1": control_rank_a_to_b == 1 and control_rank_b_to_a == 1,
                }
            )
            controls_by_pair[pair].append(control_rho)
            added += 1

    for row in positives:
        pair = "--".join(sorted((str(row["series_a"]), str(row["series_b"]))))
        null99 = percentile(controls_by_pair[pair], 0.99)
        rho = float(row["spearman_rho"])
        margin = rho - null99
        row["pair_null_p99"] = null99
        row["margin_above_null_p99"] = margin
        reciprocal_top1 = str(row["reciprocal_top1"]).lower() == "true"
        ranks_within_three = int(row["rank_a_to_b"]) <= 3 and int(row["rank_b_to_a"]) <= 3
        if (rho >= 0.98 and margin >= 0.02) or reciprocal_top1:
            row["expression_evidence"] = "confirmed"
        elif ranks_within_three or (rho >= 0.95 and margin >= 0.01):
            row["expression_evidence"] = "supported"
        else:
            row["expression_evidence"] = "not_corroborated"

    # Apply the exact same predeclared rules to the deterministic nonlinked
    # controls.  This is an empirical rule-exceedance calculation, not an
    # independent false-discovery estimate: the controls are presumed
    # nonmatches and the rules were developed in this same seed family.
    for row in controls:
        null99 = percentile(controls_by_pair[str(row["series_pair"])], 0.99)
        rho = float(row["spearman_rho"])
        margin = rho - null99
        row["pair_null_p99"] = null99
        row["margin_above_null_p99"] = margin
        reciprocal_top1 = bool(row["reciprocal_top1"])
        ranks_within_three = int(row["rank_a_to_b"]) <= 3 and int(row["rank_b_to_a"]) <= 3
        if (rho >= 0.98 and margin >= 0.02) or reciprocal_top1:
            row["expression_rule_result"] = "confirmed"
        elif ranks_within_three or (rho >= 0.95 and margin >= 0.01):
            row["expression_rule_result"] = "supported"
        else:
            row["expression_rule_result"] = "not_corroborated"

    def write_csv(path: Path, rows: list[dict]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    write_csv(OVERLAP / "expression_validated_edges.csv", positives)
    write_csv(OVERLAP / "expression_negative_controls.csv", controls)
    (OVERLAP / "fingerprint_probe_ids.txt").write_text("\n".join(chosen) + "\n", encoding="utf-8")

    positive_values = [float(x["spearman_rho"]) for x in positives]
    negative_values = [float(x["spearman_rho"]) for x in controls]
    status_counts = defaultdict(int)
    for row in positives:
        status_counts[str(row["expression_evidence"])] += 1
    control_status_counts = defaultdict(int)
    for row in controls:
        control_status_counts[str(row["expression_rule_result"])] += 1
    control_confirmed = control_status_counts["confirmed"]
    control_confirmed_rate = control_confirmed / len(controls)
    # The rule-of-three term is a transparent approximate upper calibration
    # bound for rare control confirmations rather than a formal adjusted CI.
    control_confirmed_upper = (control_confirmed + 3) / len(controls)
    pair_summary = {}
    for pair in sorted(controls_by_pair):
        p = [float(r["spearman_rho"]) for r in positives if "--".join(sorted((str(r["series_a"]), str(r["series_b"])))) == pair]
        n = controls_by_pair[pair]
        pair_summary[pair] = {
            "candidate_n": len(p),
            "candidate_median": float(np.median(p)),
            "control_n": len(n),
            "control_median": float(np.median(n)),
            "control_p99": percentile(n, 0.99),
        }
    summary = {
        "series": series,
        "common_probe_count": len(common),
        "fingerprint_probe_count": len(chosen),
        "selection_seed": SEED,
        "candidate_edges": len(positives),
        "negative_controls": len(controls),
        "candidate_median_rho": float(np.median(positive_values)),
        "candidate_min_rho": min(positive_values),
        "control_median_rho": float(np.median(negative_values)),
        "control_p99_rho": percentile(negative_values, 0.99),
        "evidence_counts": dict(sorted(status_counts.items())),
        "control_rule_counts": dict(sorted(control_status_counts.items())),
        "empirical_control_confirmed_rate": control_confirmed_rate,
        "heuristic_control_confirmed_rate_upper_bound": control_confirmed_upper,
        "expected_confirmed_controls_per_385_at_observed_rate": control_confirmed_rate * 385,
        "expected_confirmed_controls_per_385_at_heuristic_upper_bound": control_confirmed_upper * 385,
        "pair_summary": pair_summary,
        "interpretation": "Expression evidence corroborates identifier candidates; it does not independently prove patient identity. Control rule exceedance is an internal empirical calibration, not a multiplicity-adjusted external false-discovery estimate.",
    }
    (OVERLAP / "expression_validation_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
