# v1.3 语料清洗报告

日期：2026-10-02。对象：合入 main 前的 `feat/distill-v1.3`（b05–b08 + base700）。本报告取代 [dataset-v13.md](dataset-v13.md) 的行数与构成数字；
那份报告的管线和闸门说明仍然有效。

## 做了什么

1. **机械扫描**：在全部老师脚本上扫垃圾文本、语言不匹配、重复与畸形调用、零调用却说出工作区内容、违背明确格式指令。
2. **逐条审查**：Sonnet 子 Agent 按同一份清单逐条读「题面 + 工作区文件 + 老师调用 + 老师回答」，判 keep / drop：
   新语料（b05 重解、b06、b07）773 条、存量 b01–b04 1127 条、base700 保留清单 202 条，全部过一遍。
   判分器只核对关键值，这一轮专查它看不到的东西：顺带说错的数字、无依据的断言、冗余调用、拒绝写成长篇报告、反问问偏。
3. **主控复核**：抽查全部 drop 理由。推翻 24 条：nt-7132 / 7160 / 7214 三道题的 `offered_tools` 只给了 read_file / list_files，
   声称「只有只读工具」是对的；hyb-7764 删除前先确认是 N8 规格要求的行为；web-7576–7595 的 20 条只是尾巴有 shell 残留，截掉后保留。

坏路径从 `bench/distill/scripts/*.jsonl` 里直接删除（base700 从 `v13/base700-v13-kept.json` 删除），每条原因写进 `exclude.jsonl`，
所以重放、收尾变换（N10）和打包都看不到它们。

## 发现与处置

| 问题 | 条数 | 处置 |
|---|---|---|
| web-7576–7595 终答尾部混入解题 Agent 的 shell 包装（`__zcode_status=$?` … `/tmp/zcode-*-cwd` … `exit`） | 20 | 截掉尾巴，保留轨迹 |
| 新语料：事实错误（README 写明优先级却说「无法判断」、多数一条记录、press2/press3 计数错、1 秒说成一分钟） | 8 | 删 |
| 新语料：英文题中文作答（cfg-7152/7153/7155/7156、log-7507/7509） | 6 | 删 |
| 新语料：同一行连发两次 replace_lines（先数组 content 再字符串）、畸形 / 重复 list_files、猜文件名、没读文件就断言内容、零调用说出文件名 | 11 | 删 |
| 新语料：反问会话第 2 轮同时要求「说明改了什么」与「只回最终答案」、任务明确仍反问、把「15 September」读成 15 条 | 4 | 删 |
| 新语料：闲聊里的胡话 / 推荐与需求相反（nt-7182、nt-7211） | 2 | 删 |
| 存量：零调用题在题面已给全部数值时仍调 4–8 次工具 | 约 45 | 删 |
| 存量：拒绝 / 闲聊写成带标题和表格的长篇报告，夹带臆测与说教 | 约 40 | 删 |
| 存量：反问没看工作区就问、问的不是真正的歧义点（多为 `--p42`） | 约 15 | 删 |
| 存量：事实 / 算术错误、凭空加币种、终答与自己的 calculator 结果不符 | 约 20 | 删 |
| 存量：题面要求 "reply DONE"，终答完全没有 DONE | 7 | 删 |
| base700：无关 datetime 冗余调用、看到路径之前就读文件 | 8 | 删 |
| b07：改题后旧轨迹按现行判据重放不过（render 必拒） | 9 | 从脚本删 |
| base700 保留清单里当前 render 不出行的 id（10 个加载失败 + 10 个判不过） | 20 | 从清单删 |

合计从训练来源中移除 **184 条路径**，原因见 `exclude.jsonl` 中 reason 以「v1.3 清洗」开头的条目。

## 重建结果

用合并后的 main 编译的 `rwkv-lab` / `rwkv-cli` 全量重放：五批 `wire_hash` 均为
`707c67403b1b2e5269ddfcd8ecee2bfb7ce4d8133912d102bc67f1324f8018cb`，渲染零拒绝；N10 收尾 100 行全部含两个收尾标记。

```bash
O=local/runs/distill/v13-clean
# base700：按保留清单过滤 records 后用 records 模式渲染
rwkv-lab corpus render --cases bench/distill/cases --script bench/distill/scripts/b05-baseline.jsonl --source distill-b05 --rotate-catalog 0.4 --out $O/b05
rwkv-lab corpus render --cases bench/distill/cases --script bench/distill/scripts/b06.jsonl --source distill-b06 --rotate-catalog 0.4 --out $O/b06
rwkv-lab corpus render --cases bench/distill/cases --script bench/distill/scripts/b07.jsonl --source distill-b07 --rotate-catalog 0.4 --out $O/b07
rwkv-lab corpus render --records $O/base700-records.jsonl --source base700 --rotate-catalog 0.4 --out $O/base700
python3 bench/distill/tools/v13_closeout.py --script bench/distill/scripts/b05-baseline.jsonl --script bench/distill/scripts/b06.jsonl --script bench/distill/scripts/b07.jsonl --out $O/closeout.jsonl --n 100
rwkv-lab corpus render --cases bench/distill/cases --script $O/closeout.jsonl --source distill-b08 --rotate-catalog 0.4 --out $O/b08
python3 bench/distill/tools/build_v13_suffix.py --rows $O/b05/rows.jsonl --rows $O/base700/rows.jsonl --rows $O/b06/rows.jsonl --rows $O/b07/rows.jsonl --rows $O/b08/rows.jsonl --out $O/rows-suffixed.jsonl
python3 bench/distill/tools/split_v13.py --rows $O/rows-suffixed.jsonl --train $O/train-rows.jsonl --validation $O/val-rows.jsonl
rwkv-lab corpus pack --rows $O/train-rows.jsonl --exclude bench/distill/exclude.jsonl --max-tokens 8128 --out $O/dataset/train
rwkv-lab corpus pack --rows $O/val-rows.jsonl --exclude bench/distill/exclude.jsonl --max-tokens 8128 --out $O/dataset/validation
```

| | 清洗前（dataset-v13.md） | 清洗后 |
|---|---|---|
| train / validation | 2365 / 81 | **2157 / 76** |
| 来源 b05 / b06 / b07 / base700 / b08 | 1341 / 586 / 234 / 188 / 97 | 1130 / 550 / 203 / 178 / 96（train） |
| 零调用 | 25.3% | 25.2% |
| token p50 / p99 / max | 1659 / 4070 / 6925 | 1649 / 4070 / 6925 |

§5 指标（train 2157 行，按每行最后一条真实用户消息统计）：

| 指标 | 目标 | 清洗后 |
|---|---|---|
| 中文行 | ≥28% | 21.1% |
| 多轮行 | ~18% | 10.0%（≥3 轮会话的行 4.3%） |
| 带英文「Reply with only the final answer」 | ≤50% | 48.8% |
| 含中文「只回数字」、"Just the number"、"reply DONE" 等各类只给答案模板 | — | 62.2% |
| UNKNOWN 契约 | ≤20% | 21.4% |
| data_query 占调用 | ≥10% | 3.8% |
| 用工具的首轮行里首动作是 list_files | ≤35% | 62.1% |
| write + script | ≥12% | 6.4% |

dataset-v13.md 的「只给答案 51.1%」只数了英文那一句；把中文与其他写法算进去是 62%，会话题（N3/N6）几乎每轮都是「只回数字」。
中文、多轮、data_query、write+script 仍未达标，缺口主要来自 N5 / N6 少出的 50 题，以及存量在总量里占比过大。

## 遗留

- `batches.jsonl` 没有登记 b04–b08，b05–b07 的解题老师是谁没有记录（题目 author 标签为 glm-5.3-flash-b06/b07）。
- b07 报告写 127 条路径，入库的 `b07.jsonl` 实际是 124 条（本轮清洗后 104 条）。
- 用户纠正错了、模型坚持原答案的会话只有 2 个（hyb-7711、log-7504，后者本轮因事实错误被删），规划要求约占纠正轮的 1/4。
- 新题里题面给了路径仍先 list_files 的约 23%（规划 ≤10%），其中一部分确实需要先看 README，没有删。

## 训练输入（2026-10-03，mask 训练器）

训练器 rwkv_lightning_cuda 47df608 起支持 `{"segments":[{"text","train"}]}` 掩码行：各片段**分别分词**，只对 `train=true` 的 token 算 loss；不追加 EOD；超过 `--ctx` 的部分直接截断。每行只允许 `segments` 一个字段。

```bash
python3 bench/distill/tools/to_segments.py --rows $O/dataset/train/rows.jsonl --out $O/dataset/train/segments.jsonl
python3 bench/distill/tools/to_segments.py --rows $O/dataset/validation/rows.jsonl --out $O/dataset/validation/segments.jsonl
```

- `loss_spans` 是**字符**偏移（754 行含中文的行按字符全部对齐，按字节只有 146 行碰巧对齐）。
- 区间起点都紧跟 `Assistant: `。转换时把这个空格划进训练片段：前缀以 `Assistant:` 结尾，和推理端 `AppendAssistantOpening` 一致，第一个 token（` <`、` 57`）由模型学着生成。按原区间切会拆开 ` <` 等 token，train 2073/2157 行的分词与整段不一致；前移后 0 行不一致（用仓库 World 分词器逐行比对）。
- 剔除 base700 中以 `no_tool(reason=答案)` 收尾的 104 个 case（train 101、validation 3，每个 case 一行），登记进 `bench/distill/exclude.jsonl`（batch base700），统一为纯文本终答；旧产物留在 `dataset-prev/`。
- 产物：train **2056 行**（segments sha256 `70cba078…`），validation **73 行**（`f69c83e1…`）。token p50 1629 / p99 4104 / max 6925，0 行超过 8192，0 行无训练片段；每行以训练片段 `\n\nUser:` 结尾（代替 EOD）。wire_hash 不变。
- 96 条收尾恢复行（validation 4 条）插入的重复调用都在训练片段之外，其后都是重复调用拒绝回执。
- 训练必须传 `--ctx 8192`，否则长行的终答会被静默截掉。
