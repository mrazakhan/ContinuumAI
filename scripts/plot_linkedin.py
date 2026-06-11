# Copyright 2026 mrazakhan
# SPDX-License-Identifier: Apache-2.0
"""Generate a LinkedIn-card-aspect version of the post-1 accuracy plot.

Output: assets/post-1-accuracy-linkedin.png  (1200 x 627 px)

Same data, same palette, same value labels as scripts/plot.py — but
sized for LinkedIn's feed-card aspect ratio (1.91 : 1). Headlines stay
legible at the thumbnail size LinkedIn shows in the feed before someone
clicks through.

Usage::

    python3 scripts/plot_linkedin.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Inter", "SF Pro Display", "Arial", "DejaVu Sans"],
    "text.antialiased": True,
    "pdf.fonttype": 42,
})

# Same palette as scripts/plot.py
COLOR_BASELINE       = "#e4e4e7"
COLOR_BASELINE_EDGE  = "#a1a1aa"
COLOR_B              = "#93c5fd"
COLOR_C              = "#1d4ed8"
COLOR_C_EDGE         = "#1e3a8a"
COLOR_FRONTIER_FILL  = "#fafafa"
COLOR_FRONTIER_HATCH = "#71717a"
COLOR_LIFT           = "#16a34a"
COLOR_TEXT_HEAD      = "#0f172a"
COLOR_TEXT_VALUE     = "#1f2937"
COLOR_TEXT_MUTED     = "#71717a"
COLOR_RULE           = "#e5e7eb"


def main() -> int:
    canon = json.loads((DATA / "canonical-results.json").read_text())
    frontier = canon["frontier_reference"]

    series = [
        ("A: baseline",             100 * canon["configs"]["A_baseline"]["aggregate_over_measured"],   COLOR_BASELINE,      COLOR_BASELINE_EDGE, None),
        ("B: + GLM-skill",          100 * canon["configs"]["B_GLM_skill"]["aggregate_over_measured"],  COLOR_B,             None,                None),
        ("C: + Opus-skill",         100 * canon["configs"]["C_Opus_skill"]["aggregate_over_measured"], COLOR_C,             COLOR_C_EDGE,        None),
        ("Opus 4.8\nfrontier",      100 * frontier["pass_rate"],                                       COLOR_FRONTIER_FILL, COLOR_FRONTIER_HATCH, "////"),
    ]
    labels = [s[0] for s in series]
    values = [s[1] for s in series]
    fills  = [s[2] for s in series]
    edges  = [s[3] for s in series]
    hatches = [s[4] for s in series]

    # 1200 x 627 at 100 DPI = exactly LinkedIn card dimensions
    fig, ax = plt.subplots(figsize=(12, 6.27), dpi=100)
    fig.patch.set_facecolor("white")

    bar_width = 0.62

    # Subtle drop shadows behind each bar
    for i, val in enumerate(values):
        ax.add_patch(Rectangle(
            (i - bar_width / 2 + 0.022, 30),
            bar_width, val - 30,
            facecolor=(0, 0, 0, 0.05),
            edgecolor="none",
            zorder=1,
        ))

    bar_artists = ax.bar(
        labels, values,
        color=fills, edgecolor="white", linewidth=0,
        width=bar_width, zorder=3,
    )

    # Frontier hatch
    plt.rcParams["hatch.color"] = COLOR_FRONTIER_HATCH
    plt.rcParams["hatch.linewidth"] = 0.5
    for bar, hatch in zip(bar_artists, hatches):
        if hatch:
            bar.set_hatch(hatch)
            bar.set_edgecolor(COLOR_TEXT_MUTED)
            bar.set_linewidth(0.6)

    # Subtle outlines on A baseline and C headline
    for i, edge in enumerate(edges):
        if edge and hatches[i] is None:
            bar_artists[i].set_edgecolor(edge)
            bar_artists[i].set_linewidth(0.9 if i == 2 else 0.6)

    # Value labels — sized to read at thumbnail
    for bar, val in zip(bar_artists, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 1.4,
            f"{val:.1f} %",
            ha="center", va="bottom",
            fontsize=15, fontweight=500,
            color=COLOR_TEXT_VALUE, zorder=6,
        )

    # Lift pills — larger so they read in feed
    baseline_val = values[0]
    for i in (1, 2):
        delta = values[i] - baseline_val
        ax.annotate(
            f"+{delta:.1f} %",
            xy=(i, values[i] + 6.5),
            ha="center", va="bottom",
            fontsize=12, color="white", fontweight=600,
            bbox=dict(
                boxstyle="round,pad=0.55,rounding_size=0.5",
                facecolor=COLOR_LIFT, edgecolor="none",
            ),
            zorder=7,
        )

    # Axes
    ax.set_ylim(30, 102)
    ax.set_yticks(range(30, 101, 10))
    ax.tick_params(axis="y", labelsize=10.5, colors=COLOR_TEXT_MUTED, length=0, pad=8)
    ax.tick_params(axis="x", labelsize=11, colors=COLOR_TEXT_HEAD, pad=12, length=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COLOR_RULE)
    ax.spines["bottom"].set_linewidth(1)
    ax.set_axisbelow(True)

    # Title — sized to dominate the card
    fig.suptitle(
        "A learned skill file lifts an open-weight agent",
        fontsize=20, fontweight=600, color=COLOR_TEXT_HEAD,
        x=0.06, y=0.95, ha="left",
    )
    ax.set_title(
        "Terminal-Bench 2.1  ·  89 tasks  ·  K=3 attempts",
        fontsize=12, color=COLOR_TEXT_MUTED, pad=18, loc="left",
    )

    plt.subplots_adjust(left=0.06, right=0.97, top=0.84, bottom=0.13)
    out = ASSETS / "post-1-accuracy-linkedin.png"
    plt.savefig(out, dpi=100, facecolor="white")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
