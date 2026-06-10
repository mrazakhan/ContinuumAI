# AI agents are amnesiacs. We measured a fix that lets them compound knowledge across sessions.

*Post 1 of 3 in the ContinuumAI series. Published 2026-06-02.*

## The amnesiac problem

Every modern LLM coding agent — *Cursor, Claude Code, Aider, OpenHands, Codex, the one your platform team is building in-house* — shares one limiting structural property: **no memory across sessions.**

Each task starts from scratch. The agent works through a problem, makes mistakes, eventually finishes (or doesn't), and then everything it learned in that session evaporates the moment the conversation ends.

**For an individual developer this is mildly annoying:**

- Your agent reaches for `pip` even though your repo has been on `uv` since spring — or for `jest` even though you migrated to `vitest` last quarter — every new session, same wrong tool, fresh
- It re-proposes the dead-end approach you and your team explicitly rejected on Slack three weeks ago, because nothing in its context remembers any of that
- You spend more time re-explaining the project's basics — *which logger, which test runner, which branch ships to prod, where the deploy script actually lives* — than you spend on the actual change you opened the chat for

**For an engineering organization this is significantly more expensive:**

- Every engineer's agent runs through the same gotcha library independently
- The skill your senior engineer's agent acquired last quarter does **not** transfer to the junior engineer's agent next quarter
- The institutional knowledge your humans accumulate across PRs, postmortems, design reviews, and onboarding wikis has no analog for agents
- ***Your humans compound. Your agents do not.***

The absence of that compounding shows up in the most common pilot postmortem we hear from engineering leaders:

> *"The agent worked great for the first two weeks. By month six it felt like the same agent we started with, doing the same tasks, getting tripped up by the same things."*

Of course it did. There was no mechanism for it to be anything else.

**The bigger model is not the fix.** Frontier closed models can already solve essentially every Terminal-Bench 2.1 task if you give them enough tokens. The gating constraint — increasingly — is whether the *system* can carry yesterday's lesson into today.

That five-line note — the one your senior engineer would write after spending forty minutes on a gotcha — is the missing piece.

## What ContinuumAI does

**ContinuumAI is the glue mechanism between agent sessions.** It captures what an agent learned in one session and makes it available to every related session that follows — *automatically, in the background, with no human curation step.*

The loop:

```mermaid
flowchart LR
    A([Agent session ends<br/>pass or fail]) --> B[Trajectory<br/>captured]
    B --> C[Reflector LLM<br/>extracts single<br/>load-bearing insight]
    C --> D[SkillCreator LLM<br/>writes SKILL.md<br/>file]
    D --> E[(Skill library<br/>+1 skill)]
    E -. loaded automatically<br/>at the start of every<br/>related session .-> A
```

Two LLM calls. One Markdown file out per session. The library accumulates: skills authored at 11 p.m. on a Tuesday are available to your colleague's agent at 9 a.m. on Wednesday. The same SKILL.md works regardless of which model your routing layer (*OpenRouter, AWS Bedrock, direct providers*) hands the next request to.

**What the loop is NOT:**

- ❌ No model weights touched, no fine-tuning, no RL
- ❌ No vector store, no embedding database
- ❌ No human curation, no manual playbook maintenance
- ❌ No vendor lock-in — skills are plain Markdown files in a folder

## The compounding cost advantage

Without the glue, **every agent session pays the cost of re-discovering the same problems**. The dollar cost compounds badly — an enterprise running thousands of agent sessions a day across hundreds of engineers is paying for the same gotcha to be discovered N times over. The wall-clock cost is worse: every developer waits while the agent re-explores what was already known.

**With the glue, that cost is paid once.**

| Audience | What changes |
|---|---|
| **Individual developer** | An hour saved every time a repeated gotcha shows up; an agent that grows quietly sharper at *your* stack week after week |
| **Engineering organization** | Monthly agent inference bill drops meaningfully (we quantify this in Post 2); institutional knowledge becomes a *capturable, replayable, auditable artifact* the same way commits are; team-wide compounding starts happening across every PR |

The ROI shape is unusual for an AI product: **it improves the longer you run it, without model upgrades.**

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

A **+4.6-point lift** on a benchmark at this hardness — *from a single failure trajectory per task, with no iterative refinement and no validation gate* — is the headline. For context, published results in this research area have reported:

- **+9 points** for trajectory-only approaches on the easier predecessor benchmark (TB-2.0) [1]
- **+9 to +25 points** for iterative-gated approaches on broader benchmark suites (search QA, spreadsheets, ALFWorld), depending on benchmark and gating strictness [2]

Our +4.6 sits below both, which is expected: *TB-2.1 is harder than TB-2.0, our loop is simpler (no gate), and the executor is GLM-5.1 rather than a frontier closed model.* The signal we wanted was the loop works at all on a hard benchmark with an open-weight executor — and it does.

### Two findings worth flagging

**🔑 The author model matters less than you would expect.**
Self-authoring (GLM-5.1 writing its own skills, B) captures *about three-quarters* of the lift that Opus-authoring (C) provides. The skill is the asset; the author is a multiplier, not a gate. Implications:

- Individual developers and small teams can run the loop end-to-end on cheap open-weight models — *no frontier API call ever required*
- Enterprises with privacy constraints get a defensible *"we do not need to send private trajectories to a frontier API"* answer
- The economics work without dependency on any single model vendor

**⚠️ Some skills regress their target tasks.**
A small number of tasks where the unaided baseline already passed 2 of 3 attempts ended up passing only 1 of 3 after a skill was loaded. The current loop ships every skill the author produces — *no validation gate yet* — so this is the expected failure mode of the simplest version. The next iteration adds the gate (iterative-refinement approach from [2]); we expect it to close most of the gap to the +9-to-+25 numbers reported in that literature.

## Our north star

**An agent that is *yours*.** Not generic. Not whatever some model vendor trained on the public internet. An agent whose value comes from accumulating the specific knowledge of *your* codebase, *your* team, *your* failures — and that gets sharper every quarter without anyone retraining anything.

That requires:

- ✅ A **persistent, accumulating skill library** scoped per-project, per-team, per-org *(first version shipped)*
- ✅ **Automatic capture from every session** — not opt-in, not manual *(covered above)*
- 🚧 **Validation-gated skill acceptance** so the library never regresses *(next iteration)*
- ✅ **Cross-model transferability** so skill investments survive model upgrades *(by design — quantified in Post 2)*
- 🚧 **Per-team and per-org scoping with access controls** *(in design — relevant for the enterprise rollout)*

The +4.6-point measurement on TB-2.1 is the first public proof point. The measurement we eventually care about is what happens *quarter over quarter* in a team that runs the loop in production — where lessons compound, where one engineer's hard-won debugging session bootstraps every other engineer's agent, and where the value of the system grows along an axis that has nothing to do with the next model release.

That is what ContinuumAI is built to do.

## What's next

- **Post 2** — *the cost story:* what happens to your monthly agent inference bill when an open-weight executor + skills replaces a frontier closed model
- **Post 3** — *case studies:* individual skills with full SKILL.md text — what worked, what regressed, why
- **Bonus** — *the 65 % budget anomaly:* a methodology finding from this run that should change how you read every other agent benchmark

## References

[1] *Skill Learning* — Letta, 2026. https://www.letta.com/blog/skill-learning
[2] *SkillOpt: Optimizing Natural-Language Skills as the Trainable State of Frozen Agents* — Microsoft Research, 2026. https://microsoft.github.io/SkillOpt/ · paper: https://arxiv.org/abs/2605.23904

## Closing

The amnesiac problem is not a curiosity. It is the single biggest reason organizations report that AI agent pilots *"did not work out"* after six months — the agents are useful at first, but they never compound. They never become *the senior engineer's agent that has been in the trenches.* They stay junior forever.

**ContinuumAI is the glue mechanism that fixes that.** Skills accumulate across every developer on your team, every model in your routing layer, and every quarter the system runs. The agent gets meaningfully better at *your* stack every time anyone on your team uses it.

If you're an individual developer tired of re-explaining the same gotchas, or an engineering leader watching the same skill rediscover itself across every engineer's session, open a thread in [Discussions](https://github.com/mrazakhan/ContinuumAI/discussions) and tell us what you're running. We are particularly interested in cases where the same gotcha keeps surfacing across team members — those are the highest-value places to drop a skill, and exactly the workloads the next iteration of the loop is being designed around.
