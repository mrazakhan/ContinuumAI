# ContinuumAI

**Solving amnesia for coding agents.** An open-weight stack with a learned-from-failure skill loop, measured at roughly **80 % of the top frontier model's score** on Terminal-Bench 2.1 — at a fraction of the inference cost.

## Read the launch post

→ **[BLOG.md](BLOG.md)** — *AI agents are amnesiacs.*
First post in a three-part series. Covers the amnesia problem, the skill-generation loop, the Terminal-Bench 2.1 measurement, and what comes next.

## Headline result

| Stack | TB-2.1 score | Lift |
|---|---|---|
| Claude Opus 4.8 (TB-2.1 leaderboard #2, frontier reference) | 78.9 % | — |
| GLM-5.1 baseline (no skill) | 59.4 % | — |
| GLM-5.1 + GLM-authored skill | 62.8 % | +3.4 % |
| **GLM-5.1 + Opus-authored skill** | **64.0 %** | **+4.6 %** |

89 long-horizon coding and systems tasks; K=3 attempts per task; 87 measured under every condition. Skills are generated only from failed runs, not from worked solutions — no solution leakage between skill authoring and measurement.

## The series

| Post | Topic | Status |
|---|---|---|
| **Post 1** | The amnesia problem and the accuracy measurement | **Live in [BLOG.md](BLOG.md)** |
| Post 2 | Cost economics: per-attempt and per-passed-task dollars | Coming |
| Post 3 | Inside individual SKILL.md files — what each one teaches, and the regression cases | Coming after Post 2 |

## The mechanism in one paragraph

After each agent session ends, a Reflector LLM call reads the session trajectory and extracts the single load-bearing lesson from the failure. A SkillCreator LLM call writes that lesson as a short Markdown file (SKILL.md). The next related session loads the file before starting. The library grows by one per session — no model weights touched, no fine-tuning, no RL, no vector store, no human curation step. Skills are plain Markdown files that work with any model your routing layer (OpenRouter, AWS Bedrock, a direct provider) hands the next request to.

## Get in touch

Open a thread in **[Discussions](https://github.com/mrazakhan/ContinuumAI/discussions)** if any of the following sound like your stack:

- An individual developer tired of re-explaining the same gotchas to the same agent every Tuesday
- An engineering organization running a pilot that plateaued at *"still rediscovering the same skills six months in"*
- A team that publishes or trusts agent benchmark numbers (worth a separate conversation on measurement methodology)

## License

Apache 2.0.
