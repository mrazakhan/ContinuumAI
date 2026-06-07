# Copyright 2026 mrazakhan
# SPDX-License-Identifier: Apache-2.0
"""Canonical aggregation — single source of truth for the headline numbers in BLOG.md.

Reads ``data/raw-trials.json`` (compact extraction of per-trial reward + token + cost
data, ~700 trials, ~230 KB) and produces:

  data/canonical-results.json   — machine-readable per-task scores + aggregates
  data/canonical-results.md     — human-readable summary

Methodology (TB-standard aggregated score):
  Per task, score = mean of pass/fail across the first up-to-K=3 attempts available
  under the canonical condition.

  Per-task source precedence (use first available):
    1. Skill condition (B = glm-tier{1,2}-c1, C = opus-tier{1,2}-c1)
       for tasks in tier1 or tier2 respectively
    2. Long-budget baseline (glm-tb21-baseline-longt) for any task
    3. Original 30-min baseline (glm-tb21-baseline)
    4. Single-attempt recovery K=1 if no executor produced K trials

  Aggregate = mean of per-task scores. We report BOTH "over measured" and
  "treating missing as 0" — readers pick.

Cost computation:
  For each trial, GLM-5.1 cost = the OpenRouter-reported estimated_cost_usd
  recorded by the Hermes harness. Hypothetical Opus 4.8 cost on the same
  prompts = (in_tokens × $5/M + out_tokens × $25/M + cache_tokens × $0.50/M),
  applied to the same token usage we measured.

Usage::

    python3 scripts/aggregate.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
K = 3

# OpenRouter list pricing as of 2026-06-02 (input $/M, output $/M, cache_read $/M).
PRICING = {
    "glm_5_1": (0.98, 3.08, 0.98),  # treat cache_read at input rate (no separate cache discount published)
    "opus_4_8_hypothetical": (5.00, 25.00, 0.50),  # cache_read assumed 10% of input (typical)
}


def trial_cost(in_tok: int, out_tok: int, cache_tok: int, model_key: str) -> float:
    in_p, out_p, cache_p = PRICING[model_key]
    return (in_tok * in_p + out_tok * out_p + cache_tok * cache_p) / 1e6


def first_k_mean(rewards: list[float], k: int = K) -> float | None:
    if not rewards:
        return None
    return sum(rewards[:k]) / min(k, len(rewards))


def group_trials_by_task(trials: list[dict], prefix: str) -> dict[str, list[dict]]:
    """Group by (task, latest job for that prefix). Returns task -> list-of-trials sorted by trial name."""
    by_task_job: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for t in trials:
        if t["prefix"] != prefix:
            continue
        by_task_job[(t["task"], t["job"])].append(t)
    # For each task, pick the most recent job (lexicographic sort on stamp suffix works because timestamps are ISO).
    by_task: dict[str, list[dict]] = {}
    for (task, job), bucket in by_task_job.items():
        existing = by_task.get(task)
        if existing is None or job > existing[0]["job"]:
            by_task[task] = sorted(bucket, key=lambda x: x["trial"])
    return by_task


def score_task(task: str, condition: str, t1: set[str], t2: set[str], trials: list[dict], recovery: dict[str, float]) -> tuple[float | None, str]:
    """Per-task score under the named condition, with the documented source precedence."""
    if condition == "baseline":
        for prefix, tag in (("glm-tb21-baseline-longt", "baseline-longt"), ("glm-tb21-baseline", "baseline-orig")):
            grouped = group_trials_by_task(trials, prefix)
            if task in grouped:
                s = first_k_mean([t["reward"] for t in grouped[task] if t["reward"] is not None])
                if s is not None:
                    return s, tag
        if task in recovery:
            return recovery[task], "recovery-K1"
        return None, "missing"

    skill_prefix_map = {
        "B": ("glm-tier1-c1", "glm-tier2-c1"),
        "C": ("opus-tier1-c1", "opus-tier2-c1"),
    }
    if condition in skill_prefix_map:
        t1_prefix, t2_prefix = skill_prefix_map[condition]
        if task in t1:
            prefix = t1_prefix
        elif task in t2:
            prefix = t2_prefix
        else:
            return score_task(task, "baseline", t1, t2, trials, recovery)
        grouped = group_trials_by_task(trials, prefix)
        if task in grouped:
            s = first_k_mean([t["reward"] for t in grouped[task] if t["reward"] is not None])
            if s is not None:
                return s, f"{condition}-skill"
        if task in recovery:
            return recovery[task], "recovery-K1"
        s2, tag = score_task(task, "baseline", t1, t2, trials, recovery)
        return s2, f"fallback-{tag}"

    raise ValueError(f"unknown condition: {condition}")


def aggregate(condition: str, all_tasks: set[str], t1: set[str], t2: set[str], trials: list[dict], recovery: dict[str, float]) -> dict:
    per_task = {}
    for task in sorted(all_tasks):
        s, src = score_task(task, condition, t1, t2, trials, recovery)
        per_task[task] = {"score": s, "source": src}
    measured = [d["score"] for d in per_task.values() if d["score"] is not None]
    missing = [t for t, d in per_task.items() if d["score"] is None]
    n = len(all_tasks)
    return {
        "condition": condition,
        "n_tasks": n,
        "n_measured": len(measured),
        "n_missing": len(missing),
        "missing_tasks": missing,
        "aggregate_over_measured": (sum(measured) / len(measured)) if measured else None,
        "aggregate_over_all_treat_missing_as_zero": (sum(measured) / n) if n else None,
        "per_task": per_task,
        "sources_summary": dict(Counter(d["source"] for d in per_task.values())),
    }


def aggregate_costs(condition_label: str, condition_config: dict, all_tasks: set[str], t1: set[str], t2: set[str], trials: list[dict]) -> dict:
    """Sum actual GLM cost + hypothetical Opus 4.8 cost for the chosen trials under the canonical condition."""
    total_glm = 0.0
    total_opus_hyp = 0.0
    n_trials = 0
    n_tasks_with_cost = 0
    for task, info in condition_config["per_task"].items():
        src = info["source"]
        if src in ("missing", "fallback-missing"):
            continue
        # map source tag -> prefix for picking which trials to bill
        prefix_map = {
            "C-skill": ("opus-tier1-c1", "opus-tier2-c1"),
            "B-skill": ("glm-tier1-c1", "glm-tier2-c1"),
        }
        if src in prefix_map:
            t1p, t2p = prefix_map[src]
            prefix = t1p if task in t1 else t2p if task in t2 else None
            if prefix is None:
                continue
        elif src in ("baseline-longt", "fallback-baseline-longt", "recovery-K1"):
            prefix = "glm-tb21-baseline-longt"
        elif src in ("baseline-orig", "fallback-baseline-orig"):
            prefix = "glm-tb21-baseline"
        else:
            continue
        grouped = group_trials_by_task(trials, prefix)
        bucket = grouped.get(task)
        if not bucket:
            continue
        task_count = 0
        for t in bucket[:K]:
            if t.get("cost_usd") is None:
                continue
            total_glm += t["cost_usd"]
            it, ot, ct = t.get("in_tokens") or 0, t.get("out_tokens") or 0, t.get("cache_tokens") or 0
            total_opus_hyp += trial_cost(it, ot, ct, "opus_4_8_hypothetical")
            n_trials += 1
            task_count += 1
        if task_count:
            n_tasks_with_cost += 1
    n_passed = sum(1 for d in condition_config["per_task"].values() if d["score"] == 1.0)
    return {
        "n_tasks_with_cost": n_tasks_with_cost,
        "n_trials_with_cost": n_trials,
        "total_glm_usd": round(total_glm, 4),
        "total_opus_4_8_hypothetical_usd": round(total_opus_hyp, 4),
        "avg_per_attempt_glm": round(total_glm / n_trials, 4) if n_trials else 0,
        "avg_per_attempt_opus_4_8_hypothetical": round(total_opus_hyp / n_trials, 4) if n_trials else 0,
        "ratio_opus_to_glm": round(total_opus_hyp / total_glm, 2) if total_glm else 0,
        "cost_per_passed_task_glm": round(total_glm / n_passed, 4) if n_passed else None,
    }


def main() -> int:
    raw = json.loads((DATA / "raw-trials.json").read_text())
    trials = raw["trials"]
    t1 = set(raw["tier1"])
    t2 = set(raw["tier2"])
    recovery = {r["task"]: r["reward"] for r in raw["recovery_k1_results"] if r.get("reward") is not None}
    all_tasks = sorted({t["task"] for t in trials})
    print(f"Loaded {len(trials)} trials covering {len(all_tasks)} TB-2.1 tasks; T1={len(t1)}, T2={len(t2)}; recovery K=1 results={len(recovery)}")

    configs = {
        "A_baseline": aggregate("baseline", set(all_tasks), t1, t2, trials, recovery),
        "B_GLM_skill": aggregate("B", set(all_tasks), t1, t2, trials, recovery),
        "C_Opus_skill": aggregate("C", set(all_tasks), t1, t2, trials, recovery),
    }
    costs = {
        name: aggregate_costs(name, cfg, set(all_tasks), t1, t2, trials)
        for name, cfg in configs.items()
    }

    out = {
        "k": K,
        "model_executor": "z-ai/glm-5.1",
        "frontier_reference": {"name": "Claude Opus 4.8 on TB-2.1 leaderboard #2", "pass_rate": 0.789},
        "methodology": (
            "Per task, mean of first up-to-K=3 attempts under canonical condition. "
            "Per-task source precedence: skill condition > recovery K=1 > baseline. "
            "Cost: actual GLM estimated_cost_usd from OpenRouter; hypothetical Opus 4.8 cost computed at our actual token usage with list pricing."
        ),
        "pricing_usd_per_million_tokens": {
            "glm_5_1": {"input": 0.98, "output": 3.08, "cache_read": 0.98},
            "claude_opus_4_8": {"input": 5.0, "output": 25.0, "cache_read_assumed": 0.5},
        },
        "configs": configs,
        "costs": costs,
    }

    out_json = DATA / "canonical-results.json"
    out_json.write_text(json.dumps(out, indent=2))
    print(f"Wrote {out_json}")

    # Markdown summary
    lines = [
        "# Canonical aggregate — single source of truth",
        "",
        f"K={K}; methodology: per-task mean of first up-to-K=3 attempts; source precedence skill > recovery K=1 > baseline.",
        "",
        "## Headline (TB-standard aggregated score on 89 tasks)",
        "",
        "| Config | Pass rate (measured) | Pass rate (missing→0) | $ / attempt (GLM actual) | $ / attempt (Opus 4.8 hypothetical) | Ratio | n_measured / 89 |",
        "|---|---|---|---|---|---|---|",
    ]
    for key, agg in configs.items():
        m = agg["aggregate_over_measured"]
        z = agg["aggregate_over_all_treat_missing_as_zero"]
        c = costs[key]
        lines.append(
            f"| **{key}** | **{100*m:.2f}%** | {100*z:.2f}% | ${c['avg_per_attempt_glm']:.4f} | ${c['avg_per_attempt_opus_4_8_hypothetical']:.4f} | {c['ratio_opus_to_glm']:.2f}× | {agg['n_measured']}/89 |"
        )
    lines += ["", "*Frontier reference: Claude Opus 4.8 on TB-2.1 leaderboard #2 = 78.9% (cost not published).*", "", "## Source-of-score breakdown per config", ""]
    for key, agg in configs.items():
        lines.append(f"### {key}")
        for src, cnt in sorted(agg["sources_summary"].items(), key=lambda kv: -kv[1]):
            lines.append(f"- {src}: {cnt} tasks")
        if agg["missing_tasks"]:
            lines.append(f"- missing: {agg['missing_tasks']}")
        lines.append("")

    out_md = DATA / "canonical-results.md"
    out_md.write_text("\n".join(lines))
    print(f"Wrote {out_md}")

    print("\n--- HEADLINE ---")
    for key, agg in configs.items():
        m = agg["aggregate_over_measured"]
        c = costs[key]
        print(
            f"  {key:18s}  pass={100*m:.2f}%  avg=${c['avg_per_attempt_glm']:.4f}/attempt  "
            f"opus48-hyp=${c['avg_per_attempt_opus_4_8_hypothetical']:.4f}/attempt  ratio={c['ratio_opus_to_glm']:.2f}×"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
