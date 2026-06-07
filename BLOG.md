# AI agents are amnesiacs. We measured a fix that lets them compound knowledge across sessions.

*Post 1 of 3 in the ContinuumAI series. Published 2026-06-02.*

## The amnesiac problem

Every modern LLM coding agent — Cursor, Claude Code, Aider, OpenHands, Codex, the one your platform team is building in-house — shares one limiting structural property: no memory across sessions.

Each task starts from scratch. The agent works through a problem, makes mistakes, eventually finishes (or doesn't), and then everything it learned in that session evaporates the moment the conversation ends.

For an individual developer this is mildly annoying. You watch your agent rediscover the same QEMU-userland-linker landmine on the same Rust crate, three Tuesdays in a row. Forty minutes each time. You watch it fall into the same SQLite-WAL-discard-on-close trap every time you run the recovery script. You spend more time re-explaining your project's conventions ("we use `ruff`, not `black`; `uv`, not `pip`; pre-commit runs `mypy`, not just `pyright`") than you spend actually getting work done.

For an engineering organization, this is significantly more expensive. Every engineer's agent runs through the same gotcha library independently. The skill your senior engineer's agent acquired last quarter — the one that knows exactly which incantation gets a stubborn dependency to compile in your weird internal build environment — does not transfer to the junior engineer's agent next quarter. The institutional knowledge your humans accumulate organically across PRs, postmortems, design reviews, and onboarding wikis has no analog for agents. Your humans compound. Your agents do not.

The absence of that compounding shows up in the most common pilot postmortem we hear from engineering leaders: *"The agent worked great for the first two weeks. By month six it felt like the same agent we started with, doing the same tasks, getting tripped up by the same things."* Of course it did. There was no mechanism for it to be anything else.

The bigger model is not the fix. We have plenty of bigger models. Output quality on most agent workloads is no longer gated by raw capability — frontier closed models could solve essentially every Terminal-Bench 2.1 task if you gave them enough tokens. The gating constraint is increasingly whether the *system* can carry yesterday's lesson into today. Whether the agent that just spent forty minutes figuring out your build system can produce a five-line note that the next agent — yours, your teammate's, the new hire's — loads at the start of every related task.

That five-line note is the missing piece. ContinuumAI is the project we are running to test that hypothesis at benchmark scale. This post is the first of three describing what we found.

## What we built, briefly

Skill learning for stateful agents — the open question of how to make agent sessions accumulate transferable knowledge across runs without retraining the underlying model — has become an active research focus across both academic groups and industry labs over the past 18 months [1, 2]. The two-stage structure we use here (reflect on a session trajectory, write the lesson to a skill artifact, load it at run time) is one of several approaches that have shown empirical signal in published reports. Most of the recent debate has been about *how strict the loop should be* (one-shot vs validation-gated vs iterative-refined) and *where the lesson should live* (model weights, vector store, plain-text Markdown file). The continuum thesis is closest to the last.

After an agent session ends — pass or fail — a **Reflector** LLM call reads the full session trajectory. Not just the final output: every command the agent ran, every observation it made, every dead end it explored. The Reflector's job is to extract the single load-bearing decision that determined the outcome. Not a list of mistakes; just the one thing that, if the agent had known it going in, would have fixed the run.

That reflection is handed to a **SkillCreator** LLM call, which writes a short Markdown file: a *skill*. Each skill has a name (kebab-case), a triggering condition ("when this kind of task appears…"), a Principle section of one or two sentences explaining the conceptual gap, and a Procedure section of up to five concrete steps. Eighty lines or less.

The next session that touches the same kind of problem reads that skill from the agent's filesystem before doing anything else. No model weights are touched. No fine-tuning. No RL. The skill *is* the persistent memory, and it transfers cleanly: a skill authored from a GLM-5.1 failure works for any model that runs the same task.

We deliberately kept the first iteration of the loop simple. One failure trajectory in, one skill out. No iterative refinement. No validation gating. No edit budgets. The goal of this measurement was to learn how much lift the basics alone produce, before adding the obvious refinements. Future iterations will add the gates and the loops; we wanted to know the floor first.

## Measuring it on Terminal-Bench 2.1

Picking the benchmark mattered. We needed one that:

1. **Tests multi-step, long-horizon agent work.** A benchmark dominated by one-shot QA has no "skill" content for the loop to encode — the skill ends up generic, the lift is small, and the result does not generalize.
2. **Has a published frontier reference.** Without a credible "if you used the best closed model" number to compare to, no measured lift is interpretable.
3. **Allows clean K-run aggregation.** TB-standard aggregated score — per-task mean of the first K attempts, averaged across tasks — is clean, well-understood, comparable across teams.

[Terminal-Bench 2.1](https://www.tbench.ai/leaderboard/terminal-bench/2.1) fits all three. 89 long-horizon coding and systems tasks: SQLite-WAL recovery, build-chain debugging, image-processing pipelines, reverse-engineering puzzles, network-protocol implementations, environment-configuration problems. Each task has a programmatic verifier that returns a binary pass/fail score. The current leaderboard top is Codex CLI + GPT-5.5 at 83.4 %; second is Claude Code + Opus 4.8 at 78.9 %. Both run on frontier closed models.

We ran the experiment with **GLM-5.1** as the executor across three conditions. K=3 attempts per task. 87 of 89 tasks measured under every condition (two tasks errored in environment setup before the agent could run; we report them with an asterisk rather than silently dropping).

Three conditions:

- **A: baseline.** GLM-5.1 with no skill loaded — the unaided open-weight reference.
- **B: GLM-authored skill.** GLM-5.1 reads a SKILL.md authored by GLM-5.1 from its own prior failure. Same model end-to-end.
- **C: Opus-authored skill.** GLM-5.1 reads a SKILL.md authored by Claude Opus 4.6 from the same prior failure. The skill is a stronger artifact; the executor is unchanged.

### Results

| Stack | TB-2.1 aggregated score | Lift vs baseline |
|---|---|---|
| Claude Opus 4.8 (leaderboard #2) | 78.9 % | frontier reference |
| **A**: GLM-5.1 baseline (no skill) | **59.4 %** | — |
| **B**: GLM-5.1 + GLM-authored skill | **62.8 %** | **+3.4 pp** |
| **C**: GLM-5.1 + Opus-authored skill | **64.0 %** | **+4.6 pp** |

A +4.6-point lift on a benchmark at this hardness level — from a single failure trajectory per task, with no iterative refinement and no validation gating — is the headline. For context, published results in this research area have reported:

- **+9 points** for trajectory-only approaches on the easier predecessor benchmark (TB-2.0) [1]
- **+9 to +25 points** for iterative-gated approaches on broader benchmark suites (search QA, spreadsheets, ALFWorld), depending on the benchmark and the gating strictness [2]

Our +4.6 sits below both, which is expected: TB-2.1 is harder than TB-2.0, our loop is simpler than the gated variants (no validation gate), and we used GLM-5.1 as the executor where the +9-to-+25 numbers were obtained on frontier closed models. The signal we wanted was *the loop works at all on a hard benchmark with an open-weight executor*, and it does. Closing more of the gap to the gated-approach numbers comes from adding the gate — that is the next iteration of the loop, and it is the next thing we will measure.

### Two findings from the same run worth flagging

**The author model matters less than you would expect.** A design dimension explored in this literature is the author/executor split: a stronger model can author skills that a weaker model executes. We tested both author conditions. Self-authoring (GLM-5.1 writing its own skills, condition B) captures about three-quarters of the lift that Opus-authoring (condition C) provides. The skill is the asset; the author is a multiplier on it, not a gate to it. This matters for both audiences. Individual developers and small teams running cheap open-weight executors can run the loop end-to-end without ever calling a frontier API. Engineering organizations that have Opus access for the skill-authoring step can extract a marginal improvement, but the bulk of the lift is available without it — which means the policy debate around "should we send our private trajectories to a frontier API?" has a defensible no-API-access answer if the answer is no.

**Some skills regress their target tasks.** A small number of tasks where the unaided baseline already passed 2 of 3 attempts ended up passing only 1 of 3 after a skill was loaded. The loop ships every skill the author produces — there is no validation gate yet — so this is the expected failure mode of the simplest version. Adding a validation gate, as iterative-refinement approaches do [2], catches most of these before they ship. A post in this series will walk through specific regressed skills and what the Reflector got wrong; the failure modes are instructive.

## Reproducibility

Every number in this post comes from one deterministic script in the repo:

```bash
git clone https://github.com/mrazakhan/ContinuumAI.git
cd ContinuumAI && python3 scripts/aggregate.py
```

That reads [`data/raw-trials.json`](data/raw-trials.json) — 699 per-trial records, ~230 KB, containing every reward and every token count from the run — and writes [`data/canonical-results.json`](data/canonical-results.json) plus a human-readable [`data/canonical-results.md`](data/canonical-results.md). Takes about two seconds. No setup. No external API calls.

If you want to verify the +4.6-point number directly, this is the way.

## What is next in this series

This post is the first of three.

**Post 2 — The cost story.** The same experiment, viewed through a different lens. Per-attempt and per-passed-task economics when an open-weight executor with skills replaces a frontier closed model. Relevant reading if your organization has a monthly agent inference bill and a procurement conversation about it.

**Post 3 — Case studies.** Detailed write-ups of individual skills that took specific tasks from "never solved" to "always solved." Each case includes the full SKILL.md text, the failure trajectory that produced it, and a discussion of what the Reflector got right — and in two cases, what it got wrong. Relevant reading if you want to understand what skill-learning actually encodes and what it cannot.

A bonus methodology post is coming out of band, sooner — on a 65 % budget-anomaly finding that surfaced midway through this run. If your team publishes or trusts agent benchmark numbers, you will want to see it before your next publication.

## References

[1] *Skill Learning* — Letta, 2026. https://www.letta.com/blog/skill-learning
[2] *SkillOpt: Optimizing Natural-Language Skills as the Trainable State of Frozen Agents* — Microsoft Research, 2026. https://microsoft.github.io/SkillOpt/ · paper: https://arxiv.org/abs/2605.23904

## Closing

The amnesiac problem is not a curiosity. It is the single biggest reason organizations report that AI agent pilots "did not work out" after six months — the agents are useful at first, but they never compound. They never become the *senior engineer's agent that has been in the trenches.* They stay junior forever.

The continuum changes that. Every session ends with the next session's bootstrap data. Skills accumulate. The agent gets quietly better at *your* stack — your conventions, your gotchas, your weird build environment — every time you use it. That is the thesis. The +4.6-point lift above is the first measurement that the loop works at benchmark scale, with an open-weight executor, on a benchmark designed to be hard.

If you are an individual developer who is tired of re-explaining the same gotchas to the same agent, or an engineering organization watching the same skill rediscover itself across every engineer's session, open a thread in [Discussions](https://github.com/mrazakhan/ContinuumAI/discussions) and tell us what you are running. We are particularly interested in cases where the same gotcha keeps surfacing across team members. Those are the highest-value places to drop a skill, and they are exactly the workloads we want to design the next iteration of the loop around.
