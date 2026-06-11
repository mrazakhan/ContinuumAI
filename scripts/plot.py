# Copyright 2026 mrazakhan
# SPDX-License-Identifier: Apache-2.0
"""Generate the post-1 accuracy plot from data/canonical-results.json.

Output: assets/post-1-accuracy.png (1500 x 900 px, 150 DPI).
Re-run any time the canonical results regenerate to keep the plot in sync.

Editorial design choices:
- Single accent: the deep navy on bar C is the visual focus; everything
  else fades back. The baseline is a near-neutral cool grey; the frontier
  reference is a quiet hatched bar; B is a soft mid-tone that bridges
  A and C without competing with C.
- Typography: large editorial title; thin italic subtitle; value labels
  in muted slate, not bold black; lift deltas in small rounded green pills.
- Negative space: generous padding around bars and title, lighter grid,
  no axis frames except a hairline bottom rule.
- No dashed baseline line: bar A's height + its value label already
  anchor the eye, so the extra horizontal rule was schoolbook clutter.

Usage::

    python3 scripts/plot.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Inter", "Arial", "DejaVu Sans"],
    "axes.titlesize": 14,
    "axes.labelsize": 11,
})

# Refined editorial palette
COLOR_BASELINE      = "#cbd5e1"   # slate-300  -- neutral control, recedes
COLOR_B             = "#7dd3fc"   # sky-300    -- soft mid-tone
COLOR_C             = "#0c4a6e"   # sky-900    -- deep navy, the visual focus
COLOR_C_OUTLINE     = "#082f49"   # sky-950    -- subtle outline on C
COLOR_FRONTIER_FILL = "#f8fafc"   # slate-50   -- near-white, recedes
COLOR_FRONTIER_HATCH = "#94a3b8"  # slate-400  -- subtle hatch
COLOR_LIFT          = "#15803d"   # green-700  -- muted, more sophisticated
COLOR_TEXT_HEAD     = "#0f172a"   # slate-900  -- title
COLOR_TEXT_VALUE    = "#475569"   # slate-600  -- value labels
COLOR_TEXT_MUTED    = "#94a3b8"   # slate-400  -- subtitle, axis ticks
COLOR_GRID          = "#f1f5f9"   # slate-100  -- almost invisible
COLOR_RULE          = "#e2e8f0"   # slate-200  -- bottom axis hairline


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

    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=150)
    fig.patch.set_facecolor("white")

    # Bars — slightly narrower, more whitespace between
    bar_artists = ax.bar(
        labels, values,
        color=colors, edgecolor="white", linewidth=0,
        width=0.56, zorder=3,
    )

    # Style the frontier-reference bar (pale fill, subtle hatch)
    plt.rcParams["hatch.color"] = COLOR_FRONTIER_HATCH
    plt.rcParams["hatch.linewidth"] = 0.5
    for bar, hatch in zip(bar_artists, hatches):
        if hatch:
            bar.set_hatch(hatch)
            bar.set_edgecolor(COLOR_TEXT_MUTED)
            bar.set_linewidth(0.6)
    # Faint outline on the headline (C) bar to draw the eye
    bar_artists[2].set_edgecolor(COLOR_C_OUTLINE)
    bar_artists[2].set_linewidth(1.0)

    # Value labels — semibold, muted slate (not bold black)
    for bar, val in zip(bar_artists, values):
        ax.text(
            bar.get_x() + bar.get_width()/2, val + 1.0, f"{val:.1f} %",
            ha="center", va="bottom", fontsize=13, fontweight="600",
            color=COLOR_TEXT_VALUE, zorder=5,
        )

    # Lift pills above the skill bars (B and C) — muted green, rounded
    baseline_val = values[0]
    for i in (1, 2):
        delta = values[i] - baseline_val
        ax.annotate(
            f"+{delta:.1f} %",
            xy=(i, values[i] + 6.5),
            ha="center", va="bottom",
            fontsize=10.5, color="white", fontweight="600",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=COLOR_LIFT, edgecolor="none"),
            zorder=6,
        )

    # Axes
    ax.set_ylabel("Aggregated score  (%)", fontsize=11, color=COLOR_TEXT_MUTED, labelpad=14, fontweight="500")
    ax.set_ylim(30, 102)
    ax.set_yticks(range(30, 101, 10))
    ax.tick_params(axis="y", labelsize=10, colors=COLOR_TEXT_MUTED, length=0)
    ax.tick_params(axis="x", labelsize=10.5, colors=COLOR_TEXT_HEAD, pad=12, length=0)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COLOR_RULE)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.grid(axis="y", linestyle="-", linewidth=0.6, color=COLOR_GRID, zorder=0)
    ax.set_axisbelow(True)

    # Title and subtitle — editorial scale
    fig.suptitle(
        "A learned skill file lifts an open-weight agent on Terminal-Bench 2.1",
        fontsize=17, fontweight="bold", color=COLOR_TEXT_HEAD, x=0.075, y=0.965, ha="left",
    )
    ax.set_title(
        "89 tasks  ·  K=3 attempts  ·  87 measured under every condition",
        fontsize=11, color=COLOR_TEXT_MUTED, style="italic", pad=18, loc="left",
    )

    plt.subplots_adjust(left=0.075, right=0.97, top=0.86, bottom=0.16)
    out = ASSETS / "post-1-accuracy.png"
    plt.savefig(out, dpi=150, facecolor="white")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
