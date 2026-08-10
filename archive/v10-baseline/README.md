# v10 baseline artifacts (2026-08-10)

Archived because `runs/` is gitignored. These are the evidence behind the
`v10-baseline` tag. Each directory holds `run.json` (exact case definitions,
prompt config, sampling), `trace.jsonl` (per-call request/output, usage, tool
results) and `summary.json` (per-case failures and metrics).

## Valid runs

| Run | Model | Harness | Task success |
|---|---|---|---|
| `v10-rwkv13b-boundary` | rwkv7-g1i-13.3b | v10 | **13/18** |
| `v10-deepseek-v4flash-boundary` | deepseek-v4-flash | v10 | **17/18** |
| `v9-rwkv13b-buffered-boundary` | rwkv7-g1i-13.3b | v9 | 10/18 |
| `v9-deepseek-v4flash-boundary` | deepseek-v4-flash | v9 | 13/18 |
| `cmp-rwkv13b-think-boundary` | rwkv7-g1i-13.3b | v8 | 10/18 |
| `cmp-deepseek-v4flash-think-boundary` | deepseek-v4-flash | v8 | 14/18 |

v8/v9/v10 scores are not comparable across versions: v9 changed protocol
convergence, v10 relaxed discovery-tool scoring. Compare within a version only.

The v8 RWKV run additionally had integer `stop_tokens` rejected by the server,
so it degraded to client-side stop matching with no server-side stops.

## Discarded runs (not archived)

Four RWKV runs from this session were invalidated by environment faults, not
model behaviour. Kept here as a record so the scores are not mistaken for
regressions:

- `cmp-rwkv13b-think-textstops` — 0/18, server SSE returned empty bodies.
- `v9-rwkv13b-think-boundary` — 0/18, client bug: an enabled server-side stop is
  consumed without being echoed, so every route read as an unclosed envelope.
- `v9-rwkv13b-think-boundary-fix` — 5/18, 10 cases lost to a proxy switch.
- `v9-rwkv13b-boundary-retry` — 6/18, the SSE degradation recurred mid-run.

The streaming fault is why `--api-stream=false` exists; the v10 runs use it.
