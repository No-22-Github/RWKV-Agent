# Sonnet 补题 g2 批：中文直接回答 10 题

出题模型 claude-sonnet-5-5，全部 draft，放在 `bench/exam/pilots/sonnet-20261015/g2/cases/notool/nt-13001 ~ nt-13010`（30 个文件）。未并入正式考卷、未提交。

## 题目清单

| ID | task_type | 难度 | 题面 | 判分 |
|---|---|---|---|---|
| nt-13001 | smalltalk | L0 | 「你好呀，你都能帮我干点啥？」 | 零调用 + 有回答 |
| nt-13002 | smalltalk | L0 | 「哈哈今天终于周五了，你有没有什么周末计划呀」 | 同上 |
| nt-13003 | smalltalk | L0 | 「谢谢你啊，昨天那个问题搞定了……你是真人还是机器人呀？」 | 同上 |
| nt-13004 | concept | L1 | TCP 和 UDP 有啥区别 | 零调用 + 关键词（可靠/握手/无连接/reliable 等） |
| nt-13005 | concept | L1 | 同事老说接口要做幂等，是啥意思 | 零调用 + 关键词（多次/重复/相同结果等） |
| nt-13006 | stable_fact | L1 | 光在真空里一秒钟跑多远（工作区有声速笔记作干扰） | 零调用 + 30万/299792/3×10^8 等写法 |
| nt-13007 | stable_fact | L1 | 水烧开多少度、华氏多少（工作区有高原沸点表作干扰） | 零调用 + 100 与 212（整词） |
| nt-13008 | ambiguous_request | L1 | 「那个配置里的超时时间太短了，老是断，帮我调长一点」（dev/prod 两份） | 零调用 + 反问要点同义词组（哪个/哪份/多少/dev/prod…） |
| nt-13009 | ambiguous_request | L1 | 「周会那份笔记帮我删了吧，已经用不着了」（三份周会笔记） | 零调用 + 反问要点同义词组 |
| nt-13010 | beyond_capability | L1 | 订明天早上去杭州的高铁票 | 拒绝词表 + 排除 UNKNOWN + forbidden_tools（write_file/bash/replace_lines/append_file）；不放成功短语排除 |

分布与任务单一致：闲聊 3、概念/常识 4、反问 2、做不到 1；全中文；L0×3、L1×7。有工作区文件的题，源文件都加了 `unchanged: true` 保护。

## 本地检查

- **lint**：10 checked，3 violation，全是 smalltalk 与 bank lint 的已知冲突（nt-13001/2/3：lint 要求 smalltalk 的 `output_contains_any` 非空）。按任务单和规格书"smalltalk 不要加关键词"的原则，没有硬塞关键词。其余 7 题 0 violation。
- **verify**：4 题 ok；nt-13001~3 无 verify.py（verify 对 smalltalk 允许缺省，报跳过）。nt-13004/6/7/8/9/10 共 6 题仅 `sabotage_undetected`：答案来自常识或用户消息，改坏工作区里的干扰文件答案理应不变，属探针对"答案不来自 fixture"的误报，未加无关断言。nt-13005 无 fixture 直接 ok。
- **负向测试**：因没有数字题，改在隔离副本里给 nt-13006 的 `output_contains_any` 多加一项，verify 报 FAIL（set 不一致），说明 verify.py 确实在对比判分表而不是照抄。

## DeepSeek 盲解（r1，8/10）

输出目录 `local/runs/exam-gapfill-sonnet-20261015/g2-deepseek-r1`，harness app、thinking disabled、并发 6。

| ID | 结果 | 归类 |
|---|---|---|
| nt-13001~13007、13010 | 通过 | 已读回答：闲聊自然；概念/常识回答正确，没有蒙对；13010 明确说无法订票，没写文件 |
| nt-13008 | 失败 | DeepSeek 真不会（工具选择）：先列目录读了两份配置，再正确反问环境和目标值；失分只因违反零调用 |
| nt-13009 | 失败 | 同上：先列目录再让用户选哪一份，没有删除 |

"题有问题"清零，没有修题，所以没有 r2。13008/13009 的 NOTES 已写 `## Teacher result`。一个可讨论点：这两题的反问内容 DeepSeek 都答得对，被扣的是"看一眼工作区"这个动作；规格书（nt-6002）要求零调用，我保留了。若主 Agent 认为"先只读后反问"也可接受，这两题的判分应改，我认为不该由出题方单方放宽。

## 去污染

v1 / v1.3 / v1.4 / v1.41 / v2.0 全部 0 flagged（v1.42 本地没有 cases 目录，未执行）。

## 发现的问题（只记录）

1. bank lint 的 smalltalk 规则要求非空 `output_contains_any`，与"smalltalk 不锁关键词"冲突（三轮试点都遇到）。
2. verify 的破坏探针对"答案来自常识/消息"的题误报，6 题受影响。
3. 开工后 `git status` 显示 `bench/exam/imported/bfcl-product/*/case.json` 有未提交改动，不是我改的（我没动 imported），可能来自其他批次或 lint 的写回，请主 Agent 确认。
