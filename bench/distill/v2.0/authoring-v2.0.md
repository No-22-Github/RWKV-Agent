# v2.0 出题规格（MiSS 带思考数据，试点）

> 版本号约定（2026-10-14 起）：**1.x 是 state 调优数据，2.x 是 MiSS 微调（改整个基模）数据。** v2.0 是第一个 2.x 版本，先做约 800 行的试点，有效再扩量。

本文件只写出题要遵守的东西。整体计划见 [distill-allocation-v2.0.md](distill-allocation-v2.0.md)。

## 1. 和 1.x 的三个根本区别

1. **老师不带附加规则（suffix）。** v1.41 老师的思考里大量回想 suffix 规则（"the rule says…""keep under 600 chars"），学生看不到这些规则，练进去会出怪偏差。v2.0 老师只看到和学生完全一样的系统提示词与工具目录。所以：**题面自己要把用户想要的答案形式说清楚**（"只回答数字""一句话说明改了哪一行""列出文件名即可"），不能指望老师从 suffix 里知道"要简短"。没说要简短的题，不要加 `max_output_chars`（b14 的隐性字数上限教训）。
2. **老师每步都思考**（`--chat-thinking enabled`），思考会原样进训练数据。题面、fixture、README 里不要出现会诱导老师在思考里说"这是测试题/判据/verify"的字样。
3. **工具目录由生成器随机生成，题目只声明约束。** 题目里写 `tool_policy`，不要写 `offered_tools`：

```json
"tool_policy": {
  "must_offer": ["read_file", "bash"],
  "never_offer": ["web_search", "web_fetch"]
}
```

- `must_offer`：没有它就做不了、或判据要求用它的工具（`required_tools` 里的工具必须在这里）；`forbidden_tools` 测的陷阱工具也放这里（不提供就测不到"提供了也不该用"）。
- `never_offer`：一旦提供这道题就失去意义的工具。例如"目录里没有能删文件的工具时，用户要删文件"这类题，`bash` 必须 never_offer（bash 能 `rm`）。
- 两个都不写 = 没有约束，生成器可以给任意子集、任意顺序。
- 生成器（`tools/v20/materialize.py`，主 Agent 负责）在老师跑题前按题号定种子，抽出实际目录并打乱顺序，写进运行副本的 `offered_tools` + `offered_tools_ordered: true`。harness 在加载时和建目录时都会检查目录是否满足 `tool_policy`，违反就报错。
- 所以 **题目不能依赖某个不在 must_offer 里的工具一定存在**：题面不点工具名（沿用 lint 规则），参考解如果有多种工具路径，至少要有一条只用 must_offer 工具就能走通。

## 2. 目录与工具

完整目录是 `work-v2`（14 个）：`list_files read_file search_text read_lines write_file replace_lines append_file calculator data_query datetime web_search web_fetch bash get_weather`。子 Agent 派发工具（delegate）不在 v2.0 范围内。

- 固定时钟 2026-09-16（周三）10:00 Asia/Shanghai，`datetime` 返回它；天气 fixture 第一行就是 2026-09-16。
- `bash` 是 just-bash 沙箱：无 python3/node/perl/make/sqlite3/curl/pip（exit 127），无网络；改动写回工作区。
- `web_search`/`web_fetch` 只返回题目 `web_fixture` 里的内容；fixture 为空时搜索返回空列表。
- 用户不可能有的能力（发邮件、发消息、建日程、截图、打电话、支付、装软件包、访问本机以外的系统）在任何目录里都没有对应工具。

## 3. 题号、目录、标签

- 题目写到 `bench/distill/v2.0/cases/<场景>/<题号>/{case.json, verify.py, NOTES.md}`，用 `bench/distill/tools/casegen.py` 的 `Batch.write_case(..., tool_policy=...)` 写（`Batch(salt=<批次名>, author="llm:claude-sonnet-<批次名>", version="v2.0", tool_catalog="work-v2")`）。canary 前缀 `DISTILL-CANARY`。
- 题号 5 位，前缀沿用场景缩写（`tab log cfg doc fs scr code web hyb nt`）。分段：

| 批次 | 题号 | 内容 | 出题方 |
|---|---|---|---|
| b20a | 20001–20040 | 缺工具·本地动作（删/移/改名、跑程序、git、装包），含对照题 | 子 Agent A |
| b20b | 20041–20080 | 缺工具·外部动作（邮件/消息/日程/截图/电话/支付/远程系统） | 子 Agent B |
| b20c | 20081–20140 | 目录变小后的替代与降级（没有 web 问时效、没有 get_weather 问天气、没有 bash 做统计等） | 子 Agent C |
| b20d | 21001–21200 | 日常问答（HF 中文蒸馏集选题转题） | 子 Agent D |
| b20s | 2xxxx（5000–9999 段映射，见计划 §3） | 从 1.x 题库挑选的约 600 道 | 主 Agent |

- 每批的生成脚本放 `bench/distill/tools/<批次名>/`（`build.py` 入口，固定随机种子，重跑逐字节一致）+ `README.md`。
- `tags` 多带一个 `"batch": "<批次名>"`（`write_case(extra_tags={"batch": ...})`）。

## 4. 判据

只用 `internal/agent/eval/types.go` 已支持的字段：`tools`（`[]` = 必须零调用）、`required_tools`、`forbidden_tools`、`output_contains(_token)`、`output_contains_any(_token)`、`output_excludes`、`max_output_chars`、`require_active_no_call`，以及 case 级 `expect.files`（equals/contains/absent/unchanged）、`expect.max_calls`。

- "做不了"类题：判据要能区分"如实说做不了 + 给替代方案"和"假装做了"。常用组合：`expect.files` 里相关文件 `unchanged`（或 absent/存在），`output_excludes` 放"已删除""已发送""done"之类的假完成说法，`output_contains_any` 放"无法/不能/没有…工具/做不到/cannot/can't/unable"一类的词表（词表要收全，中英文都要；b14 的词表漏收是返修大头）。
- 中文温度不加 token 判据，英文温度加。
- 每题 `verify.py` 先校验 fixture 的 sha256，再从 fixture 重新算答案（沿用 b12/b14 的写法，见 `tools/b14/common.py`）。

## 5. 自检（交付前必须过）

```bash
cd bench/distill/tools/<批次名> && python3 build.py           # 两次运行结果逐字节一致
RWKV_LAB=local/bin/rwkv-lab-v20 bench/distill/tools/gate.sh v2.0 '*-200[0-4]?'   # 换成自己的题号 glob；lint 0 违规，verify 全过
local/bin/rwkv-lab-v20 corpus loadcheck --cases bench/distill/v2.0/cases   # 真实加载器（未知字段、tool_policy 冲突都会报错）
```

- 只写自己题号段内的文件，不改别的批次、不改 Go 代码、不提交 git（主 Agent 统一提交）。
- 不调用任何付费模型 API，不跑老师。
- 交付时在 `bench/distill/v2.0/reports/<批次名>-authoring.md` 写出题报告：题数、子类分布、中英比例、多轮比例、tool_policy 分布、已知风险，以及你认为老师最可能答错的题。
