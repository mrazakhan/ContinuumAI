# AI agents are amnesiacs.

*Post 1 of 3 in the ContinuumAI series. Published 2026-06-02.*

## The amnesiac problem

Pick any coding agent you might be using — *Cursor, Claude Code, Aider, OpenHands, Codex, whatever your platform team is building in-house* — and they all share one structural property: **no memory across sessions.**

Each task starts from scratch. The agent works through the problem, makes mistakes, eventually finishes (or doesn't), and then everything it learned evaporates the moment the conversation ends.

There are partial fixes you've probably tried: longer context windows that let the agent see more within a single session; project-level rules files (Cursor's `.cursorrules`, Claude Code's `CLAUDE.md`, Aider conventions, etc.); RAG-style retrieval over your docs and codebase; persistent chat memory features built into the agent platform. All of them are ad-hoc — written by hand, maintained by hand, updated whenever a developer remembers to add the gotcha they just hit. The agent itself never contributes to any of them. Whatever it learns in a session evaporates the moment the chat ends, and the next session starts from whatever a human happened to write down yesterday.

**For an individual developer this is annoying:**

- Your agent reaches for `pip` even though your repo has been on `uv` since spring — or for `jest` even though you migrated to `vitest` last quarter — every new session, same wrong tool, fresh
- It re-proposes the dead-end approach you and your team explicitly rejected on Slack three weeks ago, because nothing in its context remembers any of that
- You spend more time re-explaining the project's basics — *which logger, which test runner, which branch ships to prod, where the deploy script actually lives* — than you spend on the actual change you opened the chat for

**For an engineering team it's all of the above, multiplied across N engineers — plus a few more:**

- Every engineer's agent runs through the same gotcha library independently
- The skill your senior engineer's agent acquired last quarter does **not** transfer to the junior engineer's agent next quarter
- Your humans build up institutional knowledge across PRs, postmortems, design reviews, and onboarding wikis — and there's no equivalent for agents
- ***Your humans compound. Your agents do not.***

This is the pattern we keep seeing in agent pilots: useful out of the gate, then a plateau that never quite breaks. The agent keeps doing the same tasks and keeps getting tripped up by the same things. A bigger model would knock out some of those — but it wouldn't fix the underlying issue, which is that nothing carries from one session to the next.

That structural part doesn't go away with a model upgrade. It goes away when the system starts remembering.

**And throwing a bigger model at it doesn't help.** Frontier models can already chew through most Terminal-Bench 2.1 tasks if you give them enough tokens. Capability isn't the bottleneck. The bottleneck is that nothing about the *system around the model* carries yesterday's lesson into today.

What's missing is the five-line note your senior engineer would jot down after spending forty minutes on a gotcha. That's all a skill is, really.

## What ContinuumAI does

ContinuumAI is our attempt at giving agents memory across sessions. When a session ends, we read the trajectory, pull out the lesson that mattered most, and save it as a short file the next session can read. No human in the middle, no manual curation.

Here's the loop:

![The skill-generation loop: each agent session ends, the trajectory is captured, the Reflector extracts the single load-bearing insight, the SkillCreator writes a short SKILL.md file, the skill library grows by one, and the new skill is loaded at the start of the next related session.](assets/post-1-loop.png)

Each session adds one short Markdown file to the library. No model weights touched, no vector store, no human curation step — just plain text in a folder you can grep, version in git, or move to a different platform whenever you want.

## The compounding cost advantage

While agents keep starting from zero, **every session is paying to rediscover the same things**. The dollar cost gets ugly fast: a team running thousands of agent sessions a day across hundreds of engineers is paying for the same gotcha to get rediscovered, session after session after session. The wall-clock cost is worse — every developer sits there waiting while the agent re-treads ground that's already been covered.

**Once you capture the lesson once, that cost is paid once.**

| Audience | What changes |
|---|---|
| **Individual developer** | An hour saved every time a repeated gotcha shows up; an agent that grows quietly sharper at *your* stack week after week |
| **Engineering organization** | The monthly agent inference bill drops (we'll quantify this in Post 2). Institutional knowledge becomes something you can capture, replay, and audit — the same way commits are. And team-wide compounding starts kicking in across every PR. |

This is the unusual part: **the product gets more useful the longer you run it. No model upgrade required.**

## Measuring it on Terminal-Bench 2.1

To measure the loop we needed a benchmark that:

1. **Tests multi-step, long-horizon agent work** — so a skill has real content to encode
2. **Has a published frontier reference** — so any lift is interpretable
3. **Allows clean K-run aggregation** — so the numbers are comparable across teams

[Terminal-Bench 2.1](https://www.tbench.ai/leaderboard/terminal-bench/2.1) fits all three. 89 long-horizon coding and systems tasks: SQLite-WAL recovery, build-chain debugging, image-processing pipelines, reverse-engineering puzzles, network-protocol implementations, environment-configuration problems. Each task has a programmatic verifier. The current leaderboard top is *Codex CLI + GPT-5.5* at 83.4 %; second is *Claude Code + Opus 4.8* at **78.9 %**. Both run on frontier closed models.

We ran the experiment with **GLM-5.1 as the executor** across three conditions:

- **A — baseline**: GLM-5.1 with no skill loaded
- **B — GLM-authored skill**: GLM-5.1 reads a SKILL.md authored by GLM-5.1 from its own prior failure
- **C — Opus-authored skill**: GLM-5.1 reads a SKILL.md authored by Claude Opus 4.6 from the same prior failure

K=3 attempts per task. TB-standard aggregated score. 87 of 89 tasks measured under every condition.

### Results

| Stack | TB-2.1 aggregated score | Lift vs baseline |
|---|---|---|
| Claude Opus 4.8 (leaderboard #2) | 78.9 % | *frontier reference* |
| **A**: GLM-5.1 baseline (no skill) | **59.4 %** | — |
| **B**: GLM-5.1 + GLM-authored skill | **62.8 %** | **+3.4 pp** |
| **C**: GLM-5.1 + Opus-authored skill | **64.0 %** | **+4.6 pp** |

![Terminal-Bench 2.1 aggregated score by condition: A baseline at 59.4 %, B GLM-skill at 62.8 % (+3.4 pp), C Opus-skill at 64.0 % (+4.6 pp), and Claude Opus 4.8 frontier reference at 78.9 %.](assets/post-1-accuracy.png)

**+4.6 points** is the headline. That's what we got from one failure trajectory per task, with no refinement loop and no validation gate, on a benchmark this hard.

How does +4.6 compare to what's been published? Trajectory-only approaches on the easier predecessor benchmark (TB-2.0) have come in around **+9 points** [1]. Iterative-gated approaches on broader benchmark suites — search QA, spreadsheets, ALFWorld — have reported anywhere from **+9 to +25 points**, depending on the benchmark and how strict the gating is [2].

Our +4.6 lands below both, which makes sense — TB-2.1 is harder than TB-2.0, our loop is simpler (no gate), and we're running GLM-5.1 instead of a frontier closed model. The signal we wanted was that the loop works at all on a hard benchmark with an open-weight executor — and it does.

### Two findings from the run worth flagging

**🔑 The author model matters less than you'd expect.**
Self-authoring (GLM-5.1 writing its own skills, B) captures *about three-quarters* of the lift that Opus-authoring (C) provides. The skill is the asset; the author is a multiplier on it, not a gate to it. What this means in practice:

- Individual developers and small teams can run the whole loop on a cheap open-weight model — *no frontier API call required, ever*
- Enterprises with privacy constraints have a defensible *"we don't have to send private trajectories to a frontier API"* answer
- The economics don't depend on any single model vendor staying cheap

**⚠️ Some skills regress their target tasks.**
A handful of tasks where the unaided baseline already passed 2 of 3 attempts ended up passing only 1 of 3 once a skill was loaded. The current loop ships every skill the author produces — *no validation gate yet* — so this is the expected hiccup of the simplest version. Adding the gate (the iterative-refinement approach in [2]) is the next iteration, and we expect it to close most of the gap to the +9-to-+25 numbers reported in that literature.

## Our north star

The agent we're trying to build is the one that's *yours*. Not generic, not whatever some model vendor trained on the public internet — but an agent whose value comes from accumulating the specific knowledge of your codebase, your team, your past failures. One that gets sharper every quarter without anyone retraining anything.

To get there, the system needs:

- ✅ A **persistent, accumulating skill library**, scoped per-project, per-team, per-org *(first version shipped)*
- ✅ **Automatic capture from every session** — not opt-in, not manual *(covered above)*
- 🚧 **Validation-gated skill acceptance** so the library never regresses *(next iteration)*
- ✅ **Cross-model transferability** so skill investments survive model upgrades *(by design — quantified in Post 2)*
- 🚧 **Per-team and per-org scoping with access controls** *(in design — for the enterprise rollout)*

The +4.6-point lift on TB-2.1 is the first public sign that the loop works. The one we actually care about is what happens *quarter over quarter* in a team running this in production — lessons compound, one engineer's hard-won debug session bootstraps every other engineer's agent, and the system gets more valuable in a direction that has nothing to do with the next model release.

That's what we're building toward.

## What's coming up

Two more posts in this series, plus a methodology bonus dropping out of band:

- **Post 2 — what this actually costs.** I'll put the per-attempt and per-passed-task dollars from this run next to what those same tasks would cost on Opus 4.8 at the same token usage. If the line item *"agent inference"* on your monthly bill matters, this is the post to wait for.
- **Post 3 — what the skills actually look like.** I'll walk through a handful of individual SKILL.md files — the failure trajectories they came from, what each one teaches in plain English, why a couple of them regressed. Useful if you want to understand what skill-learning actually encodes (and what it doesn't).
- **Bonus — the 65 % budget anomaly.** A methodology finding from this run that I think most teams haven't accounted for. If your team trusts or publishes agent benchmark numbers, you'll want this one before your next publication.

## References

[1] Letta (2026). [*Skill Learning*](https://www.letta.com/blog/skill-learning).

[2] Microsoft Research (2026). [*SkillOpt: Optimizing Natural-Language Skills as the Trainable State of Frozen Agents*](https://microsoft.github.io/SkillOpt/). [arXiv:2605.23904](https://arxiv.org/abs/2605.23904).

## Closing

The amnesiac problem isn't a curiosity. It's one of the biggest reasons agent pilots quietly stall — the agents are useful at first, then they plateau. They never become *the senior engineer's agent that's been in the trenches*. They stay junior forever.

That's what ContinuumAI is built to change. Skills accumulate — across every developer on your team, every model in your routing layer, every quarter the system runs. The agent gets noticeably better at *your* stack every time anyone on your team uses it.

If you're an individual developer tired of re-explaining the same gotchas, or an engineering leader watching the same skill rediscover itself across every engineer's session, come open a thread in [Discussions](https://github.com/mrazakhan/ContinuumAI/discussions) and tell us what you're running. We're particularly interested in cases where the same gotcha keeps surfacing across team members — those are the highest-value places to drop a skill, and they're exactly the workloads the next iteration of the loop is being designed around.
