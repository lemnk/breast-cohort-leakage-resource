"""Create release-3 figures with corrected evidence language."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures_v3"
COLORS = {"navy": "#17365D", "blue": "#4C78A8", "orange": "#F28E2B", "red": "#E15759", "gray": "#6B7280", "green": "#59A14F"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def save(fig: plt.Figure, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def exact_overlap() -> None:
    rows = read_csv(ROOT / "data" / "comprehensive" / "exact_gsm_series_pairs.csv")[:20]
    labels = [f"{row['series_a']}–{row['series_b']}" for row in rows][::-1]
    values = [int(row["shared_gsm_count"]) for row in rows][::-1]
    fig, ax = plt.subplots(figsize=(10, 8))
    y = np.arange(len(labels))
    ax.barh(y, values, color=COLORS["blue"])
    ax.set_yticks(y, labels, fontsize=8.5)
    ax.set_xlabel("Shared GEO sample accessions (GSMs)")
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Largest direct accession overlaps", loc="left", fontsize=15, weight="bold", color=COLORS["navy"])
    save(fig, "figure1_direct_accession_overlap")


def evidence_classes() -> None:
    rows = read_csv(ROOT / "release_v3" / "cohort_overlap_lookup.csv")
    counts = Counter(row["evidence_class"] for row in rows)
    labels = ["Direct GSM\noverlap", "Documented GEO\nreuse", "Candidate; review\nrequired"]
    keys = ["direct_accession_overlap", "documented_geo_reuse", "candidate_relationship_review_required"]
    values = [counts[key] for key in keys]
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    bars = ax.bar(labels, values, color=[COLORS["red"], COLORS["green"], COLORS["orange"]], width=0.62)
    ax.bar_label(bars, padding=4, fontsize=12)
    ax.set_ylabel("Series pairs")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    ax.set_title("Release 3 separates direct overlap from candidate evidence", loc="left", fontsize=14, weight="bold", color=COLORS["navy"])
    ax.text(0.5, -0.2, "Expression-only evidence never establishes verified identity", transform=ax.transAxes, ha="center", color=COLORS["gray"])
    fig.subplots_adjust(bottom=0.24)
    save(fig, "figure2_release3_evidence_classes")


def resource_evaluation() -> None:
    summary = json.loads((ROOT / "reports" / "resource_evaluation" / "evaluation_summary.json").read_text(encoding="utf-8"))
    labels = ["Pairs screened", "No detected\nevidence", "Direct GSM +\nGEO-declared", "Candidate added\nbeyond GSM"]
    values = [summary["screened_pairs"], summary["finding_types"]["no_detected_evidence"], summary["direct_gsm_intersection_pairs"], summary["pairs_added_beyond_direct_intersection"]]
    colors = [COLORS["blue"], COLORS["gray"], COLORS["red"], COLORS["orange"]]
    fig, ax = plt.subplots(figsize=(9, 5.3))
    bars = ax.bar(labels, values, color=colors, width=0.62)
    ax.bar_label(bars, padding=4, fontsize=12)
    ax.set_ylabel("Study pairs")
    ax.set_yscale("symlog", linthresh=2)
    ax.set_ylim(0, 900)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    ax.set_title("Prespecified cohort-selection evaluation", loc="left", fontsize=15, weight="bold", color=COLORS["navy"], pad=14)
    ax.text(0.5, -0.22, "30 metadata-selected studies; checker exactly matched direct GSM intersection (0 mismatches)", transform=ax.transAxes, ha="center", color=COLORS["gray"])
    fig.subplots_adjust(bottom=0.25)
    save(fig, "figure3_bounded_resource_evaluation")


def expression_scope() -> None:
    summary = json.loads((ROOT / "data" / "overlap_v3" / "expression_candidate_summary.json").read_text(encoding="utf-8"))
    keys = ["corroborated_candidate", "supported_candidate", "not_corroborated"]
    labels = ["Rule-corroborated\ncandidates", "Weaker-rule\ncandidates", "Not\ncorroborated"]
    values = [summary["candidate_rule_counts"][key] for key in keys]
    fig, ax = plt.subplots(figsize=(8.5, 5.1))
    bars = ax.bar(labels, values, color=[COLORS["blue"], COLORS["orange"], COLORS["gray"]], width=0.62)
    ax.bar_label(bars, padding=4, fontsize=12)
    ax.set_ylabel("Identifier candidates")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    ax.set_title("Expression rules provide candidate corroboration, not identity labels", loc="left", fontsize=13.5, weight="bold", color=COLORS["navy"])
    ax.text(0.5, -0.22, "Development controls: 0/1,925 exceeded the stronger rule; 4/1,925 exceeded only the weaker rule", transform=ax.transAxes, ha="center", color=COLORS["gray"])
    fig.subplots_adjust(bottom=0.25)
    save(fig, "figure4_expression_candidate_results")


def main() -> None:
    exact_overlap()
    evidence_classes()
    resource_evaluation()
    expression_scope()
    print(f"Wrote four release-3 figures to {OUT}")


if __name__ == "__main__":
    main()
