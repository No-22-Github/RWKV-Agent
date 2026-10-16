# v2.1 出题规格

> 基础规格沿用 [v2.0 出题规格](../v2.0/authoring-v2.0.md)：`tool_policy` 代替 `offered_tools`、老师无 suffix 且每步思考、`casegen.Batch.write_case`、只用 `internal/agent/eval/types.go` 支持的判据字段、`verify.py` 从 fixture 重算答案、目录 work-v2 共 14 个工具、固定时钟 2026-09-16 10:00 Asia/Shanghai、bash 是无 python/node/网络的 just-bash 沙箱。**先通读 v2.0 规格和 [b20abc 判据修订记录](../v2.0/reports/b20abc-judge-fix.md)**，下面只写 v2.1 新增或改动的部分。整体计划见 [distill-allocation-v2.1.md](distill-allocation-v2.1.md)。

## 1. 写法

- `Batch(salt=<批次名>, author="llm:claude-sonnet-<批次名>", version="v2.1", tool_catalog="work-v2")`，`extra_tags={"batch": <批次名>}`。
- 题目写到 `bench/distill/v2.1/cases/<场景>/<题号>/`；生成脚本放 `bench/distill/tools/<批次名>/build.py`（固定种子，重跑逐字节一致）+ `README.md`。
- 题号前缀沿用场景缩写（`tab log cfg doc fs scr code web hyb nt`），数字段见计划 §2，只能写自己的段。
- 每道题一个独立题族（family 名 `<批次名>-<子类>-<序号>`），不同题之间 fixture 内容、文件名、数值都要不同，不要只换数字套模板。

## 2. 不许碰测试集

**不要打开** `bench/exam/`、`bench/workbank/`、`bench/bfcl*`、`bench/boundary*`、`bench/bashprobe*`、`bench/weatherprobe*`、`bench/primitive*` 下的题目，也不要照着它们改写。题目要自己设计。主 Agent 会在交付后做去污染检查，撞题会整题删掉。

## 3. 题目要逼出目标行为

- 每道题的通过路径必须真正用到本批要教的行为（例如 b21a 要先读出行号再改、改完读回核对；b21c 要查过真实位置后说明缺什么），走捷径应该过不了判据。
- 判据要区分"做对"和"像做对"：
  - 改文件：`expect.files` 用 `equals` 或 `contains` + `absent` 精确判结果；无关文件 `unchanged`。
  - 说没有：`output_contains_any` 收"没有/未找到/不存在/缺少/查不到/not found/missing/does not exist/no such"一类词，**中英文都要收全**；`output_excludes` 放会被编造出的具体值（fixture 里不存在的那个值的常见猜测）。
  - 先确认/先追问：首轮 `tools: []` 或 `forbidden_tools` 放破坏性工具，`expect.files` 相关文件 `unchanged`；第二轮用户确认后再要求真做并判结果。
- 词表漏收、否定句误伤是 v2.0 返修的大头（见 b20abc 记录），交付前自己用几种不同说法过一遍判据。
- 题面用用户会说的话，不点工具名，不写"测试""判据""verify"之类字样；需要特定答案形式时在题面说清（"只回答文件名"），没说要简短的题不加 `max_output_chars`。

## 4. 比例

- 中文 ≥ 50%；多轮（≥ 2 个用户轮）≥ 30%；难度 L1–L2 为主，L0 ≤ 20%。
- `tool_policy`：大约一半题不写约束（目录随机），写约束时 `must_offer` 只放真正必需的工具。

## 5. 自检（交付前必须过）

```bash
cd bench/distill/tools/<批次名> && python3 build.py && python3 build.py && git status --short ../../v2.1   # 两次结果一致
RWKV_LAB=local/bin/rwkv-lab bench/distill/tools/gate.sh v2.1 '<你的题号 glob>'   # lint 0 违规、verify 全过
local/bin/rwkv-lab corpus loadcheck --cases bench/distill/v2.1/cases
```

- 只写自己题号段和自己批次的工具目录，不改别的批次、不改 Go 代码、不提交 git、不调用任何付费模型 API、不跑老师。
- 交付写 `bench/distill/v2.1/reports/<批次名>-authoring.md`：题数、子类分布、中英比例、多轮比例、`tool_policy` 分布、判据设计要点、已知风险、你认为老师最可能答错的题。
