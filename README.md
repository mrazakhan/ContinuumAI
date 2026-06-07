# ContinuumAI

**Agents that continue where they left off** — an open-weight stack that learns from each failure trajectory and hits **81 % of frontier accuracy at 23 % of the cost** on Terminal-Bench 2.1.

## Read the blog post

→ **[BLOG.md](BLOG.md)** — *Agents that continue where they left off — at 23 % of the cost.* The first measurement that the continuity loop works on a hard benchmark, with an open-weight executor, at fractional cost.

## Quick numbers

| Stack | TB-2.1 pass rate | $ / attempt | $ / passed task | Per-token cost vs Opus 4.8 |
|---|---|---|---|---|
| Claude Opus 4.8 (TB-2.1 leaderboard #2) | 78.9 % | — *(not published)* | — | 1× (frontier reference) |
| GLM-5.1 baseline (no skill) | 59.4 % | $0.36 | $0.61 | **0.23×** |
| GLM-5.1 + GLM-authored skill | 62.8 % | $0.39 | $0.62 | **0.23×** |
| **GLM-5.1 + Opus-authored skill** | **64.0 %** | **$0.37** | **$0.58** | **0.23×** |

Per-token cost ratio (GLM-5.1 vs Opus 4.8 at our actual measured token usage): **4.4×**.

## Reproduce every number — two seconds

This repository is self-contained:

```bash
git clone https://github.com/mrazakhan/ContinuumAI.git
cd ContinuumAI && python3 scripts/aggregate.py
```

That reads [`data/raw-trials.json`](data/raw-trials.json) (699 per-trial records, ~230 KB) and produces [`data/canonical-results.json`](data/canonical-results.json) + [`data/canonical-results.md`](data/canonical-results.md). Every number on this page and in the blog post comes from one run of that script.

## Repo layout

| Path | Purpose |
|---|---|
| [`BLOG.md`](BLOG.md) | The launch post — full write-up of the continuity loop, what we measured, what's next |
| [`scripts/aggregate.py`](scripts/aggregate.py) | Single deterministic aggregation script — source of truth for every headline number |
| [`data/raw-trials.json`](data/raw-trials.json) | 699 per-trial records (reward + token usage + cost in USD) |
| [`data/canonical-results.json`](data/canonical-results.json) | Machine-readable script output |
| [`data/canonical-results.md`](data/canonical-results.md) | Human-readable summary |

## The continuity loop in a paragraph

Each agent session that fails leaves behind a *failure trajectory* — the verbatim record of what the agent tried, observed, and gave up on. A two-stage Reflector → SkillCreator pipeline reads that trajectory and produces a single Markdown SKILL.md file: a short, mechanical lesson the next session loads at run time. The agent doesn't *remember*; the skill library does. The library grows with every failure, and the same skill works for any model on the same task. The TB-2.1 result above is the first measurement that this loop works on a hard benchmark, with an open-weight executor, at fractional cost. Full mechanism described in [BLOG.md](BLOG.md).

## What's next

- **Two follow-up posts coming over the next two weeks**: the 65 % "budget bug" methodology finding from this run, and the first of several detailed case studies on individual skills that turned `pass^3 = 0` into `pass^3 = 1`
- **Multi-benchmark expansion**: ALFWorld and SWE-bench Verified added to the leaderboard within three weeks; WebArena, GAIA, AgentBench follow
- **Validation gate** on the skill-authoring loop (SkillOpt-style) — closes the "we sometimes ship skills that regress" caveat
- **Open-weight executor matrix** across the OpenRouter model catalog with `$ / passed-task` for each

## Get in touch

Open a thread in **[Discussions](https://github.com/mrazakhan/ContinuumAI/discussions)** — happy to talk through:

- whether this would apply to your specific stack
- adding your agent benchmark to the leaderboard
- collaboration on the skill-authoring methodology
- the budget-recovery script (if you publish or trust agent benchmark numbers, please run it)

## License

Apache 2.0.
