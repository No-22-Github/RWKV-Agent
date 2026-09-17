# 模型缺陷档案 v0（骨架）

> 模型侧视角：模型怎么错。内容**从跑分轨迹里积累**，不预先编写。
> 缺陷属于「模型 × state × wire × 轨迹」，不属于题目——同一道题，不同配置可能栽在完全不同的地方，所以缺陷标在失败轨迹上（`ledger/labels.jsonl`），不打在题目 tag 上。

## 1. 失败模式词表（`mode`，封闭）

每条失败轨迹标一个主模式，可选一个次模式。判定尽量依据 trace 里可观测的事实。

| mode | 名称 | 判定 |
|---|---|---|
| FM-TRAPHIT | 陷阱命中 | 最终答案等于题目 `tags.trap_decoys` 中某个陷阱的预期错误答案。**自动标注**，次模式写陷阱 ID |
| FM-NOREAD | 没读就答 | 答案依赖的文件或来源从未被读取或搜索 |
| FM-IGNORE | 读了没用上 | 观测里出现过正确值或关键规则，答案与之不符，且不是计算错 |
| FM-EARLYSTOP | 过早停止 | 只取了部分必要来源就作答（如两份日志只读了一份） |
| FM-MISSCALL | 该调没调 | 需要工具的题直接作答或弃权（含 `direct_final`、`semantic_no_call`） |
| FM-OVERCALL | 不该调乱调 | 不需要工具的题发起了调用 |
| FM-LOOP | 重复调用循环 | 连续 ≥ 2 次相同调用，或 duplicate reject ≥ 2，或触顶轮次且后半段调用高度重复 |
| FM-WANDER | 探索发散 | 冗余度（实际调用 / `ref_calls`）≥ 2.5 且不属于 FM-LOOP |
| FM-DROP | 链路中丢数据 | 前面步骤拿到的值，在后面步骤里用错或丢失 |
| FM-CALC | 计算错 | 输入取对了，运算结果错 |
| FM-FORMAT | 格式错 | 宽松判定能过、严格判定不过（多了单位、千分位、解释文字） |
| FM-PROTOCOL | 协议违规 | 工具调用格式损坏、think 泄漏进正文、harness 修复或拒绝 |
| FM-SCOPE | 越权操作 | 触发 `forbidden_tools` 或 `expect.files.unchanged` 失败 |
| FM-INJECTED | 被注入带偏 | 答案或动作与 fixture 内注入指令一致 |
| FM-OTHER | 其他 | **必须附一句 note**；同一现象在 note 里出现 ≥ 3 次时提议增设新 mode |

规则：
- LLM 可预标，`confirmed=false`；人确认后置 true。**统计只用 confirmed 标签。**
- FM-TRAPHIT 与另一个模式可以同时成立（例如因 FM-NOREAD 而命中陷阱），主模式记更上游的那个原因。

## 2. 缺陷条目模板

```
### D-NNN <一句话名称>
- 状态：观察 | 候选 | 确认 | 退役
- 现象：模型具体做了什么（可观测行为）
- 诱因假设：什么输入条件触发（没验证前写「假设」）
- 关联 mode：FM-...
- 证据：
  - <run_id 或报告路径> · <配置：模型 / state / wire> · <题集> · <出现次数 / 分母>
- workbank 复现：未跑 | <run_id> · <出现题数> · <涉及 family 数>
- 控制实验：无 | <去掉诱因通过、加上诱因失败的配对题与结果>
- 探针题：无 | <case id 列表>
- 修复记录：<哪个 state / wire / 语料版本后不再出现>
```

## 3. 状态门槛

| 状态 | 门槛 | 用途 |
|---|---|---|
| 观察 | 在任一 run 的轨迹中见过 | 只记录 |
| 候选 | workbank 上 ≥ 2 次 run、≥ 3 个不同 family（或无 family 的不同题）复现 | 进入控制实验排期 |
| 确认 | 做过控制实验：同骨架去掉诱因能过、加上诱因失败，且在 ≥ 2 个 family 上成立 | **才可以**用于定语料配比、写探针题（占题库预留的 10% 名额） |
| 退役 | 连续两个可比键下的新配置不再出现（≤ 原出现率的 20%） | 保留条目，注明被哪次改进修复 |

门槛理由：题库外的证据（bfcl-product、boundary、primitive-bench）来自不同题集和配置，只能证明「见过」；同一题集上的偶发失败可能是 temp 0 刀尖 token 翻转，必须跨 run、跨 family 才算稳定现象。

## 4. 已有观察条目（来自题库之外，workbank 尚未复现）

### D-001 检索工具在场时对参数知识题反射性调用
- 状态：观察
- 现象：「底 10 高 5 求三角形面积」这类题去调 `search_text` 搜工作区，搜完再搜，答案本身是对的
- 诱因假设：目录里有检索型工具 + 题面含可被当作查询词的名词
- 关联 mode：FM-OVERCALL
- 证据：
  - 自建 agent-eval `bfcl-product` · RWKV7-7.2B（无 state / 旧 XML state ctx-1024 / ctx-2048）· legacy wire · 24 个失败里 18 个来自 irrelevance，全部含 `search_text`
  - 同套件 · G1K · 消融后最终 wire · 剩余失分首位靶子为 8 道实质性 no-call 题
- workbank 复现：未跑

### D-002 重复调用，与 state 无关
- 状态：观察
- 现象：已经调过的同一调用再次发出，被 harness duplicate 拒绝
- 诱因假设：「已调用过」这一信息在 recurrent state 中未保留
- 关联 mode：FM-LOOP
- 证据：`bfcl-product` · RWKV7-7.2B 三种 state 配置 · 每个 run 36–37 次 duplicate reject / 145–146 次 tool_done，约四分之一，三个配置几乎一样
- workbank 复现：未跑

### D-003 ReAct 循环中逐字重复 thinking 与调用直至轮次耗尽
- 状态：观察
- 现象：同一段 thinking + 同一调用逐字重复，直到 max turns（14），从不推进到读文件或提交
- 诱因假设：多列数值表 + 需要映射规则的计算题
- 关联 mode：FM-LOOP
- 证据：
  - 上游 primitive-bench（marty1885）· g1i preview 3260 7.2B · llama.cpp Q8_0，4 路并发 · 13 个失败中 8 个触顶
  - 同题 Q8 单请求与 F16 单请求重跑：csv_sum、csv_reconcile_returns、fx_column_trap、loc_interest_8_months 三种条件下轮次完全相同且都触顶
  - DRY 采样惩罚使循环数减半（8→4），但总分从 17/30 降到 14/30
- workbank 复现：未跑

### D-004 think 泄漏引发协议失败循环
- 状态：观察
- 现象：思考内容泄漏进正文，解析失败，重试后再次泄漏
- 关联 mode：FM-PROTOCOL（次：FM-LOOP）
- 证据：G1K · 消融后最终 wire · 剩余失分靶子中 5 个（见 RWKV-Agent `docs/evaluations/g1k-wire-ablation/` 与 07-think-fast 轮修正）
- workbank 复现：`closeout-*-g1k`（2026-09-17，harness v21，贪心，并发 40）· **首步 think 不闭合**：workbank V0/V1/V2/V3 = 4/4/4/4 题（cfg-0003、log-0001、log-0004、web-0001 为主），噪声跑 par8 = 4/5；bfcl-product 6/6/5/5（全部集中在 irrelevance 与首步）；boundary 0；DeepSeek 0。usermsg 变体对该现象无影响（连续 User 不是诱因）
- 控制实验：V0–V3 改变连续 User 结构与 answer 阶段收尾，首步 think 不闭合率不变（4/40）→ 与 transcript 尾部结构无关

### D-010 工具调用中的训练残留绝对路径
- 状态：观察
- 现象：模型在工具参数里使用 `/home/node/.openclaw/...`、`/workspace/...` 等训练残留绝对路径约定；harness 的 absoluteCandidates 映射会容忍其中一部分
- 关联 mode：FM-PROTOCOL（次：FM-NOREAD，路径错导致读不到时）
- 证据：
  - v2-g1k-k0（harness v20）：40 题中 34 次绝对路径参数
  - **宿主路径泄漏已于 harness v21 修复**（工具报错一律改为工作区相对路径；修复前 v1/v2 首轮跑在 doc-0002 各泄漏 1 次宿主 temp 路径）。修复后重测：closeout v0/v1/v2/v3 = 15/17/9/15 次绝对路径调用——**泄漏消除后仍稳定出现，判定为模型习惯（训练残留），不是被泄漏诱导**
- workbank 复现：见上（4 个变体 run 均复现）
- 备注：harness 侧可观测性改进（记录 path-mapping 命中次数）仍未做，留待扩量期

### D-011 answer 阶段复读上一条 tool_call
- 状态：候选
- 现象：进入 answer 阶段后，模型输出与 transcript 中最近一条 assistant tool_call **逐字节相同**（或复读更早的调用 / 编造新调用），0 次纯文本收尾；被拒绝后原样再发直至触顶
- 诱因假设：~~连续 User 消息离分布外~~（**已被控制实验否定**，见下）。当前未归因；方向性猜测：吸引子是 transcript 里自己的 tool_call 历史本身，与 User 块结构无关——V3 回滚被拒输出后，模型转而复读更早的成功调用（earlier-call 复读 0 → 6/39）
- 关联 mode：FM-LOOP（次：FM-PROTOCOL）
- 证据：
  - v2-g1k-k0：34 次 answer 生成，22 次逐字节复读上一条 + 4 次复读更早 + 0 次纯文本
  - closeout V0（干净基线）：23/34 复读上一条（67.6%），纯文本 0
- workbank 复现：`closeout-v{0,1,2,3}-g1k` + 2 个噪声跑 · 6 个 run 全部复现 · 涉及全部 10 个 scenario 的多步题
- 控制实验：**已做**（2026-09-17，usermsg 轴）。V1 合并连续 User / V2 再去 nudge / V3 再回滚被拒输出+换无目录 System+单条收尾指令，三轮均通过「每次生成前 ≤1 连续 User」的逐轨迹断言；结果：通过数 3/40 不变、题级翻转 0、收尾率 11.8%→10.8%→10.5%→**0%**、复读率 67.6%→59.5%→81.6%→**87.2%**。连续 User 假设未被证实；最干净的 V3 反而最差
- 探针题：无（下一轮：fake think 前缀叠加在基线 wire 上，不与 usermsg 混合）

### D-005 需要工具时以 no-call 弃权
- 状态：观察
- 现象：严格需要工具序列的题上，模型走 no-call 出口
- 诱因假设：wire 的 no-call 出口 + 去掉示例块后调用倾向整体下调
- 关联 mode：FM-MISSCALL
- 证据：`boundary`（18 题）· G1K · 加入出口后 8 次 `semantic_no_call`，boundary 从 4/18 降到 1/18
- workbank 复现：未跑

### D-006 需要工具时凭空作答
- 状态：观察
- 现象：不调工具直接给出答案（通常是编造的）
- 关联 mode：FM-MISSCALL（次：FM-NOREAD）
- 证据：`boundary` · G1K · bare 配置下 12 次 `direct_final`，0/18
- workbank 复现：未跑

### D-007 长提取悬崖
- 状态：观察
- 现象：工具结果超过某个长度后，从中提取目标值的成功率骤降
- 诱因假设：单次观测长度落在约 4673–5021 真实 token 附近
- 关联 mode：FM-IGNORE / FM-LOOP（整页回灌后易进入重复 fetch）
- 证据：RWKV-Agent `docs/evaluations/preference-rebuild-20260831/harness-round3-report-20260831.md`；整页回灌 1/10 vs 压缩后 9/10（P5）。配置：**待从报告补填**
- workbank 复现：未跑

### D-008 示例块诱导虚构检索
- 状态：观察
- 现象：系统提示里有工具调用示例时，模型对各种问题都编出检索动作
- 关联 mode：FM-OVERCALL
- 证据：`bfcl-product` · G1K · 去掉完整 few-shot 示例块单项 +9 分
- 备注：这是 wire 层诱因，workbank 只记录，不针对它出题
- workbank 复现：未跑

### D-009 遗忘可用工具
- 状态：观察
- 现象：对话推进后不再使用某些可用工具，或声称没有该能力
- 证据：marty1885 向 BlinkDL 反馈的已知失败模式（需要学会 tool_search / tool_list）；**尚无内部轨迹证据**
- workbank 复现：未跑

## 5. 维护流程

每轮跑分入账后：
1. 自动标 FM-TRAPHIT，其余失败按 level × scenario 分层抽 30–50 条，LLM 预标、人确认
2. 已有条目：更新「workbank 复现」计数，满足门槛则升级
3. 新现象：先以「观察」建条目，写清证据与配置
4. FM-OTHER 的 note 聚类，达到 3 次提议新 mode（改词表须同步 `tag-vocab.json` 并记 changelog）
5. 「确认」级条目排期写探针题（预留名额），探针题同样走出题流水线
