"""Create release-3 expression tables with corrected, non-identity labels."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "overlap"
OUTPUT = ROOT / "data" / "overlap_v3"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    candidates = read_csv(SOURCE / "expression_validated_edges.csv")
    controls = read_csv(SOURCE / "expression_negative_controls.csv")

    candidate_map = {
        "confirmed": "corroborated_candidate",
        "supported": "supported_candidate",
        "not_corroborated": "not_corroborated",
    }
    control_map = {
        "confirmed": "strong_rule_exceeded",
        "supported": "weaker_rule_exceeded",
        "not_corroborated": "neither_rule_exceeded",
    }
    for row in candidates:
        row["legacy_release2_label"] = row.pop("expression_evidence")
        row["expression_candidate_result"] = candidate_map[row["legacy_release2_label"]]
    for row in controls:
        row["legacy_release2_label"] = row.pop("expression_rule_result")
        row["control_rule_result"] = control_map[row["legacy_release2_label"]]

    write_csv(OUTPUT / "expression_candidate_results.csv", candidates)
    write_csv(OUTPUT / "expression_control_results.csv", controls)

    candidate_counts = Counter(row["expression_candidate_result"] for row in candidates)
    control_counts = Counter(row["control_rule_result"] for row in controls)
    corroborated_rho_values = [
        float(row["spearman_rho"])
        for row in candidates
        if row["expression_candidate_result"] == "corroborated_candidate"
    ]
    summary = {
        "release": 3,
        "source_release": 2,
        "candidate_rows": len(candidates),
        "control_rows": len(controls),
        "candidate_rule_counts": {
            key: candidate_counts[key]
            for key in ("corroborated_candidate", "supported_candidate", "not_corroborated")
        },
        "control_rule_counts": {
            key: control_counts[key]
            for key in ("strong_rule_exceeded", "weaker_rule_exceeded", "neither_rule_exceeded")
        },
        "corroborated_candidate_minimum_spearman_rho": min(corroborated_rho_values),
        "corroborated_candidates_below_0_95": sum(value < 0.95 for value in corroborated_rho_values),
        "statistical_interpretation": (
            "The controls are dependent, study-family-specific presumed nonmatches. "
            "Counts are descriptive; no binomial confidence bound or false-confirmation "
            "extrapolation is estimated."
        ),
        "identity_interpretation": (
            "Expression results can corroborate a prespecified different-accession "
            "candidate but do not verify same-specimen or same-patient identity."
        ),
    }
    (OUTPUT / "expression_candidate_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
