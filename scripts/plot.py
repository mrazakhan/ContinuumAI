# Copyright 2026 mrazakhan
# SPDX-License-Identifier: Apache-2.0
"""Generate the post-1 accuracy plot from data/canonical-results.json.

Output: assets/post-1-accuracy.png (1200 x 720 px, 144 DPI).
Re-run any time the canonical results regenerate to keep the plot in sync.

Design choices:
- Y axis truncated at 30 (declared in the subtitle); the differences
  between conditions are 3-19 pp and look invisible against a 0-100 scale.
- Two-tone blue family for the skill conditions (B lighter, C darker)
  to encode "B comes first, C is the better artifact" at a glance.
- Frontier reference uses a hatched amber fill to signal "external,
  for comparison" without competing visually with our bars.
- Lift annotations live in small green pills above the skill bars so
  the headline "+4.6 pp" reads at thumbnail size.

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

# Use the nicest system sans-serif available
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Inter", "Arial", "DejaVu Sans"],
    "axes.titlesize": 14,
    "axes.labelsize": 11,
})

# Color palette
COLOR_BASELINE      = "#94a3b8"   # slate-400  -- neutral control
COLOR_B             = "#93c5fd"   # blue-300   -- first skill condition (soft)
COLOR_C             = "#1d4ed8"   # blue-700   -- best skill condition (headline)
COLOR_FRONTIER_FILL = "#f1f5f9"   # slate-100  -- pale fill for external reference
COLOR_FRONTIER_HATCH = "#64748b"  # slate-500  -- subtle hatch for external reference
COLOR_LIFT          = "#16a34a"   # green-600  -- positive delta pill
COLOR_TEXT          = "#0f172a"   # slate-900
COLOR_MUTED         = "#64748b"   # slate-500
COLOR_GRID          = "#e2e8f0"   # slate-200


def main() -> int:
    canon = json.loads((DATA / "canonical-results.json").read_text())
    frontier = canon["frontier_reference"]
    series = [
        ("A: baseline\nGLM-5.1, no skill",     100 * canon["configs"]["A_baseline"]["aggregate_over_measured"],   COLOR_BASELINE,      None),
        ("B: + GLM-authored\nskill",            100 * canon["configs"]["B_GLM_skill"]["aggregate_over_measured"],  COLOR_B,             None),
        ("C: + Opus-authored\nskill",           100 * canon["configs"]["C_Opus_skill"]["aggregate_over_measured"], COLOR_C,             None),
        (f"{frontier['name'].split(' on')[0]}\nfrontier reference",  100 * frontier["pass_rate"],                  COLOR_FRONTIER_FILL, "////"),
    ]
    labels, values, colors, hatches = zip(*series)
    baseline_val = values[0]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=144)
    fig.patch.set_facecolor("white")

    # Bars
    bar_artists = ax.bar(
        labels, values,
        color=colors, edgecolor="white", linewidth=0,
        width=0.62, zorder=3,
    )
    # Style the frontier-reference bar: pale fill, subtle slate hatch, thin outline
    plt.rcParams["hatch.color"] = COLOR_FRONTIER_HATCH
    plt.rcParams["hatch.linewidth"] = 0.6
    for bar, hatch in zip(bar_artists, hatches):
        if hatch:
            bar.set_hatch(hatch)
            bar.set_edgecolor(COLOR_MUTED)
            bar.set_linewidth(0.8)
    # Subtle outline on the headline (C) bar to draw the eye
    bar_artists[2].set_edgecolor("#1e3a8a")
    bar_artists[2].set_linewidth(1.2)

    # Value labels on top of each bar
    for bar, val in zip(bar_artists, values):
        ax.text(
            bar.get_x() + bar.get_width()/2, val + 0.7, f"{val:.1f}%",
            ha="center", va="bottom", fontsize=12, fontweight="bold", color=COLOR_TEXT, zorder=5,
        )

    # Lift pills above the skill bars (B and C) -- offset enough to clear the value label
    for i in (1, 2):
        delta = values[i] - baseline_val
        ax.annotate(
            f"+{delta:.1f} pp",
            xy=(i, values[i] + 5.5),
            ha="center", va="bottom",
            fontsize=10.5, color="white", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.45", facecolor=COLOR_LIFT, edgecolor="none"),
            zorder=6,
        )

    # Dashed baseline reference line (no inline label -- bar A's "59.4 %" value label already names it)
    ax.axhline(baseline_val, linestyle=(0, (3, 3)), linewidth=0.9, color=COLOR_MUTED, alpha=0.55, zorder=1)

    # Axes
    ax.set_ylabel("Aggregated score  (%)", fontsize=11, color=COLOR_TEXT, labelpad=10)
    ax.set_ylim(30, 100)
    ax.set_yticks(range(30, 101, 10))
    ax.tick_params(axis="y", labelsize=10, colors=COLOR_MUTED, length=0)
    ax.tick_params(axis="x", labelsize=10, colors=COLOR_TEXT, pad=8, length=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COLOR_GRID)
    ax.spines["bottom"].set_linewidth(1)
    ax.grid(axis="y", linestyle="-", linewidth=0.7, color=COLOR_GRID, zorder=0)
    ax.set_axisbelow(True)

    # Title + subtitle (title first, subtitle below — note the y-axis truncation here)
    fig.suptitle(
        "A learned skill file lifts an open-weight agent on Terminal-Bench 2.1",
        fontsize=14.5, fontweight="bold", color=COLOR_TEXT, x=0.082, y=0.965, ha="left",
    )
    ax.set_title(
        "89 tasks · K=3 attempts · 87 measured under every condition",
        fontsize=10, color=COLOR_MUTED, style="italic", pad=14, loc="left",
    )

    plt.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.16)
    out = ASSETS / "post-1-accuracy.png"
    plt.savefig(out, dpi=144, facecolor="white")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
