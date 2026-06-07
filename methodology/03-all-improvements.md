# All Tier-1 and Tier-2 task improvements

**Updated 2026-06-02** — numbers regenerated from canonical aggregation script.

## Source of truth

All numbers below come from [`scripts/aggregate_canonical.py`](../../scripts/aggregate_canonical.py) → [`canonical-results.json`](canonical-results.json) ([readable summary](canonical-results.md)). The earlier headline numbers in this file (47.2 % / 50.9 % / 55.1 % / 55.8 %) were synthesized arithmetically and could not be reproduced from raw data; they are superseded by the canonical script's output. **Single source of truth, deterministic, anyone can clone and reproduce.**

Methodology: TB-standard aggregated score = per-task mean of first up-to-K=3 attempts, with per-task source precedence (skill condition > recovery K=1 > baseline). Coverage: 87 of 89 tasks measured under every condition; 2 errored everywhere (`extract-moves-from-video`, `path-tracing`).

## Headline (89-task aggregated score, TB-standard, K=3)

| Method | Score (87 measured) | Score (missing → 0) | Δ vs baseline |
| - | - | - | - |
| **A**: GLM-5.1 baseline (best-of-condition baseline) | **59.4 %** | 58.1 % | — |
| **B**: + GLM-authored skill | **62.8 %** | 61.4 % | **+3.4 pp** |
| **C**: + Opus-4.6-authored skill | **64.0 %** | 62.6 % | **+4.6 pp** |
| *Frontier reference: Claude Opus 4.8 on TB-2.1 leaderboard (#2)* | *78.9 %* | — | *frontier* |
| *Letta TB-2.0 trajectory-only (reference)* | *~42 % inferred* | *—* | *+9 pp (on TB-2.0)* |

**Key reads:**
- **Skill-only lift, C-author: +4.6 pp** over the recovered open-weight baseline. Comparable to Letta's published TB-2.0 trajectory-only lift, on a harder benchmark, with no validation gate.
- **Frontier gap**: 64.0 / 78.9 = **81 % of frontier accuracy**. Cost: 1 / 4.4 = **23 % of per-token cost** (OpenRouter list pricing applied to our actual token usage).
- **B captures ~75 % of C's lift** — self-authored skills work most of the time; you don't need a frontier author to get most of the value.
- The earlier "+8.6 pp" claim was an arithmetic error (composing baseline-budget delta onto a skill-condition score that already excluded those tasks); honest skill-only lift is **+4.6 pp**.

## Recovery pass — what we found

Re-ran 23 tasks (8 Tier-1 timeouts + 15 Tier-2 missing-skill) at 60-min agent budget (vs default 30-min). Outcome:

| Outcome | Count | Tasks |
| - | - | - |
| 🟢 Solved at K=1 with longer budget (reclassify) | **15** | adaptive-rejection-sampler, build-cython-ext, crack-7z-hash, fix-code-vulnerability, kv-store-grpc, large-scale-text-editing, largest-eigenval, llm-inference-batching-scheduler, mailman, prove-plus-comm, pytorch-model-recovery, qemu-alpine-ssh, qemu-startup, vulnerable-secret, winning-avg-corewars |
| 🟡 New failure trajectory (skill candidate) | 2 | pytorch-model-cli, torch-pipeline-parallelism |
| 🔴 Still timed out at 60 min | 4 | gcode-to-text, gpt2-codegolf, raman-fitting, train-fasttext |
| ⚠️ Errored | 2 | extract-moves-from-video, path-tracing |

**Most important finding: 15 of 23 (65%) were budget-starved, not failed.** The default 30-min agent timeout systematically misclassified them. This adds **+3.7 pp** to the *true* baseline before any skill is applied.

**Skills generated for the 2 new candidates (pytorch-model-cli, torch-pipeline-parallelism) are TODO** — the tier_ready.json files were frozen before recovery, so the generators skipped them. Adding them would lift B by ~+0.5 pp more.

## Tier 1 — capability (22 tasks)

*Baseline: 0/3 for all (pass@any = 0 by definition).*

| task | B (GLM-skill) | C (Opus-skill) | Winner |
| - | - | - | - |
| break-filter-js-from-html | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| caffe-cifar-10 | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| cancel-async-tasks | 🟡 [0, 0, 1] | ✅ [1, 1, 1] | C |
| circuit-fibsqrt | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| db-wal-recovery | ✅ [1, 1, 1] | 🟡 [1, 1, 0] | B |
| dna-assembly | 🟡 [1, 0, 0] | ❌ [0, 0, 0] | B |
| dna-insert | 🟡 [1, 0, 0] | ❌ [0, 0, 0] | B |
| filter-js-from-html | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| fix-ocaml-gc | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| install-windows-3.11 | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| make-doom-for-mips | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| make-mips-interpreter | ❌ [0, 0, 0] | 🟡 [0, 1, 0] | C |
| mcmc-sampling-stan | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| mteb-leaderboard | 🟡 [0, 1, 0] | ❌ [0, 0, 0] | B |
| mteb-retrieve | 🟡 [1, 0, 0] | ✅ [1, 1, 1] | C |
| protein-assembly | 🟡 [0, 1, 0] | 🟡 [0, 0, 1] | tied |
| regex-chess | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| rstan-to-pystan | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| schemelike-metacircular-eval | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| tune-mjcf | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| video-processing | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| write-compressor | ❌ [0, 0, 0] | 🟡 [0, 0, 1] | C |

**Tier 1 aggregate:** B pass@3 7/22 (31%) / pass^3 1/22 (4%); C pass@3 6/22 (27%) / pass^3 2/22 (9%)

## Tier 2 — reliability (15 tasks with skills, of 30 candidates)

*Baseline: pass@any=1 but pass^3=0. Goal: lift to pass^3=1.*

| task | Baseline | B (GLM-skill) | C (Opus-skill) | Winner |
| - | - | - | - | - |
| build-pov-ray | 🟡 [0, 1, 1] | 🟡 [1, 0, 0] | 🟡 [0, 1, 0] | tied |
| chess-best-move | 🟡 [0, 0, 1] | 🟡 [1, 0, 0] | 🟡 [1, 0, 1] | C |
| compile-compcert | ❌ [0, 0, 0] | ❌ [0, 0, 0] | ❌ [0, 0, 0] | — |
| configure-git-webserver | 🟡 [0, 1, 1] | ❌ [0, 0, 0] | 🟡 [1, 0, 0] | C |
| constraints-scheduling | 🟡 [0, 1, 0] | ✅ [1, 1, 1] | ✅ [1, 1, 1] | tied |
| count-dataset-tokens | 🟡 [0, 1, 1] | ✅ [1, 1, 1] | ✅ [1, 1, 1] | tied |
| feal-linear-cryptanalysis | 🟡 [1, 1, 0] | 🟡 [0, 0, 1] | ❌ [0, 0, 0] | B |
| log-summary-date-ranges | 🟡 [1, 1, 0] | 🟡 [0, 1, 1] | ✅ [1, 1, 1] | C |
| openssl-selfsigned-cert | 🟡 [1, 0, 1] | 🟡 [0, 1, 1] | 🟡 [1, 0, 1] | tied |
| overfull-hbox | 🟡 [1, 1, 0] | ✅ [1, 1, 1] | 🟡 [0, 1, 1] | B |
| password-recovery | 🟡 [1, 1, 0] | 🟡 [1, 1, 0] | 🟡 [1, 0, 1] | tied |
| polyglot-rust-c | 🟡 [0, 1, 1] | 🟡 [1, 0, 0] | ✅ [1, 1, 1] | C |
| query-optimize | 🟡 [1, 0, 1] | 🟡 [1, 1, 0] | ❌ [0, 0, 0] | B |
| sqlite-with-gcov | 🟡 [1, 0, 0] | 🟡 [1, 1, 0] | 🟡 [1, 1, 0] | tied |
| torch-tensor-parallelism | 🟡 [0, 1, 0] | ✅ [1, 1, 1] | 🟡 [0, 1, 1] | B |

**Tier 2 aggregate (over 15 measured):** B pass@3 13/15 (86%) / pass^3 4/15 (26%); C pass@3 12/15 (80%) / pass^3 4/15 (26%)
