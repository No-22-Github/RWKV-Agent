# b10b–b10e 出题子 Agent 共用说明

你负责为 v1.4 M3 放量写**一个出题模块**（一个或几个 `m*.py`），产出指定号段的蒸馏题。主控会给你：批次号、模块名、题类、子类配比、号段、中文下限。你只写自己的模块文件，不改 `common.py`、`casegen.py` 和别人的模块，不跑老师 API，不提交 git。

## 1. 先读（按顺序）

1. `bench/distill/v1.4/distill-allocation-v1.4.md`：§3 里你负责的题类、§4 终答形态、§7 容易搞砸的地方。**最高权威。**
2. `bench/distill/v1.4/b10-scale-prompt.md` §2「出题硬规则」。
3. `bench/distill/v1.4/reports/b10-pilot.md` §5–§6，`bench/distill/v1.4/reports/b10a.md` §5–§6（上一批的判据坑，见本文 §4）。
4. 样板：`bench/distill/tools/b10/` 里与你题类对应的 `m*.py`（M4→m4a/m4b，M5→m5a/m5b，M6→m6a/m6b，M7→m7a/m7b，M8→m8a/m8b）及其生成的 `bench/distill/v1.4/cases/*/*-80xx`；写法范例看 `bench/distill/tools/b10a/m2*.py`、`m3*.py`。
5. `bench/distill/tools/casegen.py` 的 `write_case` 参数（`offered_tools`、`web`、`case_expect`、`answer_style`、`version`）。

**不得读**：`bench/workbank/cases*`、`bench/holdout/`、`docs/workbank/reports/`、`bench/workbank/reports-data/`、`bench/workbank/ledger/`、`local/runs/` 下的跑分 trace。这些是考卷。题材、文件名、公司名、数值不得取自 workbank / p13 / bfcl-product（bfcl 的 `facts/*.txt`、`config/app.env`、`metrics/summary.txt` 句式都不能用）。

## 2. 文件与写法

- 模块文件放 `bench/distill/tools/<批次>/<模块>.py`，开头 `from common import write_case`，种子固定，重跑逐字节一致（**不要把 set / dict 的无序遍历结果写进 verify.py 或 case.json**，b10a 的 m2e 就因 `repr(set)` 每次不同被返工）。
- 每题：`case.json` + `verify.py` + `NOTES.md`（Traps / Reference solution / Why the answer is unique）。canary、family、作者由 `write_case` 处理；family 用 `fam-<abbrev>-<批次>-<slug>-NN`，每族 ≤3 题，slug 全库不重名。
- 题面不点工具名、不写步骤、不提示陷阱；中文题要像真人说话，场景互不雷同（同一模块里至少 5 个不同行业 / 场景，不要一个场景刷 20 题）。
- 生成脚本里要有自检：参考答案（NOTES 里的终答示例）必须满足本题判据；判分值不能与 fixture 里无关字面量撞车。

## 3. 自检闸门（交付前必须全过）

```bash
cd bench/distill/tools/<批次> && python3 <模块>.py           # 生成
cd /Users/no22/Projects/RWKV-Agent
bench/distill/tools/gate.sh v1.4 '<你的号段 glob>'             # lint 0 违规 + verify 全过（含破坏测试）
PYTHONHASHSEED=1 python3 ...; PYTHONHASHSEED=2 python3 ...      # 两次生成 diff 为空
```

`gate.sh` 的 glob 例：`'web-80[3-9]?'`。可以多次调用覆盖多个号段。

## 4. 判分器语义与上一批的坑（逐条照做）

判分器（`internal/agent/eval/scoring.go`）：
- `output_contains` 是**全部都要出现**（AND），子串匹配；`output_contains_any` 是任一出现；`output_excludes` 任一出现即判挂；一个 turn 只有一个 `output_contains_any`。
- `output_contains_token: true` 只作用于 `output_contains`，要求两侧不是字母/数字——**中文字也算字母**，「共19单」里的 19 会判挂，所以中文题别用 token 模式，改用带单位的 any 列表（「19 单」「19单」）。
- `tools: []` + `require_active_no_call: true` 表示本轮零调用。

b10a 返工过的坑：
1. **同一数字的两种写法（5294 / 5,294）不得同时放进 `output_contains`**——那是 AND，必挂。放进 `output_contains_any`。
2. 一两位的裸数字（"1"、"12"）别单独做判据，会被别的数字蹭过；带单位或上下文写法。
3. 时间：中文自然回答写「晚上 9 点」，别只认 `21:00`；时间写法放 any 列表。
4. 排除项只排除「把错值当答案」的说法，**不要排除解释性提及**：诱饵文件路径、其他对象的名字、背景金额，老师在「查了哪里」里提到它们是对的。诱饵**数值**可以排除（简报不许复述）。
5. 排除短语要防否定句误伤：`"0 次"` 会命中「10 次」「不能报 0 次」；`"defined in X"` 会命中「not defined in X」。
6. 「部分可答」题：给出确定部分 + 标明不完整就是对的，不要排除部分合计。
7. 反问题的词表要收点名参数的常见说法（「姓名」「名称」「编号」「路径」「起止日期」「Which file」），不收泛问。
8. 英文大小写：词表里同时给句首大写和小写（"Which rooms" / "which rooms"）。
9. 题面要包含能命中网页 fixture `query_match` 的名字（b10a 有两题题面没有品牌名，老师搜不到）。
10. 题目数据要和 README / 说明自洽（b10a tab-8045 的 README 写「按盒管理」，和问「多少支」矛盾）。
11. 长度上限一律 ≤600；单轮简单题可用 300–400，但别低于老师合理回答的长度。
12. `verify.py` 打印的 `expected_*` 必须与判据一致（`expected_contains_any` 要与 turn 的 `output_contains_any` 并集相等）；`bank verify --strict-shape` 会查。

## 5. 交付

完成后回复主控：模块文件路径、题号清单、子类实际题数、中文题数、闸门输出最后几行、你认为有风险的题（判据可能偏严 / 偏松的，列题号和理由）。不要写报告文件。
