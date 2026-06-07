# ContinuumAI

**Cost-optimal skill-augmented agents** — an open-weight stack that hits **81 % of frontier accuracy at 23 % of the cost** on Terminal-Bench 2.1.

## Quick numbers

| Stack | TB-2.1 pass rate | $ / attempt | $ / passed task |
|---|---|---|---|
| Claude Opus 4.8 (TB-2.1 leaderboard #2) | 78.9 % | — *(not published)* | — |
| GLM-5.1 baseline (no skill) | 59.4 % | $0.36 | $0.61 |
| GLM-5.1 + GLM-authored skill | 62.8 % | $0.39 | $0.62 |
| **GLM-5.1 + Opus-authored skill** | **64.0 %** | **$0.37** | **$0.58** |

Per-token cost ratio (GLM-5.1 vs Opus 4.8 at our actual token usage): **4.4×**.

## Read the launch post

[**LAUNCH-POST-DRAFT.md**](LAUNCH-POST-DRAFT.md) — full write-up of the methodology, three case studies where a single skill moved a task from `pass^3 = 0` to `pass^3 = 1`, the per-token cost comparison, and what comes next.

## Source data and methodology

The raw trajectory data, the skill files, the skill-authoring pipeline, and the canonical aggregation script all live in the research repo:

→ **[github.com/mrazakhan/LongLearningAgents](https://github.com/mrazakhan/LongLearningAgents)**

Specifically:
- [`scripts/aggregate_canonical.py`](https://github.com/mrazakhan/LongLearningAgents/blob/main/scripts/aggregate_canonical.py) — single deterministic source for every number above. Clone the repo, run the script, reproduce every value exactly.
- [`progress/day20/`](https://github.com/mrazakhan/LongLearningAgents/tree/main/progress/day20) — full results, methodology report, and three deep-dive case studies
- [`src/lla/learning/`](https://github.com/mrazakhan/LongLearningAgents/tree/main/src/lla/learning) — two-stage skill-authoring code (Reflector → SkillCreator)

## Why "ContinuumAI"?

Agents today restart from zero every session. The premise here is that they shouldn't — each failure should leave behind a transferable lesson the next session loads at run time. ContinuumAI is the project tracking what happens when you actually build that.

## Get in touch

Open an issue or a thread in [Discussions](https://github.com/mrazakhan/ContinuumAI/discussions) — happy to talk through:
- whether this would apply to your stack
- adding your agent benchmark to the leaderboard
- collaboration on the skill-authoring methodology

## What's next

- Multi-benchmark live cost/quality leaderboard — TB-2.1 already covered; ALFWorld and SWE-bench Verified within 3 weeks; WebArena, GAIA, AgentBench after that
- Validation gate on the skill-authoring loop (SkillOpt-style) to avoid shipping skills that regress
- Open-weight executor matrix across the OpenRouter model catalog (Qwen, GLM, Mistral, Llama variants) with `$/passed-task` for each
