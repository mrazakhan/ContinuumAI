# Copyright 2026 mrazakhan
# SPDX-License-Identifier: Apache-2.0
"""Generate the post-1 accuracy plot from data/canonical-results.json.

Output: assets/post-1-accuracy.png  (1800 x 1080 px, 150 DPI)

Refined editorial design:
- Wider bars (0.68) — more confident visual presence
- Flat, restrained palette — one saturated accent (deep blue on the headline)
- No gridlines — y-axis ticks alone carry the scale
- Larger typography — 18pt title, 15pt value labels, room to breathe
- Subtle drop shadow under bars — adds depth without infographic feel
- Lift indicators inline as small green pills, refined typography
- Pure white background, hairline bottom rule, no top/right/left frame

Usage::

    python3 scripts/plot.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Inter", "SF Pro Display", "Arial", "DejaVu Sans"],
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "text.antialiased": True,
    "pdf.fonttype": 42,
})

# Refined editorial palette
COLOR_BASELINE       = "#e4e4e7"   # zinc-200, warm neutral
COLOR_BASELINE_EDGE  = "#a1a1aa"   # zinc-400
COLOR_B              = "#93c5fd"   # blue-300
COLOR_B_EDGE         = "#3b82f6"   # blue-500
COLOR_C              = "#1d4ed8"   # blue-700 — the focus
COLOR_C_EDGE         = "#1e3a8a"   # blue-900
COLOR_FRONTIER_FILL  = "#fafafa"   # zinc-50
COLOR_FRONTIER_HATCH = "#71717a"   # zinc-500
COLOR_LIFT           = "#16a34a"   # green-600
COLOR_TEXT_HEAD      = "#0f172a"   # slate-900
COLOR_TEXT_VALUE     = "#1f2937"   # gray-800
COLOR_TEXT_MUTED     = "#71717a"   # zinc-500
COLOR_RULE           = "#e5e7eb"   # gray-200


def add_bar_shadow(ax, x, height, width, y_base=30):
    """Add a soft drop shadow below a bar."""
    shadow = Rectangle(
        (x - width / 2 + 0.02, y_base),
        width, height - y_base,
        facecolor=(0, 0, 0, 0.04),
        edgecolor="none",
        zorder=2,
        transform=ax.transData,
    )
    ax.add_patch(shadow)


def main() -> int:
    canon = json.loads((DATA / "canonical-results.json").read_text())
    frontier = canon["frontier_reference"]

    series = [
        ("A: baseline\nGLM-5.1, no skill",     100 * canon["configs"]["A_baseline"]["aggregate_over_measured"],   COLOR_BASELINE,      COLOR_BASELINE_EDGE, None),
        ("B: + GLM-authored\nskill",            100 * canon["configs"]["B_GLM_skill"]["aggregate_over_measured"],  COLOR_B,             None,                None),
        ("C: + Opus-authored\nskill",           100 * canon["configs"]["C_Opus_skill"]["aggregate_over_measured"], COLOR_C,             COLOR_C_EDGE,        None),
        (f"{frontier['name'].split(' on')[0]}\nfrontier reference",  100 * frontier["pass_rate"],                  COLOR_FRONTIER_FILL, COLOR_FRONTIER_HATCH, "////"),
    ]
    labels   = [s[0] for s in series]
    values   = [s[1] for s in series]
    fills    = [s[2] for s in series]
    edges    = [s[3] for s in series]
    hatches  = [s[4] for s in series]

    fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
    fig.patch.set_facecolor("white")

    bar_width = 0.68

    # Subtle drop shadows behind each bar (light gray, slightly offset)
    for i, val in enumerate(values):
        ax.add_patch(Rectangle(
            (i - bar_width / 2 + 0.025, 30),
            bar_width, val - 30,
            facecolor=(0, 0, 0, 0.05),
            edgecolor="none",
            zorder=1,
        ))

    # Bars — wider for confident presence
    bar_artists = ax.bar(
        labels, values,
        color=fills, edgecolor="white", linewidth=0,
        width=bar_width, zorder=3,
    )

    # Frontier hatch styling
    plt.rcParams["hatch.color"] = COLOR_FRONTIER_HATCH
    plt.rcParams["hatch.linewidth"] = 0.5
    for bar, hatch in zip(bar_artists, hatches):
        if hatch:
            bar.set_hatch(hatch)
            bar.set_edgecolor(COLOR_TEXT_MUTED)
            bar.set_linewidth(0.6)

    # Bar outlines for headline (C) and baseline (A) — subtle definition
    for i, edge in enumerate(edges):
        if edge and hatches[i] is None:
            bar_artists[i].set_edgecolor(edge)
            bar_artists[i].set_linewidth(0.9 if i == 2 else 0.6)

    # Value labels — larger, refined tabular figures
    for bar, val in zip(bar_artists, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 1.4,
            f"{val:.1f} %",
            ha="center", va="bottom",
            fontsize=15, fontweight=500,
            color=COLOR_TEXT_VALUE, zorder=6,
        )

    # Lift pills above the skill bars — refined typography, slightly larger
    baseline_val = values[0]
    for i in (1, 2):
        delta = values[i] - baseline_val
        ax.annotate(
            f"+{delta:.1f} %",
            xy=(i, values[i] + 6.5),
            ha="center", va="bottom",
            fontsize=11.5, color="white", fontweight=600,
            bbox=dict(
                boxstyle="round,pad=0.55,rounding_size=0.5",
                facecolor=COLOR_LIFT, edgecolor="none",
            ),
            zorder=7,
        )

    # Axes — minimal frame, no grid
    ax.set_ylim(30, 102)
    ax.set_yticks(range(30, 101, 10))
    ax.tick_params(axis="y", labelsize=10.5, colors=COLOR_TEXT_MUTED, length=0, pad=8)
    ax.tick_params(axis="x", labelsize=11, colors=COLOR_TEXT_HEAD, pad=14, length=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COLOR_RULE)
    ax.spines["bottom"].set_linewidth(1)

    # No grid — y-ticks alone carry the scale
    ax.set_axisbelow(True)

    # Title — editorial scale
    fig.suptitle(
        "A learned skill file lifts an open-weight agent on Terminal-Bench 2.1",
        fontsize=18, fontweight=600, color=COLOR_TEXT_HEAD,
        x=0.065, y=0.955, ha="left",
    )
    ax.set_title(
        "89 tasks  ·  K=3 attempts  ·  87 measured under every condition",
        fontsize=11.5, color=COLOR_TEXT_MUTED, pad=22, loc="left",
    )

    plt.subplots_adjust(left=0.065, right=0.97, top=0.86, bottom=0.14)
    out = ASSETS / "post-1-accuracy.png"
    plt.savefig(out, dpi=150, facecolor="white")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
