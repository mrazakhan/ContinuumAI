# Copyright 2026 mrazakhan
# SPDX-License-Identifier: Apache-2.0
"""Generate the skill-generation loop diagram.

Output: assets/post-1-loop.png  (~1800 x 720 px, 150 DPI)

Editorial design choices match scripts/plot.py:
- Same palette (slate neutrals + sky family + deep navy accent)
- Same typography (Helvetica Neue / Inter / Arial stack)
- Single saturated accent — deep navy on the skill-library node, the
  output of the loop and the focal point
- Light neutrals on the session/trajectory nodes; sky mid-tone on the
  two LLM-call nodes
- One curved dashed arrow underneath for the loop-back

Usage::

    python3 scripts/plot_loop.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Inter", "SF Pro Display", "Arial", "DejaVu Sans"],
    "text.antialiased": True,
    "pdf.fonttype": 42,  # TrueType embedding
})

# Palette (matches scripts/plot.py)
COLOR_NEUTRAL_FILL   = "#f8fafc"   # slate-50    -- session-marker fill
COLOR_NEUTRAL_STROKE = "#94a3b8"   # slate-400   -- session-marker stroke
COLOR_ARTIFACT_FILL  = "#e2e8f0"   # slate-200   -- trajectory node fill
COLOR_ARTIFACT_STROKE = "#94a3b8"  # slate-400
COLOR_LLM_FILL       = "#bae6fd"   # sky-200     -- LLM-call node fill
COLOR_LLM_STROKE     = "#0c4a6e"   # sky-900
COLOR_STORE_FILL     = "#0c4a6e"   # sky-900     -- skill library (focal point)
COLOR_STORE_STROKE   = "#082f49"   # sky-950
COLOR_TEXT_DARK      = "#0f172a"   # slate-900
COLOR_TEXT_LIGHT     = "#ffffff"
COLOR_TEXT_MUTED     = "#64748b"   # slate-500
COLOR_ARROW          = "#475569"   # slate-600
COLOR_LOOP_ARROW     = "#64748b"   # slate-500   -- dashed, slightly lighter


# Node definitions: x-position, two-line title, kind
NODES = [
    (1.2,  "Agent session ends",      "pass or fail",                 "neutral"),
    (4.0,  "Trajectory captured",     "commands · observations",      "artifact"),
    (6.9,  "Reflector",               "extracts the single\nload-bearing insight",  "llm"),
    (10.0, "SkillCreator",            "writes a short\nSKILL.md file","llm"),
    (12.8, "Skill library",           "+1 skill on disk",             "store"),
]

NODE_WIDTH = 2.0
NODE_HEIGHT = 1.5
ROW_Y = 2.6  # vertical center of all nodes


def style_for(kind: str) -> tuple[str, str, str]:
    """Return (fill, stroke, text_color) for a node kind."""
    if kind == "neutral":
        return COLOR_NEUTRAL_FILL,  COLOR_NEUTRAL_STROKE, COLOR_TEXT_DARK
    if kind == "artifact":
        return COLOR_ARTIFACT_FILL, COLOR_ARTIFACT_STROKE, COLOR_TEXT_DARK
    if kind == "llm":
        return COLOR_LLM_FILL,      COLOR_LLM_STROKE,     COLOR_TEXT_DARK
    if kind == "store":
        return COLOR_STORE_FILL,    COLOR_STORE_STROKE,   COLOR_TEXT_LIGHT
    raise ValueError(kind)


def main() -> int:
    fig, ax = plt.subplots(figsize=(14, 4.8), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4.8)
    ax.axis("off")

    # Draw nodes
    for x, title, sub, kind in NODES:
        fill, stroke, text_color = style_for(kind)
        box = FancyBboxPatch(
            (x - NODE_WIDTH / 2, ROW_Y - NODE_HEIGHT / 2),
            NODE_WIDTH, NODE_HEIGHT,
            boxstyle="round,pad=0.02,rounding_size=0.16",
            linewidth=1.2 if kind in ("llm", "store") else 1.0,
            edgecolor=stroke, facecolor=fill, zorder=2,
        )
        ax.add_patch(box)
        # Title — semibold (weight 600) for refined hierarchy vs heavy bold
        ax.text(x, ROW_Y + 0.22, title, ha="center", va="center",
                fontsize=12.5, color=text_color, fontweight=600, zorder=3)
        # Subtitle — regular weight, not italic (italic adds visual heaviness
        # that doesn't pay for itself at small sizes; weight + size contrast
        # is enough hierarchy on its own). Brighter slate inside dark box.
        sub_color = "#e2e8f0" if kind == "store" else "#475569"
        ax.text(x, ROW_Y - 0.32, sub, ha="center", va="center",
                fontsize=10, color=sub_color, fontweight=400, zorder=3,
                linespacing=1.45)

    # Forward arrows between adjacent nodes
    for i in range(len(NODES) - 1):
        x_from = NODES[i][0] + NODE_WIDTH / 2 + 0.05
        x_to   = NODES[i + 1][0] - NODE_WIDTH / 2 - 0.05
        arrow = FancyArrowPatch(
            (x_from, ROW_Y), (x_to, ROW_Y),
            arrowstyle="->",
            color=COLOR_ARROW, linewidth=1.4, zorder=1,
            mutation_scale=15,
        )
        ax.add_patch(arrow)

    # Loop-back arrow: dashed curve from the right of the last node, down and
    # under, back up into the left of the first node.
    x_start = NODES[-1][0]
    x_end   = NODES[0][0]
    loopback = FancyArrowPatch(
        (x_start, ROW_Y - NODE_HEIGHT / 2 - 0.05),
        (x_end,   ROW_Y - NODE_HEIGHT / 2 - 0.05),
        connectionstyle="arc3,rad=-0.22",
        arrowstyle="->",
        color=COLOR_LOOP_ARROW, linewidth=1.3, zorder=1,
        linestyle=(0, (5, 4)), mutation_scale=15,
    )
    ax.add_patch(loopback)

    # Loop-back label (centered between first and last node) — white background
    # cuts the dashed curve cleanly. Italic here works (it differentiates the
    # label from the node-text subtitles, which are now roman).
    label_x = (x_start + x_end) / 2
    ax.text(
        label_x, 0.65,
        "loaded at the start of the next related session",
        ha="center", va="center", fontsize=11, color=COLOR_TEXT_MUTED,
        style="italic", fontweight=500,
        bbox=dict(facecolor="white", edgecolor="none", pad=5),
        zorder=5,
    )

    # Title above the diagram — editorial size, semibold for refined look
    ax.text(
        7.0, 4.45, "The skill-generation loop",
        ha="center", va="center", fontsize=16, color=COLOR_TEXT_DARK,
        fontweight=600,
    )

    plt.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.03)
    out = ASSETS / "post-1-loop.png"
    plt.savefig(out, dpi=150, facecolor="white")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
