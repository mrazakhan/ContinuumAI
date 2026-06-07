# Three deep-dive case studies — pass^3: 0 → 1

**Date:** 2026-05-30 (case-study analyses) / **Updated 2026-05-31** with recovery-pass framing
**Scope:** Three Tier-1/Tier-2 tasks where a single trajectory-only skill changed the executor's outcome from *never* (or *unreliably*) solving to **all 3 attempts pass cleanly**. The three are chosen to surface distinct stories: (1) pure capability gain, (2) Opus-skill beats GLM-skill, (3) Opus root-cause analysis beats GLM generic advice.

> **Note on framing:** these three tasks are real skill wins — none of them was solved by the budget-recovery pass (see [03-all-improvements.md](03-all-improvements.md)). The recovery pass tells us **how much of the gross gain was budget-fix vs skill-fix**; the case studies below isolate what the *skill itself* contributed.

---

## Case 1 — `db-wal-recovery` (Tier 1, B wins decisively)

**The task:** Recover data from a SQLite WAL-mode database where the WAL file is corrupted or encrypted. The verifier checks that a specific number of records was reconstructed.

**Baseline behavior (no skill):**
- 3 of 3 attempts: reward = 0
- Failure mode: GLM opened the database directly with `sqlite3`, which silently discarded the unreadable WAL on close — **permanently destroying the WAL data** before any analysis could happen.

**B-skill (GLM-authored)** — `skills/day20-tier1-glm/db-wal-recovery/sqlite-wal-recovery/SKILL.md`

> *"Opening a WAL-mode SQLite database causes it to process the WAL file. If the WAL is corrupted, SQLite silently discards it and deletes the file on close — permanently losing the data. Always make byte-level backups of ALL related files (db, -wal, -shm) before any sqlite3 access. Then analyze the raw WAL bytes on the backup, and only open a copy of the database, never the originals."*

The skill encoded the **single load-bearing insight** (back up before any `sqlite3` invocation) and a 5-step procedure for raw-WAL parsing.

**B-skill result:** **`[1.0, 1.0, 1.0]` — pass^3 = 1.** Full reliability.

**C-skill (Opus-authored)** identified the same root cause but with slightly different procedure; result was `[1.0, 1.0, 0.0]` — pass@3 but not pass^3.

**Read:** Pure **capability win** — went from *unsolvable* in baseline to *fully reliable* with skill. The GLM author happened to land on a marginally crisper procedural sequence here. The single insight ("backup first") was load-bearing in both cases.

---

## Case 2 — `mteb-retrieve` (Tier 1, C wins reliability)

**The task:** Use the `mteb` library to load a BGE embedding model and rank documents by similarity to a query. The verifier compares the produced rankings to expected output.

**Baseline behavior (no skill):**
- 3 of 3 attempts: reward = 0
- Failure mode: GLM imported `sentence_transformers.SentenceTransformer` directly instead of going through `mteb`. This **skipped the model-specific query-prefix preprocessing** that BGE expects (the literal Chinese instruction `"为这个句子生成表示以用于检索相关文章："`). Without the prefix, the query embedding is wrong → rankings are wrong.

**B-skill (GLM-authored)** — `mteb-mandatory-encode/SKILL.md`

> *"mteb applies model-specific preprocessing (e.g., query instruction prefixes for BGE models …) that `sentence_transformers.SentenceTransformer.encode()` does not. Using the wrong loader produces different embeddings and incorrect similarity rankings. When a task mandates mteb, you must use mteb's encoder API — not the underlying library directly."*

**B-skill result:** `[1.0, 0.0, 0.0]` — pass@3 = 1, but pass^3 = 0. Got it right once, missed twice.

**C-skill (Opus-authored)** — `mteb-model-loading-encoding/SKILL.md`

Same principle, but with a more concrete code example (`prompt_name="query"` for the query side) and tighter procedural steps.

**C-skill result:** **`[1.0, 1.0, 1.0]` — pass^3 = 1.** Full reliability.

**Read:** **Opus-skill produces more reliable outcomes than GLM-skill on the same task.** Both identified the same conceptual gap, but the Opus skill's more concrete code template appears to remove the variance that left GLM-skill at 1/3 attempts. This is the canonical "stronger-reasoning author = more reliable skill" pattern.

---

## Case 3 — `polyglot-rust-c` (Tier 2, C wins by identifying the actual root cause)

**The task:** Write a single file that compiles and runs as both Rust and C. Verifier runs the exact build commands from the task spec.

**Baseline behavior (no skill, with thinking):**
- `[0.0, 1.0, 1.0]` — solves 2 of 3 attempts. Sometimes works, sometimes fails.

**B-skill (GLM-authored)** — `test-with-exact-task-commands/SKILL.md`

> *"Verifiers re-run the exact commands from the task specification. If you test with altered commands (e.g., adding `-o <custom_name>` to change the output path), you may miss failures that only appear with the default output path …"*

GLM's diagnosis: the agent was using non-spec output paths in testing. The skill's procedure: "use the exact build commands from the spec."

**B-skill result:** **`[1.0, 0.0, 0.0]` — pass@3 = 1, pass^3 = 0. *Regressed* from baseline 2/3 to 1/3.** The generic advice ("just follow the spec") wasn't actionable enough to prevent the underlying failure.

**C-skill (Opus-authored)** — `rustc-qemu-linker-crash/SKILL.md`

> *"In QEMU user-mode emulated environments, the default C linker (`cc`) invoked by `rustc` can crash with SIGSEGV due to jemalloc's `MADV_DONTNEED` syscall not working correctly under emulation. The telltale sign is `<jemalloc>: MADV_DONTNEED does not work` in stderr. The fix is to either configure jemalloc, use an alternative linker, or avoid the problematic linking step."*

Opus identified the **actual root cause**: a jemalloc/QEMU interaction crashing the linker in the containerized environment. Concrete fix: `export MALLOC_CONF="retain:false,abort_conf:false"`.

**C-skill result:** **`[1.0, 1.0, 1.0]` — pass^3 = 1.** Full reliability, ahead of baseline.

**Read:** **Skill quality dominates.** GLM's skill misdiagnosed the failure (it saw output-path differences and assumed they were causal); Opus's skill correctly identified an obscure infrastructure interaction (jemalloc + QEMU + cc linker) and gave a concrete environment fix. The B-skill case actively *hurt* baseline performance — a real "wrong skill is worse than no skill" data point. The C-skill case fixed the underlying flake.

---

## What ties the three together

| Lever | Case 1 | Case 2 | Case 3 |
| - | - | - | - |
| Did baseline ever solve it? | never | never | sometimes (2/3) |
| Did the *insight* matter more than the *prose*? | yes (both authors got it) | no (insight matched, prose differed) | yes (Opus had right insight, GLM didn't) |
| Did GLM-skill or Opus-skill win? | tied conceptually; B's procedure was tighter here | **C** by reliability | **C** by capability and reliability |
| Letta-comparable lift on this task | +100% reliability | +100% reliability | +100% reliability |

**The composite pattern across all our pass^3 wins:** when the skill correctly diagnoses the single load-bearing failure mode *and* provides a concrete procedure, the executor reliably succeeds. When either step is weak (generic insight or vague procedure), the skill at best gives a single lucky pass, at worst regresses.
