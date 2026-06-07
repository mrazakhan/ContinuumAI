# Copyright 2026 mrazakhan
# SPDX-License-Identifier: Apache-2.0
"""Generate the post-1 accuracy plot from data/canonical-results.json.

Output: assets/post-1-accuracy.png (1200 x 700 px, 144 DPI).
Re-run any time the canonical results regenerate to keep the plot in sync.

Usage::

    python3 scripts/plot.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)


def main() -> int:
    canon = json.loads((DATA / "canonical-results.json").read_text())
    frontier = canon["frontier_reference"]
    bars = [
        ("A: baseline\n(GLM-5.1, no skill)", 100 * canon["configs"]["A_baseline"]["aggregate_over_measured"], "#9aa0a6"),
        ("B: + GLM-authored skill",          100 * canon["configs"]["B_GLM_skill"]["aggregate_over_measured"], "#6366f1"),
        ("C: + Opus-authored skill",         100 * canon["configs"]["C_Opus_skill"]["aggregate_over_measured"], "#2563eb"),
        (f"{frontier['name'].split(' on')[0]}\n(frontier reference)", 100 * frontier["pass_rate"], "#cbd5e1"),
    ]
    baseline_val = bars[0][1]

    fig, ax = plt.subplots(figsize=(10, 5.8), dpi=144)
    labels, values, colors = zip(*bars)
    bar_artists = ax.bar(labels, values, color=colors, edgecolor="#1f2937", linewidth=0.6, width=0.62)

    # Value labels on top of each bar
    for bar, val in zip(bar_artists, values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 1.2, f"{val:.1f}%",
                ha="center", va="bottom", fontsize=11, fontweight="bold", color="#0f172a")

    # Lift annotations above the skill bars (B and C)
    for i in (1, 2):
        delta = values[i] - baseline_val
        ax.annotate(
            f"+{delta:.1f} pp", xy=(i, values[i] + 5.5), ha="center", va="bottom",
            fontsize=10.5, color="#15803d", fontweight="bold",
        )

    # Dashed line at baseline level to anchor the reader's eye
    ax.axhline(baseline_val, linestyle="--", linewidth=0.9, color="#9aa0a6", alpha=0.7, zorder=0)
    ax.text(3.45, baseline_val - 1.2, "baseline", ha="right", va="top", fontsize=9, color="#6b7280", style="italic")

    # Axes & spines
    ax.set_ylabel("Terminal-Bench 2.1 aggregated score  (%)", fontsize=11, color="#1f2937")
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 20))
    ax.tick_params(axis="y", labelsize=9.5, colors="#4b5563")
    ax.tick_params(axis="x", labelsize=10, colors="#1f2937", pad=6)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#cbd5e1")
    ax.grid(axis="y", linestyle=":", linewidth=0.5, color="#e5e7eb", zorder=0)
    ax.set_axisbelow(True)

    # Title + subtitle (title above, subtitle below — standard convention)
    fig.suptitle(
        "A learned skill file lifts an open-weight agent on Terminal-Bench 2.1",
        fontsize=13.5, fontweight="bold", color="#0f172a", x=0.125, y=0.96, ha="left",
    )
    ax.set_title(
        "89 tasks · K=3 attempts · 87 measured under every condition · GLM-5.1 as the executor",
        fontsize=9.5, color="#6b7280", style="italic", pad=12, loc="left",
    )

    plt.tight_layout(rect=(0, 0, 1, 0.93))
    out = ASSETS / "post-1-accuracy.png"
    plt.savefig(out, dpi=144, facecolor="white")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
