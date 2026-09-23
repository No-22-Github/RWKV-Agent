# g1k 采样参数扫描报告（2026-09-23）

计划与全部偏离记录见 [PLAN.md](PLAN.md)，规程见 [benchmark-protocol.md](../benchmark-protocol.md)。

## 结论

1. **没有唯一最优，按任务选命名预设**（已落为 `rwkv-cli --sampling <名字>`）：

   | 预设 | 参数 | 何时用 | 依据 |
   |---|---|---|---|
   | `g1k-agent` | T 0.3 · top_p 0.5 | **默认**，工具调用决策 | bfcl-product 最高（均 48/60），7 套合计最高（186） |
   | `g1k-agent-fast` | 同上 + presence 0.5 · frequency 0.1 · decay 0.996 | 长的多步 Agent 任务 | 分数同一档、单档快约 27%；**缺参数时追问变差**（见 §5） |
   | `g1k-stable` | T 1 · top_k 20 · top_p 0.3 | 少副本 A/B 对比 | 7 套两副本合计只差 3，最稳 |
   | `greedy` | top_k 1 | 回归、调试 | 基线；批处理仍有约 ±1 题抖动 |
   | `backend` | rwkv_lightning 作者默认（presence 2） | 聊天、最快跑分 | 单档约 5 分钟（其余约 9–11 分钟） |

2. **截断比温度重要**。有截断（top_p 0.5 或 0.3）的档 bfcl-product 都在 43–48；不截断时温度越高越崩：T 0.3 / 0.6 / 1.0 依次 42 / 37 / **22**。
3. **前三名在统计上分不开**，都只比 greedy 好 2–5 题（bfcl-product）。选 `g1k-agent` 是按预注册平局规则（取低温度）。
4. **workbank 对采样不敏感**：所有档 5–10/148，且几乎全部来自 notool 场景；其余 9 个需要工具的场景接近 0（§5）。瓶颈是能力，调参无效。
5. 过程中修掉 **9 个 harness / 配置坑**，其中 5 个会系统性压低 g1k 分数（§6）。g1k 在 workbank 上"历史 0–3/40"有相当部分来自这些坑。

## 1. 可比性与有效性

| 项 | 值 |
|---|---|
| 模型 / 端点 | `rwkv-g1k-7b-temp-3601` @ api-7b.rwkvos.com，albatross-1.3.0，hard_max_bsz 169；6 次驱动调用各有跑前快照，正常结束的 5 次另有跑后快照（中止的一次加赛无跑后快照），模型 id 全部一致（`runs/bench-20260923/endpoint-*.json`） |
| 分支 / 提交 | `bench/g1k-sampling-sweep`；run 分布在 `f050d18`（29）、`ddac4fb`（17）、`511ca2b`（8） |
| 二进制 | **54 个 run 同一个二进制**，sha256 `028abf88…`（`aaf8f2d` 起未再改动编译进去的代码）。其中 23 个 run 的工作区含未提交改动，均为 PLAN 文档或尚未编译的源码，二进制哈希可证 |
| 格式 | `--profile g1k --strict-spec`（primitive 两套用自带协议） |
| 预算 | `--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m`；传输 `--remote-batch-wait 0s`；总并发 64 |
| workbank | 148 题含 draft；bank_version `sha256:11a561f5…`（build.py）；case 源哈希 `2d9193e4…`（sweep.py） |
| 有效性 | **54/54 过闸门，0 作废，0 基础设施错误，0 重试**。此前 5 次失败尝试全部归档在 `runs/bench-20260923/aborted/`，不计分 |

## 2. 阶段 1：9 档筛选（k=1）

| 档 | T | top_k | top_p | 惩罚 | workbank | bfcl-product | 合计 |
|---|---|---|---|---|---|---|---|
| `t03-p05` | 0.3 | – | 0.5 | – | 6 | 46 | **52** |
| `backend-nopen` | 1.0 | 20 | 0.3 | – | 8 | 43 | 51 |
| `t06-p05` | 0.6 | – | 0.5 | – | 5 | 45 | 50 |
| `backend` | 1.0 | 20 | 0.3 | 2 / 0.2 / 0.996 | 7 | 43 | 50 |
| `t03-p10` | 0.3 | – | 1.0 | – | 7 | 42 | 49 |
| `greedy` | – | 1 | – | – | 6 | 43 | 49 |
| `t10-p05` | 1.0 | – | 0.5 | – | 7 | 40 | 47 |
| `t06-p10` | 0.6 | – | 1.0 | – | 7 | 37 | 44 |
| `t10-p10` | 1.0 | – | 1.0 | – | 2 | 22 | 24 |

`–` 表示不截断（top_k 65536）或无惩罚。workbank 最高 7–8 > 地板线 5，未触发地板规则，但各档对照 greedy 的逐题符号检验全部 p ≥ 0.22。

## 3. 阶段 2（k=2）与加赛

| 档 | workbank | bfcl-product | 两套合计 |
|---|---|---|---|
| `t03-p05` | 6 / 8（7.0） | 46 / 50（48.0） | 110 |
| `backend-nopen` | 8 / 9（8.5） | 43 / 45（44.0） | 105 |
| `t06-p05` | 5 / 7（6.0） | 45 / 43（44.0） | 99 |
| `greedy` | 6 / 7（6.5） | 43 / 42（42.5） | 98 |

前两名 workbank 差 1.5 ≤ 极差 2 → 触发预注册加赛：其余 5 套，每档 k=2。

| 套件 | `t03-p05` k0 / k1 | `backend-nopen` k0 / k1 |
|---|---|---|
| workbank | 6 / 8 | 8 / 9 |
| bfcl-product | 46 / 50 | 43 / 45 |
| boundary（18） | 0 / 1 | 1 / 0 |
| assistant（6） | 3 / 3 | 1 / 2 |
| smoke（10） | 3 / 2 | 2 / 3 |
| primitive-orig30 | 15 / 18 | 18 / 15 |
| primitive-feedback30 | 14 / 17 | 16 / 18 |
| **合计** | 87 / 99 = **186** | 89 / 92 = **181** |

差 5 ≤ 较大极差 12 → 无法区分 → 取低温度 **`t03-p05`**（= `g1k-agent`）。

## 4. 阶段 3：`t03-p05` + 轻度惩罚

判定："不掉分" = 两套两副本合计 ≥ 110 − 6 = 104，不掉分者取最快。

| 档 | workbank | bfcl-product | 合计 | 判定 | 单档耗时 |
|---|---|---|---|---|---|
| `t03-p05`（基准） | 6 / 8 | 46 / 50 | 110 | – | 9.9 / 11.2 分钟 |
| `t03-p05-pr05`（presence 0.5） | 7 / 10 | 47 / 41 | **105** | 不掉分 | **8.2 / 7.1 分钟** |
| `t03-p05-pr10`（presence 1.0） | 8 / 7 | 44 / 42 | 101 | 掉分 | 6.9 / 7.7 分钟 |

`t03-p05-pr05` 即 `g1k-agent-fast`。惩罚提速的机制：`backend` 档平均每次回复约 370 字符，其余档约 950——压住了复读空转。

## 5. 拆分

**workbank 按场景**（两副本通过次数之和；n 为题数）：

| 场景 | n | g1k-agent | g1k-agent-fast | g1k-stable | greedy |
|---|---|---|---|---|---|
| notool | 12 | 14 | 16 | 15 | 13 |
| config | 16 | 0 | 0 | 2 | 0 |
| web | 16 | 0 | 1 | 0 | 0 |
| code / docs / filesystem / hybrid / logs / script / tabular | 104 | 0 | 0 | 0 | 0 |

**bfcl-product 按类别**（两副本通过次数之和）：

| 类别 | n | g1k-agent | g1k-agent-fast | g1k-stable | greedy |
|---|---|---|---|---|---|
| irrelevance（不该调） | 20 | **32** | 26 | 23 | 25 |
| missing（缺参数，应追问） | 10 | 19 | **11** | 20 | 20 |
| supplied（信息给全，应调用） | 10 | 15 | **19** | 15 | 12 |
| state 多轮 | 10 | 15 | 17 | 17 | 12 |
| recovery 多轮 | 10 | 15 | 15 | 13 | 16 |

**`g1k-agent-fast` 的副作用**：惩罚让模型更倾向于直接调用工具（workbank 两副本 `called_tool` 36 次 vs g1k-agent 18 次）——supplied 类因此涨，但 **missing 类（该追问时）从 19 掉到 11**。需要澄清或追问的场景不要用 fast 预设。

**workbank 的失败模式**（阶段 1 前 5 档，需要工具的 136 题 × 5 = 680 次）：
- 59% **一次工具都不调**，直接给答案（编造）。
- 调用了工具的，主死因是复读链：首次检索关键词不对 → 转 `web_search`（题面已说明本地有）→ 同一调用原样重复 → 被判重复拒绝 → 强制作答阶段仍在发工具调用（`tool action is forbidden during answer`，调 3 次以上工具的失败里有 151 次）。
- 自发 `<think>` 写不完（`incomplete leading think block`）36 次。
- 抖动题都不是能力抖动：要么碰巧答对（未读文件就作答），要么格式不守约（内容对但回了整句，被判"不是纯数字"）。

**训练靶子**：先读本地文件；不重复调用；进入作答阶段就停止调用工具；终答遵守"只回答案"契约。

## 6. 过程中修掉的坑

| # | 坑 | 影响 | 修复 |
|---|---|---|---|
| 1 | 漏传 `--profile` 静默落 legacy 格式；长 profile 名难记 | 9-22 g1k 0/148 | `g1k` 短名预设（`6783ba1`） |
| 2 | workbank 的 firstcall=auto 让 `--strict-spec` 误拒 | 无法锁格式 | 文本传输下 MatchPreset 忽略该惰性轴（`6783ba1`） |
| 3 | `top_k=1` 使温度失效 | 历史 RWKV "T=0.3" 实为贪心 | 规程与预设表禁止 |
| 4 | 单题超时默认 2 分钟 | 56/148 被掐 | 固定 30m，记入 run.json（`4754a63`、`aaf8f2d`） |
| 5 | 决策步预算默认 512，截断自发思考 | 85/148 协议无效 | `--decision-max-tokens 2048`，闸门查（`d3c88b5`） |
| 6 | 合并请求的 4 MiB 上限按整批算 | 132/148 作废；9-22 的 30 题同源 | 按条数放大 + 回归测试（`3f64fd6`） |
| 7 | 合并请求整批结束才交付（队头阻塞） | 25/148 撞 30m | 开放 `--remote-batch-wait`，设 0（`85e137b`、`aaf8f2d`） |
| 8 | 关闭合并后约 168 路同时预填充打挂共享端点 | 102/148 断流 | 总并发 ≤ 64（`f050d18`） |
| 9 | `dist/rwkv-cli` 过期；`/v1/models` 的 `created` 是请求时刻 | 误判 | 只用 `bin/`；不据此判断重启 |

另记一条未修：chat-completions 路径的 `run.json` `wire_canonical` 失真（记录缺陷，不影响分数），已另开任务。

## 7. 局限

- **副本少**：阶段 1 k=1，阶段 2/3 k=2（按用户要求控时）。前三名的差距在噪声内，"最强"是规则判定，不是统计显著。
- **选择偏差**：报告中的分数就是扫参时的分数。PLAN 要求的"用新副本重跑胜出档出最终分"未做；对外引用 g1k 分数前应补跑。
- **加赛用掉了"未参与扫参的套件"**：boundary / assistant / smoke / primitive 已参与选择，不能再作为独立验证。
- **greedy 不确定**：两副本相差 1 题，后端批处理组合带来抖动。
- **共享端点**：运行期间有他人请求；并发与吞吐受此影响，结果不受影响（闸门与快照一致）。
- 只测了 g1k 格式、thinking=off；"空思考预填"等格式维度未交叉（见下）。

## 8. 复现

```bash
go build -o bin/rwkv-cli ./cmd/rwkv-cli
export RWKV_CF_ID=… RWKV_CF_SECRET=…
python3 .claude/skills/rwkv-bench/sweep.py --out runs/bench-YYYYMMDD \
  --arms greedy,t03-p10,t03-p05,t06-p10,t06-p05,t10-p10,t10-p05,backend,backend-nopen \
  --suites workbank,bfcl-product --k 0
python3 .claude/skills/rwkv-bench/rank.py runs/bench-YYYYMMDD
```

单次使用预设：`rwkv-cli agent-eval --sampling g1k-agent …`。

## 9. 后续

1. **格式 × 采样矩阵**：用 `g1k-agent` / `g1k-agent-fast` 交叉测空思考预填（thinking=fast）等格式维度。
2. 胜出预设用新副本补跑全 7 套，得到可对外引用的 g1k 分数。
3. 把 §5 的训练靶子交给语料 / state 侧。
