# Agent Wire 配置指南

模型看到什么、我们怎么解析它，由 `internal/agent/wire.Spec` 这一个规范对象描述。
CLI/API/评测都用同一条路径选择它：

- **简写**：`--profile <preset>`（注册过的点）
- **长写**：`--wire key=value,...`（在 suite 默认或 preset 之上只改点名的轴）

两者最终都会归一化成同一个 `canonical` 字符串和 `hash`，写进 `run.json`。preset 只是
快捷方式，不是唯一入口；未注册的组合照常可跑，并靠 canonical/hash 追溯。

---

## 1. 两条入口

| 入口 | 用途 | 说明 |
| --- | --- | --- |
| `rwkv-cli agent-eval` | 固定题库、可归档评测 | 每个 case 独立工作区；批量并发；产出 `run.json` / `summary.json` / `trace.jsonl` |
| `rwkv-cli agent` | 交互式 / 单任务产品路径 | 同一套 harness；配置经 `api.Config.Profile` / `api.Config.Wire` |

两者由同一份 `ProductHarnessOptions` / `XMLHarnessOptions` 构造，`--profile` 与 `--wire`
语义一致。

---

## 2. 快速开始（远程 rwkv_lightning 示例）

```sh
export RWKV_CF_ACCESS_CLIENT_ID='...'
export RWKV_CF_ACCESS_CLIENT_SECRET='...'

./dist/rwkv-cli agent-eval \
  --model rwkv7-g1j-7.2b-20260831-ctx16384 \
  --completion rwkv-lightning-cuda \
  --api-url https://<host>/v1/batch/completions \
  --api-header-env CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID \
  --api-header-env CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET \
  --api-stream=false \
  --api-stop-tokens none \
  --suite bfcl-product --profile xml-v1 \
  --case-parallelism 60 --case-timeout 5m \
  --output runs/my-run
```

要点：

- `--api-header-env HEADER=ENV_VAR` 只从环境变量读值，不写入评测产物。
- `--api-url` 是**完整 URL**，客户端不拼接路径。rwkv_lightning 传 `contents[]`，因此
  `/v1/batch/completions`、`/v1/chat/completions` 都可用；`/big_batch/completions` 是单请求串行，别用于并发。
- `--api-stop-tokens` 支持情况因部署而异（见 §9），连不上时先试 `none`。
- `--case-parallelism` >1 时客户端会在 10ms 窗口内把同一时刻的调用合并成一次 `contents[]` 请求。

查看配置而不花机时（不需要 `--model`）：

```sh
./dist/rwkv-cli agent-eval --list-profiles
./dist/rwkv-cli agent-eval --explain-profile md-v1
./dist/rwkv-cli agent-eval --explain-profile xml-v1 --wire "route=respond-inspect,prefill=envelope"
```

---

## 3. 轴：参数总表

`--wire` 的键就是下表的轴名。

| 轴 | 取值 | 产品 XML 默认 | 产品 Markdown 默认 | 旧参数 |
| --- | --- | --- | --- | --- |
| `format` | `xml` \| `md-fence` | `xml` | `md-fence` | `--agent-protocol` |
| `transcript` | `product` \| `benchmark` | `product` | `product` | （Primitive 专用，见 §8） |
| `transport` | `text` \| `native` | `text` | `text` | `--chat-prompt-mode native-chat` |
| `thinking` | `off` \| `fast` \| `full` | `off` | 仅 `off` | `--thinking` / `--reasoning` |
| `prefill` | `none` \| `envelope` \| `fence` \| `deep-fence` \| `fake-think-half` \| `fake-think-closed` | `none` | `deep-fence` | `--deep-tool-anchor`、`--decision-fake-think`、`--closed-fake-think` |
| `abstain` | `none` \| `no-tool` \| `no-tool+gate-state` \| `no-tool+gate-evidence` | `none` | `no-tool` | `--semantic-no-tool`、`--no-tool-gate` |
| `terminal` | `none` \| 任意工具名（如 `submit`） | `none` | `none` | Primitive 逐题 |
| `route` | `none` \| `respond-inspect` \| `progressive` | `none` | `none` | `--route-stage`、`--progressive-tools` |
| `catalog` | `full` \| `progressive` | `full` | `full` | `--progressive-tools` |
| `control` | `base` \| `fewshot` | `base` | `base` | `--few-shot` |
| `feedback` | `raw` \| `compress-fetch` | `raw` | `raw` | `--compress-fetch` |
| `subagent` | `block` \| `raw` | `block` | `block` | `--subagent-raw-feedback` |
| `align` | `legacy` \| `qwen36` | `legacy` | `legacy` | — |

`align=qwen36` 是 G1K 语料对齐配置：工具结果改由 user 轮承载并包 `<tool_response>`，
工具目录从 markdown 列表改为 `<tools>` 内的 JSON 数组；动作信封 `<tool_call>`、指令
文字与目录内容均不变。仅支持 `format=xml` + `transcript=product` + `transport=text`；
解析器同时接受新旧两种结果包络（模型回显结果信封记 `envelope_recovered` 修复）。

跨轴约束（违反会在构造期报错，不会静默改字节）：

- `thinking=fast/full` 已经占用 assistant opening ⇒ `prefill` 必须是 `none`；
- `format=md-fence` 没有 think 槽位 ⇒ 产品 Markdown 只能 `thinking=off`；
- `prefill=deep-fence` 移除了全部句法弃权出口 ⇒ 必须配 `abstain=no-tool`（可加 gate）；
- `prefill=fake-think-*` 是产品 Markdown 实验，与深锚点互斥（同一槽位）；
- `route=progressive` 与 `catalog=progressive` 必须同时出现；
- `transport=native` 在提供 tools 时没有 prefill ⇒ `prefill=none`。

---

## 4. 简写：preset 与修饰符

```sh
--profile md-v1                    # 注册点
--profile md-v1+anchor+gate-state  # preset + 修饰符
--profile md-fence-v1              # 浅锚点
--profile xml-v1+think-fast        # XML + 半开 think
```

修饰符：`think-off|think-fast|think-full`、`prefill-none|envelope|fence|deep-fence|anchor|fake-think|fake-think-closed`、
`no-tool|gate-state|gate-evidence`、`submit`、`route-respond|route-progressive|progressive`、
`fewshot`、`native`、`compress-fetch`、`raw-subagent`。

`--strict-spec`（仅 `agent-eval`）要求最终 spec 命中注册 preset，否则报错并打印 canonical，
用于把正式实验登记成命名点。未注册组合默认允许，`run.json` 的 `wire_preset` 为空即表示匿名。

> `--profile` / `--wire` 不能与旧的单轴开关（`--agent-protocol`、`--deep-tool-anchor`、
> `--semantic-no-tool`、`--thinking`…）同时使用：同一轴两个来源会让语义依赖 flag 顺序。

<!-- BEGIN GENERATED: wire-profiles -->
## Registered presets

| preset | canonical | short |
| --- | --- | --- |
| `bfcl-md-v1` | `format=md-fence;transcript=product;transport=text;thinking=off;prefill=deep-fence;abstain=no-tool;terminal=none;route=progressive;catalog=progressive;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+deep-fence+no-tool+route-progressive+progressive` |
| `bfcl-xml-v1` | `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=progressive;catalog=progressive;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `route-progressive+progressive` |
| `default` | `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `default` |
| `md-fakethink-v1` | `format=md-fence;transcript=product;transport=text;thinking=off;prefill=fake-think-half;abstain=no-tool;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+fake-think-half+no-tool` |
| `md-fence-v1` | `format=md-fence;transcript=product;transport=text;thinking=off;prefill=fence;abstain=no-tool;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+fence+no-tool` |
| `md-v1` | `format=md-fence;transcript=product;transport=text;thinking=off;prefill=deep-fence;abstain=no-tool;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+deep-fence+no-tool` |
| `native-v1` | `format=xml;transcript=product;transport=native;thinking=off;prefill=none;abstain=none;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `native` |
| `primitive-v1` | `format=md-fence;transcript=benchmark;transport=text;thinking=off;prefill=fence;abstain=none;terminal=submit;route=none;catalog=full;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `md-fence+benchmark+fence+submit` |
| `xml-progressive-v1` | `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=progressive;catalog=progressive;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `route-progressive+progressive` |
| `xml-route-v1` | `format=xml;transcript=product;transport=text;thinking=off;prefill=envelope;abstain=none;terminal=none;route=respond-inspect;catalog=full;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `envelope+route-respond-inspect` |
| `xml-v1` | `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=none;terminal=none;route=none;catalog=full;control=base;feedback=raw;subagent=block;align=legacy;stages=two;loop=0,0,0,0,0,0,0,0,0,0,false` | `default` |

## Axis domain

| axis | values |
| --- | --- |
| `format` | `xml`, `md-fence` |
| `transcript` | `product`, `benchmark` |
| `transport` | `text`, `native` |
| `thinking` | `off`, `fast`, `full` |
| `prefill` | `none`, `envelope`, `fence`, `deep-fence`, `fake-think-half`, `fake-think-closed` |
| `abstain` | `none`, `no-tool`, `no-tool+gate-state`, `no-tool+gate-evidence` |
| `terminal` | `none`, `any tool name (e.g. submit)` |
| `route` | `none`, `respond-inspect`, `progressive` |
| `catalog` | `full`, `progressive` |
| `control` | `base`, `base-nocall`, `greeting`, `bare`, `fewshot` |
| `feedback` | `raw`, `compress-fetch` |
| `subagent` | `block`, `raw` |

## Recovery vocabulary

| transcript | recoveries |
| --- | --- |
| `xml` | `think_stripped`, `array_envelope`, `envelope_recovered`, `json_repaired`, `function_wrapper`, `key_alias`, `arguments_hoisted`, `stringified_arguments`, `nested_name`, `name_inferred`, `tool_renamed`, `path_argument`, `legacy_xml_call`, `xml_path_alias` |
| `md-fence` | `think_stripped`, `array_envelope`, `envelope_recovered`, `json_repaired`, `function_wrapper`, `key_alias`, `arguments_hoisted`, `stringified_arguments`, `nested_name`, `name_inferred` |

## Modifiers

`align-legacy`, `align-qwen36`, `anchor`, `bare`, `base-nocall`, `compress-fetch`, `deep-fence`, `envelope`, `fake-think`, `fake-think-closed`, `fence`, `fewshot`, `gate-evidence`, `gate-state`, `greeting`, `native`, `no-tool`, `one-stage`, `prefill-none`, `progressive`, `raw-subagent`, `route-progressive`, `route-respond`, `submit`, `think-fast`, `think-full`, `think-off`, `two-stage`

## Override keys

`abstain`, `align`, `catalog`, `control`, `feedback`, `format`, `prefill`, `route`, `stages`, `subagent`, `terminal`, `thinking`, `transcript`, `transport`
<!-- END GENERATED: wire-profiles -->

---

## 5. 长写：`--wire`

```sh
--wire "format=md-fence,prefill=fence,abstain=no-tool"
--wire "thinking=fast"                       # 在 --profile xml-v1 之上叠加
--wire "terminal=echo"                       # 任意合法工具名
```

- 键 = 轴名（§3），值 = §3 的取值；未知键、重复键、空值在解析阶段报错。
- 在 suite 默认或 `--profile` 之上只改被点名的轴，其余保持不变。
- 最终仍走同一套校验：例如 `--wire "thinking=full,prefill=envelope"` 会报 `prefill.conflict`。

---

## 6. 旧参数 → 轴 对照

| 旧参数 | 映射 |
| --- | --- |
| `--agent-protocol xml` | `format=xml` |
| `--agent-protocol markdown` | `format=md-fence` |
| `--completion chat-completions --chat-prompt-mode native-chat` | `transport=native` |
| `--thinking off\|fast\|full` | `thinking` |
| `--reasoning[=true]` | `thinking=fast`（deprecated 别名） |
| `--deep-tool-anchor` | `prefill=deep-fence` |
| `--decision-fake-think` | `prefill=fake-think-half` |
| `--decision-fake-think --closed-fake-think` | `prefill=fake-think-closed` |
| `--semantic-no-tool` | `abstain=no-tool` |
| `--no-tool-gate state\|evidence` | `abstain=no-tool+gate-state\|gate-evidence` |
| `--progressive-tools` | `route=progressive` + `catalog=progressive` |
| `--route-stage` | `route=respond-inspect` |
| `--few-shot` | `control=fewshot` |
| `--compress-fetch` | `feedback=compress-fetch` |
| `--subagent-raw-feedback` | `subagent=raw` |

suite 默认差异：

- `agent` / App：XML 默认；选 `--agent-protocol markdown` 时 `no-tool` 与 `deep-fence` 默认打开。
- `agent-eval --suite bfcl-product`：Markdown + progressive router + `no-tool` + 深锚点（route 预算 48）。
- 其余内置 suite：XML、无 router、无 `no_tool`、无锚点。
- Primitive suite：`md-fence` + benchmark transcript + 逐题 terminal（含 submit 时）；`--profile`/`--wire` 暂不支持。

---

## 7. loop 参数

兜底机制靠循环计数触发，因此循环参数也进 spec 与 manifest。

| 参数 | 默认 | 作用 |
| --- | --- | --- |
| `--max-steps` | 6 | 单轮最大步数；到达后强制 answer |
| `--max-tokens` | 1024 | 单次生成上限（answer 预算） |
| `--decision-max-tokens` | 0 = 按 format（XML 512 / md 96） | 决策阶段预算，受 `--max-tokens` 夹取 |
| `--route-max-tokens` | 16（agent 48；bfcl-product 48） | route 阶段预算 |
| `--duplicate-replay-limit` | 2 | 纯读工具重复调用的重放上限 |
| `--duplicate-rescue-threshold` | 3 | 连续相同调用达到该值进入 rescue |
| `--same-tool-rescue-limit` | 3 | 同一工具连续成功达到该值进入 rescue（已统一到产品常量；历史值 8 需显式传） |
| `--answer-stage-lead` | 0 | 提前 N 步进入 answer 阶段，并给一次 answer 阶段重问 |
| `--no-tool-gate` | 空 | `state`/`evidence`，对 `no_tool` 的 harness 级约束 |

> 注意：`duplicate` 系列只对"完全相同的调用/同一工具的连续成功"生效。多样化过度探索
> （每步换工具）不会触发 rescue，只会走到 `--max-steps` 的强制 answer。

---

## 8. 产物里怎么核对

- `run.json`
  - `harness.wire_canonical` / `wire_hash`：本轮模型侧配置的完整身份；
  - `harness.wire_preset`：命中的注册 preset（空 = 匿名组合）；`wire_conflict`：被拒绝的旧组合；
  - `case_wires[]`：**逐题**生效的 transcript / terminal_tool / max_steps / decision budget。
- `summary.json`
  - 分数：`task_success`、`answer_accuracy`、`route_accuracy`、`protocol_validity`、`required_tool_completion` 等；
  - `metrics.repairs_by_id`：每种容错修复各触发多少次（格式漂移会先在这里显形）。
- `trace.jsonl`
  - 每步的 `request.prompt`（模型真正看到的字节）、`response.output`、`protocol_repairs`。

---

## 9. 远程部署注意事项（rwkv_lightning）

- 请求体（客户端实际发送）：`model`、`contents[]`、`max_tokens`、`temperature/top_k/top_p/alpha_*`、
  `stream`、`chunk_size`，可选 `state_id` / `password` / `stop_tokens`。响应取
  `choices[0].message.content`。
- `stop_tokens` 的形态随部署而异：
  - 有的部署接受 decoded-text 字符串数组（`--api-stop-tokens text`，默认）；
  - `rwkv_lightning_cuda` 一系可能要求整数 token ID（`--api-stop-tokens 0,6884,24281`）；
  - **实测 api-7b.rwkvos.com 对任何 `stop_tokens` 都返回 HTTP 500**，必须 `--api-stop-tokens none`。
  连通性排查顺序：`none` → `text` → `cuda`。
- `--api-stream=false` 返回一次性 JSON，评测更稳；`true` 走 SSE。
- state：不传 `--state-id` 即基模零状态；传 `--state-id <id>` 复用上传的 state。
  **带 state 的 run 与基模 run 不能直接比较。**
- 并发：`--case-parallelism` 设成题目数即可一波跑完；同一时刻的请求会被合并成一次
  `contents[]`。批推理下贪心解码仍可能有几个 case 的结果抖动，比较两组配置时注意这点。

---

## 10. 常见组合示例

```sh
# 产品评测：无 router 的 XML / Markdown（g1j 7B 实测优于带 router 的默认）
agent-eval --suite bfcl-product --profile xml-v1 --case-parallelism 60 ...
agent-eval --suite bfcl-product --profile md-v1  --case-parallelism 60 ...

# 对照 progressive router（suite 默认）
agent-eval --suite bfcl-product --case-parallelism 60 ...

# 临时实验：浅锚点 + evidence gate
agent-eval --suite bfcl-product --wire "prefill=fence,abstain=no-tool+gate-evidence" ...

# 交互式：与评测同一份配置
agent --profile xml-v1 --completion rwkv-lightning-cuda --api-url ... --model ... \
      --api-stop-tokens none --api-stream=false --workspace /path/to/project --prompt "..."
```
