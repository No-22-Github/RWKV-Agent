# 迁移中删除的工具

docs/go-tooling-migration.md §2.5 / §2.6 删除的文件清单。保留在这里是为了以后能从 git 历史里找回：
`git show <commit>:<path>`。

## D 档：已出结论的一次性实验分析（24 个，不迁移）

| 文件 | 用途 | 最后改动 |
|---|---|---|
| `scripts/closeout-matrix.sh` | workbank closeout run matrix driver — sequential, one endpoint load profile. | `21da473` |
| `scripts/state-matrix.py` | Matched full-concurrency state matrix; keep failures, continue other arms. | `39bf2de` |
| `scripts/ablation-run-report.py` | Ablation-run analysis: per-category breakdown, run-to-run flips, prompt bytes. | `78e9644` |
| `scripts/wire-experiment.py` | Sequential online wire trials. | `39bf2de` |
| `scripts/wire-request-replay.py` | Replay a saved text request without executing generated tools. | `39bf2de` |
| `scripts/bfcl-m2-negative.py` | (no module docstring) | `65af7d1` |
| `bench/workbank/tools/closeout_metrics.py` | Closeout experiment metrics from agent-eval run artifacts. | `21da473` |
| `bench/workbank/tools/extract_failures.py` | Extract failed agent-eval trajectories into a reviewable bundle. | `b7e0005` |
| `bench/workbank/tools/first_step_metrics.py` | First-step information-source metrics for the S1 source-hint experiment. | `36e471d` |
| `bench/workbank/tools/check_user_runs.py` | Check the consecutive-User-run invariant of an eval run's model prompts. | `5a06547` |
| `bench/workbank/tools/evidence_probe_cases.py` | Build answer-only diagnostic cases, never a replacement workbank score. | `39bf2de` |
| `bench/workbank/tools/make_diagnostic_ladder.py` | Generate a separate 16-case diagnostic, never modify the frozen Workbank. | `94d3ad3` |
| `bench/workbank/tools/run_diagnostic_matrix.py` | Run no-state scoring/ladder diagnostics with the same binary and budgets. | `94d3ad3` |
| `bench/workbank/tools/summarize_diagnostic_matrix.py` | Summarize archived paired scoring, evidence and termination diagnostics. | `94d3ad3` |
| `bench/workbank/tools/summarize_budget_audit.py` | Offline execution/termination/token audit; never changes official scoring. | `94d3ad3` |
| `bench/workbank/tools/scorer_ablation.py` | Paired, offline scorer sensitivity on archived outputs; never reruns a model. | `94d3ad3` |
| `bench/workbank/tools/test_scorer_ablation.py` | (no module docstring) | `94d3ad3` |
| `bench/workbank/tools/state_alignment_audit.py` | Read-only full-corpus audit for the two supplied G1K state training exports. | `39bf2de` |
| `bench/workbank/tools/state_case_report.py` | Produce a reviewable per-case state comparison from original scored outputs. | `39bf2de` |
| `bench/workbank/tools/state_results.py` | Summarize completed state runs without treating transport/drift as model score. | `39bf2de` |
| `bench/workbank/tools/measure_anchor_agreement.py` | Anchor-agreement metrics for a workbank run: how well the first decision matches. | `167ee77` |
| `bench/workbank/tools/extract_anchors.py` | Wash out corpus rows whose prompt is byte-identical to a workbank eval prompt. | `167ee77` |
| `bench/workbank/tools/index_runs.py` | Generate an INDEX. | `123c93a` |
| `bench/workbank/tools/reparse.go` | Run with: go run. | `39bf2de` |

## A 档：已迁进 `rwkv-lab` 的旧实现

迁完即删，避免 Go 改了它们静默失效（§1）。新入口见 docs/go-tooling-migration.md §3。

| 文件 | 用途 | 最后改动 |
|---|---|---|
| `bench/workbank/tools/lint.py` | lint. | `bcc439a` |
| `bench/workbank/tools/test_lint.py` | test_lint. | `bcc439a` |
| `bench/workbank/tools/dedup.py` | dedup. | `52679e6` |
| `bench/workbank/tools/wire_metrics.py` | Read-only wire audit. | `39bf2de` |
| `bench/workbank/tools/test_wire_metrics.py` | (no module docstring) | `39bf2de` |
| `bench/workbank/tools/capability_gate.py` | Layered failure attribution: is a run's score a capability reading at all?. | `414205e` |
| `bench/workbank/tools/failure_audit.py` | Mechanical failure observations; overlapping flags are not causal buckets. | `39bf2de` |
| `bench/workbank/tools/build.py` | build. | `87ff33a` |
| `bench/workbank/tools/coverage.py` | coverage. | `52679e6` |
| `bench/workbank/tools/calibrate.py` | calibrate. | `87ff33a` |
| `bench/workbank/tools/web_hitcheck.py` | web_hitcheck. | `52679e6` |
| `bench/workbank/tools/verify_all.py` | verify_all. | `665c166` |
| `bench/workbank/tools/compare.py` | compare. | `87ff33a` |
| `bench/workbank/tools/ledger.py` | ledger. | `bcc439a` |
| `bench/workbank/tools/replicate_summary.py` | Summarize an explicit, complete set of comparable repeated runs, offline. | `94d3ad3` |
| `bench/workbank/tools/test_replicate_summary.py` | (no module docstring) | `94d3ad3` |
| `.claude/skills/rwkv-bench/check_run.py` | check_run. | `7c0c39c` |
| `.claude/skills/rwkv-bench/sweep.py` | sweep. | `71d2941` |
| `.claude/skills/rwkv-bench/rank.py` | rank. | `fc64f22` |

## Go 零散命令

| 文件 | 用途 | 最后改动 |
|---|---|---|
| `cmd/workreplay/main.go` | Command workreplay replays teacher-authored tool trajectories against the. | `afaeb79` |
| `cmd/wirecheck/main.go` | Command wirecheck validates supervised assistant spans of corpus rows. | `afaeb79` |
| `cmd/tokcount/main.go` | Command tokcount counts tokens with the real RWKV World vocabulary using. | `afaeb79` |
| `internal/agent/eval/replay.go` | (no header comment) | `afaeb79` |

`cmd/tokcount` 并入 `rwkv-lab tokcount`（行为逐项相同）；
`cmd/tracecorpus` 与 `scripts/corpus/` 在 M1 删除，`scripts/state-*.py` 与
`bench/workbank/tools/state_sanity.py` 在 M4 删除。
