"""Create publication figures from frozen registry outputs."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"

COLORS = {
    "navy": "#17365D",
    "blue": "#4C78A8",
    "orange": "#F28E2B",
    "green": "#59A14F",
    "red": "#E15759",
    "gray": "#6B7280",
    "light": "#EAF0F6",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def save(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIGURES / f"{stem}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(FIGURES / f"{stem}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def flow_figure() -> None:
    fig, ax = plt.subplots(figsize=(12, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    boxes = [
        (0.2, 4.25, 2.25, 0.95, "5,931 GEO series\n(frozen query universe)"),
        (3.1, 4.25, 2.25, 0.95, "282,989 sample\nmentions"),
        (6.0, 4.25, 2.25, 0.95, "41,428 reused GSMs\nin 1,622 series"),
        (6.0, 2.55, 2.25, 0.95, "2,125 specific-title\nalias groups"),
        (0.2, 0.85, 2.25, 0.95, "11 seed matrices\n(1,947 samples)"),
        (3.1, 0.85, 2.25, 0.95, "385 identifier\ncandidate links"),
        (6.0, 0.85, 2.25, 0.95, "316 expression-\ncorroborated links"),
        (9.25, 2.55, 2.25, 0.95, "1,948 series pairs\nin release lookup"),
    ]
    for x, y, w, h, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04", fc=COLORS["light"], ec=COLORS["navy"], lw=1.5))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=10.2, color=COLORS["navy"])
    for x1, y1, x2, y2 in [
        (2.45,4.73,3.1,4.73), (5.35,4.73,6.0,4.73),
        (4.23,4.25,6.0,3.03),
        (2.45,1.33,3.1,1.33), (5.35,1.33,6.0,1.33),
        (8.25,4.73,9.6,3.5), (8.25,3.03,9.25,3.03), (8.25,1.33,9.6,2.55),
    ]:
        ax.annotate("", xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle="->", lw=1.6, color=COLORS["gray"]))
    ax.text(7.12, 0.45, "304 confirmed + 12 supported; 69 identifier links not corroborated", ha="center", fontsize=10.2, color=COLORS["gray"])
    ax.set_title("Construction of the breast cancer cohort-overlap resource", loc="left", fontsize=15, weight="bold", color=COLORS["navy"])
    save(fig, "figure1_resource_flow")


def exact_reuse_figure() -> None:
    rows = read_csv(ROOT / "data" / "comprehensive" / "exact_gsm_series_pairs.csv")[:20]
    labels = [f"{r['series_a']}–{r['series_b']}" for r in rows][::-1]
    values = [int(r["shared_gsm_count"]) for r in rows][::-1]
    patterns = [r["overlap_pattern"] for r in rows][::-1]
    palette = {"complete_containment": COLORS["blue"], "near_containment": COLORS["orange"], "partial_overlap": COLORS["red"]}
    fig, ax = plt.subplots(figsize=(10, 8))
    y = np.arange(len(labels))
    ax.barh(y, values, color=[palette[p] for p in patterns])
    ax.set_yticks(y, labels, fontsize=9)
    ax.set_xlabel("Shared GEO sample accessions")
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    for yi, value in zip(y, values):
        ax.text(value + max(values) * 0.01, yi, f"{value}", va="center", fontsize=8)
    handles = [plt.Rectangle((0,0),1,1,color=palette[p]) for p in palette]
    ax.legend(handles, ["Complete containment", "Near containment", "Partial overlap"], frameon=False, loc="lower right")
    ax.set_title("Largest exact-accession overlaps between GEO series", loc="left", fontsize=15, weight="bold", color=COLORS["navy"])
    save(fig, "figure2_exact_accession_overlap")


def fingerprint_figure() -> None:
    candidates = read_csv(ROOT / "data" / "overlap" / "expression_validated_edges.csv")
    controls = read_csv(ROOT / "data" / "overlap" / "expression_negative_controls.csv")
    candidate_by_pair: dict[str, list[float]] = {}
    control_by_pair: dict[str, list[float]] = {}
    for row in candidates:
        p = "–".join(sorted((row["series_a"], row["series_b"])))
        candidate_by_pair.setdefault(p, []).append(float(row["spearman_rho"]))
    for row in controls:
        p = row["series_pair"].replace("--", "–")
        control_by_pair.setdefault(p, []).append(float(row["spearman_rho"]))
    pairs = sorted(candidate_by_pair, key=lambda p: -len(candidate_by_pair[p]))
    fig, ax = plt.subplots(figsize=(12, 6.5))
    positions, data, colors = [], [], []
    for i, p in enumerate(pairs):
        positions.extend([i * 3, i * 3 + 1])
        data.extend([candidate_by_pair[p], control_by_pair[p]])
        colors.extend([COLORS["blue"], COLORS["gray"]])
    bp = ax.boxplot(data, positions=positions, widths=0.72, patch_artist=True, showfliers=False, medianprops=dict(color="white", lw=1.5))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    ax.set_xticks([i * 3 + 0.5 for i in range(len(pairs))], [p.replace("–", "–\n") for p in pairs], fontsize=8)
    ax.set_ylabel("Within-sample probe-rank correlation")
    ax.set_ylim(0.25, 1.03)
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend([plt.Rectangle((0,0),1,1,color=COLORS["blue"]), plt.Rectangle((0,0),1,1,color=COLORS["gray"])], ["Identifier candidate", "Deterministic nonmatch"], frameon=False, loc="lower right")
    ax.set_title("Expression fingerprints distinguish many candidate reuses from nonmatched controls", loc="left", fontsize=14, weight="bold", color=COLORS["navy"])
    save(fig, "figure3_expression_fingerprints")


def release_figure() -> None:
    rows = read_csv(ROOT / "release_v2" / "cohort_overlap_lookup.csv")
    tiers = Counter(r["overall_evidence_tier"] for r in rows)
    labels = ["High-confidence overlap", "Manual review required"]
    values = [tiers["high_confidence_overlap"], tiers["manual_review_required"]]
    fig, ax = plt.subplots(figsize=(7, 4.8))
    bars = ax.bar(labels, values, color=[COLORS["red"], COLORS["orange"]], width=0.58)
    ax.bar_label(bars, fontsize=13, padding=4)
    ax.set_ylabel("Series pairs")
    ax.set_ylim(0, max(values) * 1.25)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    ax.set_title("Evidence tier in release 2", loc="left", fontsize=15, weight="bold", color=COLORS["navy"])
    save(fig, "figure4_release_evidence")


def validation_scope_figure() -> None:
    metadata = json.loads((ROOT / "reports" / "validation" / "metadata_rule_validation.json").read_text(encoding="utf-8"))
    platform = json.loads((ROOT / "reports" / "validation" / "platform_coverage.json").read_text(encoding="utf-8"))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.9))

    recovery = 100 * metadata["positive_strict_rule_recovery_rate_within_exact_gsm_reuse"]
    collision = 100 * metadata["background_strict_collision_rate"]
    bars = axes[0].bar(
        ["Known exact-reuse\npairs recovered", "Presumed-background\npairs colliding"],
        [recovery, collision],
        color=[COLORS["blue"], COLORS["gray"]],
        width=0.58,
    )
    axes[0].bar_label(bars, labels=[f"{recovery:.1f}%", "0%"], padding=4)
    axes[0].set_ylabel("Percent")
    axes[0].set_ylim(0, 60)
    axes[0].set_title("A  Title-rule check", loc="left", weight="bold", color=COLORS["navy"])
    axes[0].text(0.5, -0.25, "Recovery is conditional on exact-GSM reuse; background pairs were not verified negatives", transform=axes[0].transAxes, ha="center", fontsize=8.2, color=COLORS["gray"])

    values = [platform["total_series"], platform["gpl96_series_in_universe"], platform["expression_validation_series"]]
    labels = ["Registry\nuniverse", "GPL96 in\nuniverse", "Fingerprint\nevaluation"]
    bars = axes[1].bar(labels, values, color=[COLORS["blue"], COLORS["orange"], COLORS["red"]], width=0.58)
    axes[1].set_yscale("log")
    axes[1].bar_label(bars, labels=[f"{v:,}" for v in values], padding=4)
    axes[1].set_ylabel("Series (log scale)")
    axes[1].set_title("B  Expression-validation scope", loc="left", weight="bold", color=COLORS["navy"])
    axes[1].text(0.5, -0.25, "Seven GPL96 series = 0.12% of the registry", transform=axes[1].transAxes, ha="center", fontsize=8.5, color=COLORS["gray"])

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("Validation findings and scope limits", x=0.06, ha="left", fontsize=15, weight="bold", color=COLORS["navy"])
    fig.subplots_adjust(bottom=0.25, top=0.84, wspace=0.32)
    save(fig, "figure5_validation_scope")


def heldout_figure() -> None:
    candidates = read_csv(ROOT / "data" / "heldout" / "heldout_crossplatform_candidates.csv")
    controls = read_csv(ROOT / "data" / "heldout" / "heldout_crossplatform_controls.csv")
    null99 = float(candidates[0]["pair_null_p99"])
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    control_values = [float(r["spearman_rho"]) for r in controls]
    offsets = np.linspace(-0.18, 0.18, len(control_values))
    ax.scatter(np.zeros(len(control_values)) + offsets, control_values, color=COLORS["gray"], s=38, alpha=0.75, label="Deterministic controls")
    labels = ["UACC812", "ZR-75-1", "ZR-75-30"]
    colors = [COLORS["green"] if r["expression_evidence"] == "confirmed" else COLORS["red"] for r in candidates]
    for x, label, row, color in zip(range(1, 4), labels, candidates, colors):
        rho = float(row["spearman_rho"])
        ax.scatter([x], [rho], color=color, s=95, zorder=3)
        ax.text(x, rho + 0.012, f"ranks {row['rank_a_to_b']}/{row['rank_b_to_a']}", ha="center", fontsize=9)
    ax.axhline(null99, color=COLORS["orange"], lw=1.6, ls="--", label=f"Control 99th percentile ({null99:.3f})")
    ax.set_xticks(range(4), ["Controls", *labels])
    ax.set_ylabel("Within-sample probe-rank correlation")
    ax.set_ylim(min(control_values) - 0.04, 0.95)
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Held-out GPL96–GPL570 cell-line fingerprint check", loc="left", fontsize=14, weight="bold", color=COLORS["navy"])
    ax.text(0.01, -0.18, "Two reciprocal top-1 confirmations; ZR-75-1 reverse rank = 9", transform=ax.transAxes, fontsize=9.5, color=COLORS["gray"])
    fig.subplots_adjust(bottom=0.23)
    save(fig, "figure6_heldout_crossplatform")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    flow_figure()
    exact_reuse_figure()
    fingerprint_figure()
    release_figure()
    validation_scope_figure()
    if (ROOT / "data" / "heldout" / "heldout_crossplatform_candidates.csv").exists():
        heldout_figure()
    print(f"Wrote 6 figures in PNG and PDF format to {FIGURES}")


if __name__ == "__main__":
    main()
