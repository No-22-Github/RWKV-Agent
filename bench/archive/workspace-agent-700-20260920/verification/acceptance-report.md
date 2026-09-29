# workspace-agent-700 验收报告

状态：**data_ready**（版本 workspace-agent-700-v0，run phase3-repaired-700-20260920，2026-09-20T12:17:33Z）

## 口径（每个数字只属于一个 scope）
- candidates_records_dir: 700
- candidates_gate_passed: 700
- candidates_approved: 700
- candidates_needs_review: 0
- candidates_rejected_status: 0
- candidates_bound_current: 700
- exported: 700
- exported_train: 630
- exported_validation: 70
- not_exported: 0

## 数量
- 目标 700 = 630 训练 + 70 验证；导出 700 = 630 训练 + 70 验证；缺口 0
- 种子锚点 36/36；非锚点记录 664

## 硬门槛
- ✅ total_700
- ✅ train_630
- ✅ validation_70
- ✅ anchors_36
- ✅ quota_conserved
- ✅ replay_bound_all
- ✅ review_no_pending
- ✅ independent_review_anchors
- ✅ independent_review_validation
- ✅ independent_review_train_sample
- ✅ independent_review_all_scenarios
- ✅ double_replay_clean
- ✅ no_cross_split_conflicts
- ✅ no_exact_duplicates
- ✅ all_branches_covered

## token 分布
- {"p50": 1847, "p90": 2487, "p99": 3006, "max": 3352, "min": 1206}

## 工具轨迹
- 步数 p50 4 / p90 6 / max 9；恢复样本 123

## 独立审查覆盖（§G）
- 锚点 36/36；验证 70/70；训练变体 576（阈值 60）
- 场景覆盖 ['code', 'config', 'docs', 'filesystem', 'hybrid', 'logs', 'script', 'tabular', 'web']
- 人工审查：none recorded; all reviewers are labelled agent:*

## 去重与 split
- 精确重复 0；未解决跨 split 近重复 0；同组跨 split 0

## 二次回放
- {"scope": "extra clean-room replay for anchors/validation/web/hybrid/recovery/clock records", "targets": 349, "covered": 349, "failed": 0, "missing_binding": 0}

## 失败漏斗
- {"ledger_entries": 34, "build_runs": 20, "record_level_failures": 14, "by_stage": {"null": 20, "validate": 14}}

## 已知局限
- web_fixture url_match shadowing in 1 record(s): ws7-hyb-0001-a00 — the shadowed page is unreachable by design of the frozen fetcher; see verification/fixture-audit.json
- User-authorized retention (2026-09-20): 13 previously rejected train records are retained despite structural similarity/within-train fixture reuse. Non-duplication defects were repaired; 700 is the number of records, not structurally independent tasks. See verification/phase3-retention-policy.json and phase3-repair-report.md. All 18 resolutions are labelled production, not a new independent or human review.
- S2: the four web anchors carry one extra neutral notes/*.md file added when validate.py still required a non-empty workspace; it is absent from the rendered text and carries no answer, and the issue record has been updated with that basis.
- S3: records whose review was voided by a content repair keep a `revision.superseded_review_label` recording the legacy `human:` label; the live reviewer fields are all agent:* and no record claims human review.
- S4: `verification.clean_room_replays`/`replayed_at` now count the production session and the binding replay (2) per record.
- time gate: the current-date gate is deliberately conservative, so 7 records carry a real `datetime` receipt that their answer does not causally depend on; the receipt is genuine and contradicts nothing.
- evaluator gap: the frozen `CaseExpect.FileExpectation` has no `NotContains` field, so `not_contains` in case expectations is never consumed; the dataset compensates with byte-exact `equals` (4 hyb b2 records) or full-content contains needles, and `tooling/fixture_audit.py` + review cover the rest.
- self-approval gap: cfg b3 records run a workspace `preflight.py` through `case_expect.run`; those records now also pin the script with `unchanged: true` so the model cannot rewrite its own gate.
- Historical validation contamination: ws7-fs-0001-v10 formerly reused training fixtures; the current record has an approved independent review confirming fixture freshness. The historical rejection is preserved in the review evidence.
- every candidate (not only the exported set) passes the full §E battery: generated/candidates/all.jsonl reports gate_passed over all records, so mask/wire/token<=4096 checks are executed for rows still awaiting review too.
- S5: the frozen script runner copies the workspace under `workspace/` and hidden fixtures at the sandbox root with cwd=sandbox, so a script must sweep from the launch directory; implementations that locate the project via __file__ would miss hidden fixtures.
- S6: tabular row-count vs unique-entity decisions rely on the record's documented uniqueness rule (e.g. order_id); the accepter treats the documented rule as the semantic standard.
- scr-0001-b10: its hidden fixture sits at the sandbox root, so that single record's run battery does not exercise the nested-folder sweep clause; the sibling b11/b12 records do.
- S3 (unconstrained fixtures): 29 artifact records pin the produced file byte-exactly but leave some read-only fixtures unconstrained; an independent reviewer showed that tampering with those fixtures still passes. The shipped trajectories are verified correct, so this is a checker-strength gap, not a data defect; new records add `unchanged: true` for read-only fixtures and existing ones should be backfilled with a rebinding pass.
- code r2 deviation: the frozen `truncate_and_resume` axis is unbuildable under the <=4096-token rendering limit because the frozen read_file returns up to 64 KiB (internal/agent/tools.go maxReadBytes); code r2 uses a documented same-family substitute (ambiguity -> contract abstain). See issues/code-r2-truncate-and-resume-infeasible.md.
- harness observation: two authoring subagents reported an unrelated injected `## Task ... agent-toolkit` block arriving at the end of their session; the string and the directory do not exist anywhere in this dataset, none of it entered any record/fixture/sketch, and neither agent acted on it. Reported for the harness owner.
- review log: the anchors-b reviewer re-applied its batch, so verification/review-log.jsonl holds two identical approval rows for 18 anchors; the record-level verdict is unaffected and the log is append-only by design.
- no_tool closeout: some records end with a short `no_tool` reason; a bank configured with NoToolGate=evidence (shingle >= 10) would reject such exits. The bank contract leaves that gate to the deployment configuration.
