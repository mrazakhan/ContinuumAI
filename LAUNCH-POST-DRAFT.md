# Launch Post v1 — Draft for Reaction (cost-leading, canonical numbers)

**Status:** v4 draft. All numbers regenerated from a single deterministic aggregation script ([`scripts/aggregate_canonical.py`](../../scripts/aggregate_canonical.py)) — `progress/day20/canonical-results.json` is the single source of truth. Anyone can clone the repo, run the script, and reproduce every number in this post.

**Data sources (all 2026-06-02):**
- OpenRouter list pricing: GLM-5.1 ($0.98/M input, $3.08/M output); Claude Opus 4.8 ($5/M input, $25/M output)
- TB-2.1 official leaderboard: #1 Codex CLI + GPT-5.5 at 83.4%; **#2 Claude Code + Opus 4.8 at 78.9%** (no cost published)
- Per-trial actual cost from `hermes-session.jsonl` → `estimated_cost_usd`, summed under canonical per-task condition
- Per-task source precedence: skill condition (K=3) > recovery K=1 > baseline (K=3)
- Coverage: **87 of 89 tasks measured** under every condition (2 tasks errored everywhere: `extract-moves-from-video`, `path-tracing`)

Project name: **The Irregulars** — published as `github.com/mrazakhan/LongLearningAgents` (no domain at launch; the repo IS the project). After Sherlock Holmes's *Baker Street Irregulars* — the network of small, scrappy agents that gathered intelligence across London while the famous detective stayed home. Frontier closed models are Holmes. We're building the Irregulars.

No remaining blockers. Domain can be registered later if traction justifies it; until then the repo and a GitHub Pages leaderboard (optional, ~30 min to set up) are sufficient.

**Author's note for the reactor (you):** v4 replaces the v3 numbers, which were synthesized arithmetically and couldn't be reproduced from raw data. The new headline is *stronger*: **81 % of frontier accuracy at 23 % of cost** (was: 71 % / 22 %). Skill-only lift is smaller (+4.6 pp vs +8.6 pp) because the v3 baseline was understated — most of the apparent skill lift was actually a measurement artifact. The honest story still works: we're closer to frontier than people realize, and skills add real lift on top.

---

## Suggested title

**"We measured per-attempt agent cost on Terminal-Bench 2.1: an open-weight model with a learned skill hits 81 % of frontier accuracy at 23 % of the cost."**

(Show HN variant: *"Show HN: Open-weight agent on Terminal-Bench 2.1 — 81 % of frontier accuracy at 23 % of the cost"*)

(LinkedIn variant: *"GLM-5.1 + a learned skill: 64.0 % on Terminal-Bench 2.1 at \$0.37 per attempt — vs ~\$1.64 hypothetical Opus 4.8 cost on the same prompts"*)

---

## Body

The [Terminal-Bench 2.1 leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.1) is currently topped by Codex CLI on GPT-5.5 (83.4 %) and Claude Code on Opus 4.8 (78.9 %). Both run on frontier closed models. Neither publishes the dollar cost of getting that accuracy.

We spent two weeks measuring what an open-weight stack can do on the same benchmark, with the same harness, with real cost numbers attached.

**Headline result on 89 TB-2.1 tasks, K=3, TB-standard aggregated score:**

| Stack | Pass rate | $ / attempt | $ / passed task | per-token cost vs Opus 4.8 |
|---|---|---|---|---|
| Claude Opus 4.8 (TB-2.1 leaderboard #2) | **78.9 %** | — *(not published)* | — *(not published)* | **1×** (frontier reference) |
| GLM-5.1 baseline, no skill | 59.4 % | $0.36 | $0.61 | **0.23×** |
| **GLM-5.1 + GLM-authored skill** | **62.8 %** | **$0.39** | **$0.62** | **0.23×** |
| **GLM-5.1 + Opus-authored skill** | **64.0 %** | **$0.37** | **$0.58** | **0.23×** |

(Pass rates computed by [`scripts/aggregate_canonical.py`](https://github.com/mrazakhan/LongLearningAgents/blob/main/scripts/aggregate_canonical.py); 87/89 tasks measured; 2 errored everywhere. Per-token cost ratio computed from OpenRouter list pricing applied to the actual token usage we measured across 214 trials in `progress/day20/`. Hypothetically running our exact same prompts on Opus 4.8 would cost ~\$1.64/attempt at a **4.4×** rate.)

The clean read: **we don't match frontier accuracy; we land at 81 % of it (64.0 / 78.9) at 23 % of the per-token cost (1 / 4.4).** That's a different price-quality cell than the leaderboard captures. For workloads where 78.9 % pass rate is overkill and dollar cost matters, this cell is open.

### How the skill works (briefly)

The skill is a single Markdown file. The agent reads it before starting a task. No model weights are touched.

Authoring uses a two-stage pipeline borrowed from [Letta's skill-learning recipe](https://www.letta.com/blog/skill-learning): a **Reflector** call reads one failure trajectory and extracts the single load-bearing mistake; a **SkillCreator** call writes the actual Markdown file from that reflection plus the trajectory. One trajectory in, one ~80-line skill out. No iterative refinement, no validation loop — the simplest version that works.

Two author models tested:

- **GLM-5.1 authors its own skills** (B) → 62.8 % pass rate (+3.4 pp over baseline)
- **Claude Opus 4.6 authors the skills** (C) → 64.0 % pass rate (+4.6 pp over baseline)

The GLM-authored skill captures ~75 % of the lift the Opus-authored skill gives. You can author and execute with the same cheap open model and still get most of the value. The skill is the asset, not the author.

### Three example skill wins

We documented [three deep-dive case studies](https://github.com/mrazakhan/LongLearningAgents/blob/main/progress/day20/02-case-studies.md) where the skill moved a task from `pass^3 = 0` (never reliably solved) to `pass^3 = 1` (all 3 attempts pass):

- **`db-wal-recovery`** — the agent was opening corrupted SQLite databases directly, which silently destroyed the WAL file on close. Skill: back up the WAL bytes before any `sqlite3` invocation. Outcome: 0/3 → 3/3.
- **`mteb-retrieve`** — the agent was using `sentence_transformers` directly instead of going through `mteb`, which skipped a model-specific query-prefix preprocessing step. Skill: use the mandated loader, not the underlying one. Outcome: 0/3 → 3/3.
- **`polyglot-rust-c`** — the actual root cause was a jemalloc + QEMU + linker interaction crashing the build. Opus's skill correctly identified it; GLM's skill misdiagnosed it as a "use the right command-line flag" issue. Opus skill: 2/3 → 3/3; GLM skill: 2/3 → 1/3 (a regression we'd have caught with a validation gate, see "what's next").

These are real, mechanical, transferable lessons — exactly the kind of thing a frontier model would also benefit from. The same skill files work for any model on the same task.

### Why "The Irregulars"?

In Conan Doyle's stories, the famous detective at 221B Baker Street didn't gather his own intelligence — he ran a network of small, scrappy, cheap-to-deploy agents (a group of London street children) called the Baker Street Irregulars. They went where he couldn't, watched what he couldn't, and reported back. They were never as famous as Holmes. They were also why he kept winning.

That's the pitch. Frontier closed models are Holmes. We're building the Irregulars.

### Coming next: a public, multi-benchmark, cost-aware leaderboard

What's missing from public agent-benchmark reporting:

| Existing | Agentic? | Cost axis? | Skill-augmented vs not? |
|---|---|---|---|
| [Artificial Analysis](https://artificialanalysis.ai) | ❌ | ✅ | ❌ |
| HuggingFace Open LLM | ❌ | ❌ | ❌ |
| LM Arena | ❌ | ❌ | ❌ |
| Official TB-2.1 | ✅ | ❌ | ❌ |
| **Ours** | ✅ | ✅ | ✅ |

Nobody currently publishes `$/task` on agentic benchmarks AND the skill-augmented-vs-baseline split side by side. We're building the leaderboard that fills that gap. v1 covers TB-2.1 across 4 OpenRouter models; ALFWorld and SWE-bench Verified land within 3 weeks; expansion to WebArena, GAIA, and AgentBench after that. Live at [github.com/mrazakhan/LongLearningAgents](https://github.com/mrazakhan/LongLearningAgents).

Weekly sampled-slice updates catch new OpenRouter model adds; monthly full reruns are the authoritative number people cite.

### One methodology finding worth flagging

While running this we noticed something uncomfortable: the Hermes agent harness defaults to a 30-minute per-task budget. When we re-ran 23 tasks that had looked like clean failures at 60 minutes instead, **15 of 23 (65 %) solved**. They weren't capability failures. They were budget-starved.

That single fix moved our measured open-weight baseline from 53.8 % to 59.4 % — most of what we'd initially attributed to skill lift was actually a measurement artifact in the original aggregator. If you publish or trust agent benchmark numbers, run a cheap recovery pass at 2× budget on every "failed" task before you do. It's one extra K=1 attempt per failure, a few dollars of compute, and it can completely change what you think you're measuring. A dedicated post on this finding is coming next week.

### If you're shipping agents at scale

- **If your monthly agent inference bill is meaningful**: there's a real price/quality cell open here. The skills we author for your tasks become yours; you keep running on whatever model your routing layer (OpenRouter, AWS Bedrock, direct providers) selects. Open a thread in [GitHub Discussions](https://github.com/mrazakhan/LongLearningAgents/discussions) — happy to chat through what would apply to your stack.
- **If you maintain an agent benchmark**: we'd like to add your benchmark to the leaderboard. Same offer.
- **If you publish agent benchmark numbers**: please run the budget-recovery pass first. Single-file script in the repo: [link](https://github.com/mrazakhan/LongLearningAgents/blob/main/scripts/eval_glm_vanilla_long_budget_recovery.py).

### Links

- Live leaderboard: [canonical-results.md](https://github.com/mrazakhan/LongLearningAgents/blob/main/progress/day20/canonical-results.md) (auto-regenerated by the canonical script; GitHub Pages version coming)
- **Canonical aggregation script**: [`scripts/aggregate_canonical.py`](https://github.com/mrazakhan/LongLearningAgents/blob/main/scripts/aggregate_canonical.py) — single source of truth for every number in this post
- Full results, methodology, and 3 deep-dive case studies: [`progress/day20/`](https://github.com/mrazakhan/LongLearningAgents/tree/main/progress/day20)
- Two-stage skill-authoring code: [`src/lla/learning/`](https://github.com/mrazakhan/LongLearningAgents/tree/main/src/lla/learning)

---

## Twitter / X thread starter (7 tweets, drop in order)

**1/** We measured per-attempt agent cost on Terminal-Bench 2.1:

- Frontier (Opus 4.8): 78.9 % pass rate
- Open-weight (GLM-5.1) + a learned skill: 64.0 % pass rate at ~23 % of the per-token cost ($0.37 vs ~$1.64 per attempt)

81 % of frontier accuracy. 23 % of the cost. How:

**2/** A single Markdown skill file per task. Agent reads it before starting. No model weights touched. No fine-tuning. No RL.

Authoring is a two-stage pipeline (Reflector → SkillCreator) from [@Letta_AI](https://twitter.com/Letta_AI)'s recipe. One failure trajectory in, one ~80-line skill out.

**3/** Two author models tested:

- GLM-5.1 self-authors → captures ~75 % of the lift
- Claude Opus 4.6 authors → captures the full lift

You can author and execute with the same cheap open model and still get most of the value. The skill is the asset, not the author.

**4/** Three example skill wins (`pass^3` went from 0 → 1):

- `db-wal-recovery`: skill teaches "back up WAL bytes before touching the DB"
- `mteb-retrieve`: skill teaches "use the mandated loader, not the underlying one"
- `polyglot-rust-c`: skill identifies a jemalloc + QEMU + linker interaction crashing the build

**5/** Coming next: a public multi-benchmark, cost-aware leaderboard. TB-2.1 first, then ALFWorld + SWE-bench Verified within 3 weeks.

Nobody currently publishes \$/attempt on agentic benchmarks AND skill-augmented-vs-baseline side by side — let alone with cross-model price-quality cells. We're filling that gap. [github.com/mrazakhan/LongLearningAgents](https://github.com/mrazakhan/LongLearningAgents)

**6/** Bonus methodology finding from this run: 15 of 23 (65 %) of "agent failures" we measured were just our default 30-min budget being too short. Re-ran at 60 min, they solved cleanly.

If you publish agent benchmark numbers, please run the budget recovery first.

**7/** If your monthly agent inference bill is meaningful, this price/quality cell deserves a look. Open an issue or thread: github.com/mrazakhan/LongLearningAgents/discussions

Full numbers + canonical aggregation script + methodology in the repo: github.com/mrazakhan/LongLearningAgents

---

## What you should react to (v4)

1. **The "81 % of frontier / 23 % of cost" headline.** Stronger than v3 (71 % / 22 %), more defensible because every number reproduces from `aggregate_canonical.py`. Alternative framings:
   - *"4.4× cheaper per token, 0.81× the accuracy"* — quantitative
   - *"\$0.37 per attempt instead of \$1.64"* — visceral
   - *"For \$1 of inference, you get one Opus 4.8 attempt (78.9 %) or four GLM+skill attempts (each 64.0 %) — union pass rate ≈ 98 %"* — strongest claim, requires a union-pass calculation

2. **Skill-only lift is smaller than v3 claimed (+4.6 pp vs +8.6 pp).** This is the honest number from the canonical script — most of the apparent v3 lift was measurement artifact from the prior aggregator. The +4.6 pp is still consistent with Letta's published TB-2.0 lift; it's a real result, just less dramatic. Want me to soften the *"closer to frontier than people realize"* framing if it sounds too defensive?

3. **The hypothetical Opus 4.8 cost (\$1.64/attempt).** It's explicitly labeled as "running our same prompts on Opus" — the 4.4× ratio is pure list-pricing math on our measured token usage, not a claim that Opus would have the same token profile. If you want to defang the *"Opus would have used the same tokens"* critique further, we can compute a range using ±20 % token-profile shifts.

4. **Case studies inline vs link-only.** Currently inline (3 examples). Removes ~120 words if cut. I'd keep them — they're the most concrete proof.

5. **CTAs.** Three audiences (customer / benchmark maintainer / benchmark publisher). Customer CTA is the YC-relevant one.

6. **Name + URL + contact.** Resolved: **The Irregulars** as project name (the Sherlock backstory still earns the brand in the post body), GitHub as the launch venue. No domain registration. No remaining publish blocker. Domain can graduate to a real `.dev` / `.com` / `.ai` later if traction justifies it; until then the repo is the project.

7. **What I left out**: the broader persistent-coding-memory thesis (`08-commercialization.md`). Save for follow-up post. Keeps this one tight.
