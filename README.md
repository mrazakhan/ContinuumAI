# ContinuumAI

**Cost-optimal skill-augmented agents** — an open-weight stack that hits **81 % of frontier accuracy at 23 % of the cost** on Terminal-Bench 2.1.

## Read the blog post

→ **[BLOG.md](BLOG.md)** — *81 % of frontier accuracy at 23 % of the cost: what an open-weight agent with a learned skill actually delivers on Terminal-Bench 2.1.*

## Quick numbers

| Stack | TB-2.1 pass rate | $ / attempt | $ / passed task | Per-token cost vs Opus 4.8 |
|---|---|---|---|---|
| Claude Opus 4.8 (TB-2.1 leaderboard #2) | 78.9 % | — *(not published)* | — | 1× (frontier reference) |
| GLM-5.1 baseline (no skill) | 59.4 % | $0.36 | $0.61 | **0.23×** |
| GLM-5.1 + GLM-authored skill | 62.8 % | $0.39 | $0.62 | **0.23×** |
| **GLM-5.1 + Opus-authored skill** | **64.0 %** | **$0.37** | **$0.58** | **0.23×** |

Per-token cost ratio (GLM-5.1 vs Opus 4.8 at our actual measured token usage): **4.4×**.

## Reproduce every number

This repository is self-contained. Two seconds to verify:

```bash
git clone https://github.com/mrazakhan/ContinuumAI.git
cd ContinuumAI
python3 scripts/aggregate.py
```

That reads [`data/raw-trials.json`](data/raw-trials.json) (699 per-trial records, ~230 KB) and produces [`data/canonical-results.json`](data/canonical-results.json) + [`data/canonical-results.md`](data/canonical-results.md). Every number on this page and in the blog post comes from one run of that script.

## Repo layout

| Path | Purpose |
|---|---|
| [`BLOG.md`](BLOG.md) | The launch post — full write-up of methodology, results, case studies, and what comes next |
| [`scripts/aggregate.py`](scripts/aggregate.py) | Single deterministic aggregation script — source of truth for every headline number |
| [`data/raw-trials.json`](data/raw-trials.json) | Per-trial reward + token + cost data (699 trials extracted from the research repo) |
| [`data/canonical-results.json`](data/canonical-results.json) | Machine-readable script output |
| [`data/canonical-results.md`](data/canonical-results.md) | Human-readable summary of the same numbers |
| [`methodology/01-methodology-report.md`](methodology/01-methodology-report.md) | Two-stage skill-authoring pipeline explained with diagrams |
| [`methodology/02-case-studies.md`](methodology/02-case-studies.md) | Three deep-dive case studies of `pass^3: 0 → 1` skill wins |
| [`methodology/03-all-improvements.md`](methodology/03-all-improvements.md) | Per-task tables for Tier 1 and Tier 2 |

## Methodology in a paragraph

89 Terminal-Bench 2.1 tasks, K=3 attempts each, GLM-5.1 as the executor. Skills are single Markdown files authored by a two-stage Reflector → SkillCreator pipeline ([Letta's recipe](https://www.letta.com/blog/skill-learning)) from one failure trajectory per task. Per-task source precedence: skill condition (K=3) > recovery K=1 > baseline (K=3). Coverage: 87 of 89 tasks measured under every condition (2 tasks errored everywhere). Cost: actual `estimated_cost_usd` from the Hermes harness (OpenRouter billing) for GLM-5.1, hypothetical Opus 4.8 cost computed by applying [OpenRouter list pricing](https://openrouter.ai/anthropic/claude-opus-4.8) to our actual token usage. All details in [`methodology/01-methodology-report.md`](methodology/01-methodology-report.md).

## Where the raw trajectories live

The full agent trial directories (~700 dirs with `hermes-session.jsonl`, `trajectory.json`, container logs, verifier outputs) live in the research repo: **[github.com/mrazakhan/LongLearningAgents](https://github.com/mrazakhan/LongLearningAgents)**. Everything you need to verify the headline numbers is in *this* repo — the research repo is for anyone who wants to dig into individual agent behavior.

## What's next

- **A second post** on the 65 % "budget bug" finding from this run — landing within a week
- **Multi-benchmark expansion**: ALFWorld and SWE-bench Verified added to the leaderboard within three weeks; WebArena, GAIA, AgentBench follow
- **Validation gate** on the skill-authoring loop (SkillOpt-style) to stop shipping skills that regress
- **Open-weight executor matrix** across the OpenRouter model catalog with `$ / passed-task` for each

## Why "ContinuumAI"?

Most AI agents today are amnesiacs — each session starts from zero, every developer rediscovers the same gotchas. ContinuumAI is the project tracking what happens when agents' sessions instead form a *continuum* of skills: each failure leaves behind a transferable lesson the next session loads at run time. The TB-2.1 result above is the first measurement that this works on a hard benchmark, with an open-weight executor, at fractional cost. The blog post tells the full story.

## Get in touch

Open a thread in **[Discussions](https://github.com/mrazakhan/ContinuumAI/discussions)** — happy to talk through:

- whether this would apply to your specific stack
- adding your agent benchmark to the leaderboard
- collaboration on the skill-authoring methodology
- the budget-recovery script (if you publish or trust agent benchmark numbers, please run it)

## License

Apache 2.0. See the research repo for full source code under the same license.
