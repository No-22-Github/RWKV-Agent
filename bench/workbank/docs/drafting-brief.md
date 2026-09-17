# workbank 起草简报（每个起草 Agent 必读，v1）

> 你的任务：为本 scenario 起草 4 道题（L0×1、L1×2、L2×1），每题一个目录：
> `bench/workbank/cases/<scenario>/<id>/`，内含 `case.json`、`verify.py`、`NOTES.md`。
> 这三份文件的契约在 `docs/HANDOFF.md` §2，出题法则在 `docs/authoring-guide.md`（最高权威），
> 工具真实行为在 `docs/M0-findings.md` §1/§2/§9。开工前先通读这三份。
> 机器可读枚举：`docs/tag-vocab.json`。合法样例：`tools/testdata/tabular/tab-9001/`、`tools/testdata/web/web-9001/`。

## 1. 硬规则（lint.py 会逐一检查，违反即打回）

1. **题面（每轮 prompt）不得出现 12 个工具名**，也不得出现本题陷阱的题面禁词（tag-vocab.json 里每个陷阱的 forbidden_words）。题面只讲业务目标，不讲步骤、不提示陷阱。
2. **答案契约逐字节**追加在最后一轮 prompt 末尾：
   - 数字/字符串答案题：`Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.`
   - 写文件/写脚本题（有 expect.files 或 expect.run）：`When finished, reply DONE.`
3. `description` 末尾：` WORKBANK-CANARY-<8位hex>`（每题不同）。
4. **陷阱**：L1 恰 1 个 trap；L2 恰 2 个；L0 无 trap。每个 trap 必须在 `tags.trap_decoys` 里有键，值=「不注意会得到的错误答案」，且 ≠ 正确答案（数值题给数值）；写文件类可 null。
5. `axes` 必须覆盖每个陷阱的轴（tag-vocab.json）。
6. **level 由计数决定不凭感觉**：L0=0陷阱且ref_calls≤3；L1=1陷阱且ref_calls≤4；L2=2陷阱，或1陷阱且(涉及文件≥3或ref_calls≥5)。
7. `ref_calls` 必须与 NOTES 里参考解步骤数一致。
8. **M0 写目录规则**：题面要求模型写入的任何目录必须已存在于 `files`（放一个 `.keep` 占位）——工作区工具不能创建目录。lint 的 `m0.write_dir` 会查 expect.files 的路径。
9. fixture 现实感（手册 §6）：金额带分、量级跨 2–3 档、人名/SKU/服务名多领域、日期 2025-10～2026-09、禁 `foo/bar/example/test1/Alice/Bob`；目录层级 1–3、含 README 与无关文件。文件合计 ≤8KB（除非题干设计需要长文）。
10. 英文出题。
11. `verify.py` 只用标准库、必须引用 `case.json`（从 `files` 独立计算期望，不得照抄 expect 字段值）、打印：数字题 `{"expected_number": x}`；字符串题 `{"expected": "..."}`；写文件题 `{"files": {path: content}}`。
12. `NOTES.md` 四段：`## Traps`（埋点位置+错误答案）、`## Reference solution`（编号步骤，共 ref_calls 步）、`## Why the answer is unique`；web/hyb 加 `## Five alternative phrasings`（恰 5 条查询）。

## 2. 家族变体结构（4 题一套）

同一家族 `fam-<abbrev>-<slug>-01`：同一骨架（同场景同任务结构），L0 基题 → L1 加陷阱甲 → L1 换数据/名字再加陷阱乙 → L2 叠加（甲+乙或甲+丙）。变体之间**换数值、换人名、换措辞**，任务结构不变。4 题的 prompt 相互 3-gram Jaccard 要 <0.6（换措辞），dedup.py 会查。

## 3. 工具行为速查（详见 M0-findings）

- `data_query` **不解析** `$1,234.50`、`12.5%`、`(300.00)`、`NA`/`-`/空串——这些列直接聚合会**报错**；filter 匹配是字符串精确比较。TR-NUMFMT/TR-MISSING 的「错误答案」要写成：模型绕开报错后的典型手算错。
- `read_file` 64KB 截断，输出带 `truncated:true` JSON 字段；`read_lines` 每次最多 200 行、底层同样 64KB 静默截断。
- `list_files` 默认上限 200 条（可调到 500），`truncated` 恒在输出里；dotfile 会列出。
- web 工具恒注册；无 fixture 的题搜索返回空列表、fetch 返回固定 not-found 页。web 题页面按 >4096 token（触发压缩）/ ≤8192（硬截断）两档设计。

## 4. schema v5 要点（case.json 是裸 Case 对象，无外层包裹）

- `tags`：scenario、task_type、traps[]、trap_decoys{}、axes[]、level、family、ref_calls、fixture_bytes（先写 0，lint --fix 回填）、status:"draft"、version:1、author:"llm:<你的模型身份写 glm-drafter>"、reviewer:null。
- `files`：{相对路径: 完整内容}。`outside_files`：工作区外的文件（不放 workspace/ 前缀）。
- turn 的 `expect`：数字题 `{"expected_number": x, "tolerance": 0.01}`；字符串题 `{"output_equals": "..."}`（宽松用 output_contains）；notool 题加 `"tools": [], "require_active_no_call": true`；越权题用 `forbidden_tools`。
- case 级 `expect`（写文件/脚本题用）：`{"files": {path: {"contains": [...] 或 "equals": ... 或 "absent": true 或 "unchanged": true}}, "run": {...仅脚本题}}`。`expect.run`：`{"path": "脚本名", "expected_stdout": "模型脚本应打印的内容", "hidden_files": {path: content}(可选，第二组输入防硬编码), "timeout_millis": 10000}`。
- web/hyb 题：`web_fixture` 条目字段 `query_match`/`url_match`/`url`/`title`/`snippet`/`content`/`published_at`（模拟 Brave/Tavily 的真实响应改写，不手写整页）。搜索命中=query_match 是查询的大小写不敏感子串，条目顺序=结果顺序。

## 5. 自检闭环（全部通过才算完成）

在 `bench/workbank/` 目录下：
```bash
.venv/bin/python tools/lint.py --case ../workbank/cases/<scenario>/<id>   # 每题 0 违规
.venv/bin/python tools/lint.py --fix --case <同上>                          # 回填 fixture_bytes
.venv/bin/python tools/verify_all.py --cases cases/<scenario>              # 本场景全部 PASS
.venv/bin/python tools/web_hitcheck.py --case <dir>                        # web/hyb 必须 5/5
.venv/bin/python tools/dedup.py --cases cases/<scenario>                   # 无家族内误报（措辞要拉开）
```
verify_all 对你的每题会做期望比对 + 破坏测试；`{"files": ...}` 形状的题破坏测试可能跳过（warning 可接受）。**不要跑 git 命令**（主控统一提交），**不要碰别的 scenario 目录**。
