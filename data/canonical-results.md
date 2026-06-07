# Canonical aggregate — single source of truth

K=3; methodology: per-task mean of first up-to-K=3 attempts; source precedence skill > recovery K=1 > baseline.

## Headline (TB-standard aggregated score on 89 tasks)

| Config | Pass rate (measured) | Pass rate (missing→0) | $ / attempt (GLM actual) | $ / attempt (Opus 4.8 hypothetical) | Ratio | n_measured / 89 |
|---|---|---|---|---|---|---|
| **A_baseline** | **59.39%** | 58.05% | $0.3628 | $1.5588 | 4.30× | 87/89 |
| **B_GLM_skill** | **62.84%** | 61.42% | $0.3929 | $1.7442 | 4.44× | 87/89 |
| **C_Opus_skill** | **63.98%** | 62.55% | $0.3705 | $1.6359 | 4.42× | 87/89 |

*Frontier reference: Claude Opus 4.8 on TB-2.1 leaderboard #2 = 78.9% (cost not published).*

## Source-of-score breakdown per config

### A_baseline
- baseline-orig: 63 tasks
- baseline-longt: 24 tasks
- missing: 2 tasks
- missing: ['extract-moves-from-video', 'path-tracing']

### B_GLM_skill
- B-skill: 36 tasks
- baseline-orig: 29 tasks
- recovery-K1: 14 tasks
- baseline-longt: 7 tasks
- missing: 1 tasks
- fallback-missing: 1 tasks
- fallback-baseline-longt: 1 tasks
- missing: ['extract-moves-from-video', 'path-tracing']

### C_Opus_skill
- C-skill: 36 tasks
- baseline-orig: 29 tasks
- recovery-K1: 14 tasks
- baseline-longt: 7 tasks
- missing: 1 tasks
- fallback-missing: 1 tasks
- fallback-baseline-orig: 1 tasks
- missing: ['extract-moves-from-video', 'path-tracing']
