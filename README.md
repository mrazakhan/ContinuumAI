# ContinuumAI

**Solving the amnesiac problem for LLM agents.** A research series on agents that compound knowledge across sessions instead of restarting from zero every time. First measured result: **+4.6 percentage points** on Terminal-Bench 2.1 with an open-weight executor and a single failure-trajectory-derived skill — no fine-tuning, no RL.

## The three-post series

| Post | Topic | Status |
|---|---|---|
| **Post 1** | The amnesiac problem and an accuracy measurement on Terminal-Bench 2.1 | [Live → BLOG.md](BLOG.md) |
| Post 2 | Per-attempt and per-passed-task cost economics — what changes when an open-weight executor + skills replaces a frontier closed model | Coming next |
| Post 3 | Detailed case studies of individual skills that turned `pass^3 = 0` into `pass^3 = 1`, with full SKILL.md text and failure trajectories | Coming after Post 2 |
| Bonus | A 65 % budget-anomaly methodology finding from the same run | Coming sooner, out of band |

## Headline result from Post 1

89 tasks. K=3 attempts per task. TB-standard aggregated score. GLM-5.1 as the executor across three conditions:

| Stack | TB-2.1 aggregated score | Lift vs baseline |
|---|---|---|
| Claude Opus 4.8 (TB-2.1 leaderboard #2, frontier reference) | 78.9 % | — |
| **A**: GLM-5.1 baseline (no skill) | **59.4 %** | — |
| **B**: GLM-5.1 + GLM-authored skill | **62.8 %** | **+3.4 pp** |
| **C**: GLM-5.1 + Opus-authored skill | **64.0 %** | **+4.6 pp** |

Author-model takeaway: self-authoring (B) captures about three-quarters of the lift that stronger-author (C) provides. The skill is the asset; the author is a multiplier, not a gate. Both individual developers running cheap open-weight models and engineering organizations with frontier API access can run the loop and see most of the lift either way.

## Reproduce every number — two seconds

This repository is self-contained:

```bash
git clone https://github.com/mrazakhan/ContinuumAI.git
cd ContinuumAI
python3 scripts/aggregate.py    # regenerates every headline number
python3 scripts/plot.py         # regenerates the bar chart in BLOG.md
```

The aggregator reads [`data/raw-trials.json`](data/raw-trials.json) (699 per-trial records, ~230 KB — reward, token usage, per-trial cost) and writes [`data/canonical-results.json`](data/canonical-results.json) + [`data/canonical-results.md`](data/canonical-results.md). The plot script reads the canonical-results JSON and writes [`assets/post-1-accuracy.png`](assets/post-1-accuracy.png). Every number and figure in Post 1 reproduces exactly.

## Repo layout

| Path | Purpose |
|---|---|
| [`BLOG.md`](BLOG.md) | Post 1 — the amnesiac problem and the Terminal-Bench 2.1 measurement |
| [`scripts/aggregate.py`](scripts/aggregate.py) | Single deterministic aggregation script — source of truth for every number |
| [`scripts/plot.py`](scripts/plot.py) | Regenerates the BLOG.md bar chart from `canonical-results.json` |
| [`data/raw-trials.json`](data/raw-trials.json) | 699 per-trial records (reward + token usage + cost) |
| [`data/canonical-results.json`](data/canonical-results.json) | Machine-readable script output |
| [`data/canonical-results.md`](data/canonical-results.md) | Human-readable summary |
| [`assets/post-1-accuracy.png`](assets/post-1-accuracy.png) | The bar chart embedded in Post 1 |

## The continuity loop in a paragraph

Each agent session that fails leaves behind a *failure trajectory* — the verbatim record of what the agent tried, observed, and gave up on. A two-stage Reflector → SkillCreator pipeline reads that trajectory and produces a single Markdown SKILL.md file: a short, mechanical lesson the next session loads at run time. The agent does not *remember*; the skill library does. The library grows with every failure, and the same skill works for any model on the same task. The Terminal-Bench 2.1 result above is the first measurement that this loop works on a hard benchmark, with an open-weight executor. Full mechanism described in [BLOG.md](BLOG.md).

## Get in touch

Open a thread in **[Discussions](https://github.com/mrazakhan/ContinuumAI/discussions)** — relevant for both audiences:

- **Individual developers** tired of re-explaining the same gotchas to the same agent every Tuesday
- **Engineering organizations** running pilots that plateaued at "still rediscovering the same skills six months in"
- **Benchmark maintainers** interested in adding their benchmark to a forthcoming multi-benchmark cost-aware leaderboard
- **Anyone publishing or trusting agent benchmark numbers** — the bonus methodology post on the 65 % budget anomaly is highly relevant; happy to share the recovery script directly

## License

Apache 2.0.
