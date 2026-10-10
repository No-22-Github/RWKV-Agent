# 老师思考和 g1k 像不像（2026-10-10）

数据：DeepSeek-flash 与 MiniMax-M3.1-Flash 各跑 workbank 148 一轮（思考取自 `reasoning_content`）；g1k think-full 用 T、F 两组，各 3 轮，
取自 [think-shape.md](../think-full-20261010/think-shape.md) 的同一批 run。脚本 [think_compare.py](think_compare.py)（只读），
用的口径与 think_shape.py 相同：开头、收尾、是否引用上一步结果、分位数。bfcl 只比 irrelevance + missing 两类（共 30 题），
因为 DeepSeek 另外 30 题只能关掉思考跑。原始输出见附录。

## 结论

**两个老师彼此很像，和 g1k 都只是部分像。** 语言和段落形态一致；开头习惯、首步长度、长尾、自我推翻这几项都和 g1k 差得远。
DeepSeek 在「步步都想」上比 MiniMax 更接近 g1k，但首步更短、长尾更长。

| 维度 | g1k（T / F） | DeepSeek | MiniMax | 像不像 |
| --- | --- | --- | --- | --- |
| 思考语言（workbank） | 100% 英文 | 100% 英文 | 100% 英文 | 像 |
| 段落形态 | 单段，行数中位 1 | 单段，行数中位 1 | 行数中位 3 | DeepSeek 像 |
| 有思考的步 | 84% / 92%（预填 `<think`，几乎每步都想） | 69% | 44% | DeepSeek 较接近 |
| 首步长度中位 | 336 / 331 字符 | **71** | 237 | 不像：DeepSeek 首步只有一句「Let me look at the workspace.」 |
| 后续步长度 p50 / p90 | 214–229 / 591–721 | 193 / **1293**（最长 20427） | 311 / 1479 | 中位像，长尾不像 |
| 复述需求（思考里提到 `The user`） | 49% / 50% | 6% | 13% | 不像：老师直接写动作意图 |
| 自我推翻（Wait / Hmm / Actually） | 1% | **22%** | 24% | 不像 |
| 后续步引用上一步结果 | 79% / 75% | 60% | 71% | 偏低 |
| 中文题用中文想（bfcl） | 70% / 94% | 0% | 0% | 不像 |
| 通过题整条思考 p50 | 933 / 611 | 1078 | 1000 | 像 |

### DeepSeek 思考的三种样子

1. **一句话动作意图**（大多数短步）：`Let me look at the workspace.`、`Let's read the files.`、`Read all files.`。
   g1k 的同类步会先复述需求或总结上一步结果（`The user wants me to … Let me start by …`），DeepSeek 跳过这一句，有时连主语都省了，是电报式。
2. **算账步**（中等长度）：列出读到的数字，写出算式，和 g1k 的「引用具体值 → 下一步」形状接近。
3. **反复推敲的长尾**（13% 的思考步超过 900 字符）：`Hmm, but wait — could the intended trick be…`，围绕题目「是不是陷阱」打转。
   log-0017、log-0012 都是怀疑日志日期和 yesterday 对不上，绕了几千到两万字符，最后答 UNKNOWN 而失败。
   g1k 几乎没有这种自我推翻（1%）；它的长思考是另一种坏法：复读、写满预算不闭合。

bfcl 的不调工具题里，两个老师都写成 `We need answer. Need …` / `Final concise.` 这种极简电报体，g1k 则写完整句子，中文题还多半用中文想。

## 对训练数据的影响

- **长度过滤的代价可以接受**：按 think-shape.md 定的每步 ≤900 字符上限，DeepSeek 通过的 143 条轨迹里有 93 条（65%）整条达标，MiniMax 是 89/132（67%）。
  两者损失差不多。超长步大多出在通过题里（DeepSeek 80/89），也就是说「绕了一大圈最后答对」的轨迹占了不少。
- **首步太短是 DeepSeek 特有的问题**：照搬会把 g1k 原生的「复述需求 + 取证计划」首步教成一句话。可选做法：
  ① 接受（首步本来就只决定 list_files，信息量低）；② 在老师附加指令里要求先复述需求，再小批量看效果。
- **空思考步**：DeepSeek 31%、MiniMax 56% 的步没有思考。带思考版怎么处理这些步（写空 `<think></think>`，还是只作上下文不监督），
  这个待定问题对 DeepSeek 的影响比对 MiniMax 小。
- **自我推翻**：22% 的思考步带 Wait / Hmm。g1k 原生几乎没有，学进去可能放大打转；可以考虑把含「Hmm, but wait」又超过 900 字符的步整条丢掉，规则和长度过滤合并。
- **中文思考**：两个老师都不会在中文题里用中文想。g1k 在 bfcl 中文题里本来多半用中文想，训练后这一习惯可能被冲淡。workbank 全是英文题，不受影响。

**一句话**：选 DeepSeek 不会比 MiniMax 离 g1k 更远。它步步都想、单段英文、中位长度贴近，这几项更像 g1k；
首步过短和推敲长尾这两项要靠过滤或附加指令来压。think-shape.md 里「DeepSeek 长思考（中位 3000+ 字符）」那句不适用于
deepseek-flash：实测思考步中位只有 154 字符。

## 附录：think_compare.py 原始输出

# workbank

| 组 | 步数 | 有思考的步 | 首步有思考 | 终答步有思考 | 首步长度 p10/p50/p90/max | 后续步长度 | 行数 p50 |
|---|---|---|---|---|---|---|---|
| DeepSeek | 1019 | 704/1019 (69%) | 124/151 (82%) | 110/149 (74%) | 29 / 71 / 313 / 1128 | 22 / 193 / 1293 / 20427 | 1 |
| MiniMax | 988 | 433/988 (44%) | 50/151 (33%) | 59/146 (40%) | 58 / 237 / 797 / 1907 | 55 / 311 / 1479 / 15597 | 3 |
| g1k-T | 1609 | 1349/1609 (84%) | 453/453 (100%) | 262/263 (100%) | 177 / 336 / 835 / 6683 | 97 / 214 / 591 / 4368 | 1 |
| g1k-F | 1609 | 1483/1609 (92%) | 445/448 (99%) | 256/259 (99%) | 162 / 331 / 865 / 3181 | 92 / 229 / 721 / 8762 | 1 |

| 组 | 引用上一步结果 | 中文为主（中文题内） | Wait/Hmm/Actually | We need / Let's | The user … | Let me / I need | Markdown list/heading | code / JSON in think |
|---|---|---|---|---|---|---|---|---|
| DeepSeek | 350/580 (60%) | – | 154/704 (22%) | 176/704 (25%) | 43/704 (6%) | 425/704 (60%) | 33/704 (5%) | 7/704 (1%) |
| MiniMax | 273/383 (71%) | – | 106/433 (24%) | 127/433 (29%) | 57/433 (13%) | 318/433 (73%) | 44/433 (10%) | 8/433 (2%) |
| g1k-T | 729/923 (79%) | – | 11/1349 (1%) | 85/1349 (6%) | 665/1349 (49%) | 1079/1349 (80%) | 207/1349 (15%) | 16/1349 (1%) |
| g1k-F | 776/1035 (75%) | – | 15/1483 (1%) | 93/1483 (6%) | 738/1483 (50%) | 1167/1483 (79%) | 242/1483 (16%) | 20/1483 (1%) |

| 组 | 通过题整条思考 p50/p90（字符） | 失败题整条思考 p50/p90 |
|---|---|---|
| DeepSeek | 1078 / 4112 | 5308 / 26506 |
| MiniMax | 1000 / 4067 | 432 / 15023 |
| g1k-T | 933 / 22198 | 1120 / 22170 |
| g1k-F | 611 / 2827 | 1117 / 17021 |
- DeepSeek 首步开头：`Let me explore the` 17；`Let me start by` 17；`Let me look at` 16；`I need to find` 14；`The user asks about` 14；`We need to find` 7
- DeepSeek 后续步开头：`Let me read the` 25；`Let me read all` 15；`Let's read the files.` 7；`Read all files.` 6；`Let's read files.` 6；`Let's read all files.` 4
- DeepSeek 收尾：`Let me read the` 29；`Let me look at` 24；`Let me explore the` 23；`Let me start by` 20；`Let me read all` 15；`Let me search the` 12
- MiniMax 首步开头：`The user asks about` 13；`The user wants the` 7；`Let me look at` 5；`The user is asking` 4；`Let me explore the` 2；`The user wants me` 2
- MiniMax 后续步开头：`Let me read the` 12；`Let me also check` 4；`Workspace is empty. So` 4；`The file is now` 3；`Let me look at` 3；`Let me fetch the` 3
- MiniMax 收尾：`Let me read the` 21；`Let me check the` 14；`Let me look at` 10；`Let me list files.` 8；`Let me search for` 7；`Let me explore the` 6
- g1k-T 首步开头：`The user is asking` 162；`The user wants me` 123；`The user wants to` 17；`We need to answer:` 8；`The user asks: "The` 6；`The user asks for` 3
- g1k-T 后续步开头：`The search results are` 103；`The user asks for` 75；`The user wants the` 52；`The search did not` 45；`The read_file call failed` 31；`The user wants me` 31
- g1k-T 收尾：`Let me start by` 141；`Let me search for` 89；`I need to search` 81；`I need to try` 57；`I need to read` 26；`Let me first explore` 23
- g1k-F 首步开头：`The user is asking` 182；`The user wants me` 118；`The user wants to` 22；`We need to answer:` 13；`The user asks: "The` 8；`I need to find` 4
- g1k-F 后续步开头：`The user asks for` 74；`The search results are` 69；`The user wants me` 49；`The search did not` 48；`The user wants to` 31；`The user wants the` 29
- g1k-F 收尾：`Let me start by` 148；`Let me search for` 84；`I need to try` 76；`I need to read` 44；`Let me use the` 38；`I need to search` 33

# bfclp（irrelevance + missing，30 题/轮）

| 组 | 步数 | 有思考的步 | 首步有思考 | 终答步有思考 | 首步长度 p10/p50/p90/max | 后续步长度 | 行数 p50 |
|---|---|---|---|---|---|---|---|
| DeepSeek | 30 | 30/30 (100%) | 30/30 (100%) | 30/30 (100%) | 108 / 303 / 1291 / 5024 | – | 1 |
| MiniMax | 30 | 23/30 (77%) | 23/30 (77%) | 23/30 (77%) | 120 / 247 / 695 / 3526 | – | 1 |
| g1k-T | 173 | 143/173 (83%) | 90/90 (100%) | 79/79 (100%) | 39 / 351 / 980 / 2374 | 120 / 234 / 682 / 1199 | 1 |
| g1k-F | 157 | 139/157 (89%) | 90/90 (100%) | 78/79 (99%) | 39 / 393 / 1178 / 2455 | 146 / 284 / 678 / 3007 | 1 |

| 组 | 引用上一步结果 | 中文为主（中文题内） | Wait/Hmm/Actually | We need / Let's | The user … | Let me / I need | Markdown list/heading | code / JSON in think |
|---|---|---|---|---|---|---|---|---|
| DeepSeek | – | 0/10 (0%) | 4/30 (13%) | 27/30 (90%) | 7/30 (23%) | 8/30 (27%) | 2/30 (7%) | 0/30 (0%) |
| MiniMax | – | 0/9 (0%) | 0/23 (0%) | 23/23 (100%) | 0/23 (0%) | 1/23 (4%) | 0/23 (0%) | 0/23 (0%) |
| g1k-T | 34/55 (62%) | 21/30 (70%) | 1/143 (1%) | 18/143 (13%) | 77/143 (54%) | 80/143 (56%) | 3/143 (2%) | 4/143 (3%) |
| g1k-F | 25/55 (45%) | 30/32 (94%) | 12/139 (9%) | 21/139 (15%) | 76/139 (55%) | 76/139 (55%) | 6/139 (4%) | 6/139 (4%) |

| 组 | 通过题整条思考 p50/p90（字符） | 失败题整条思考 p50/p90 |
|---|---|---|
| DeepSeek | 303 / 1291 | – |
| MiniMax | 204 / 695 | – |
| g1k-T | 303 / 956 | 4283 / 17938 |
| g1k-F | 300 / 1117 | 2209 / 16636 |
- DeepSeek 首步开头：`We need answer. Need` 7；`We need to respond` 5；`We need answer simple.` 3；`We need answer. User` 3；`We need answer physics.` 2；`The user says they` 2
- DeepSeek 后续步开头：
- DeepSeek 收尾：`Final concise.` 3；`Ensure no tools.` 3；`Need direct.` 2；`Final only.` 2；`Maybe mention assuming =0.` 1；`Need concise.` 1
- MiniMax 首步开头：`We need answer. Need` 8；`We need respond Chinese,` 3；`We need answer in` 3；`We need answer calculate` 2；`We need answer simple.` 2；`We need answer Chinese.` 2
- MiniMax 后续步开头：
- MiniMax 收尾：`No tools.` 2；`Need perhaps explain.` 1；`Concise.` 1；`Ensure "roots" perhaps answer.` 1；`Concise with steps.` 1；`Need concise maybe steps.` 1
- g1k-T 首步开头：`The user asks for` 8；`The user is asking` 5；`The user asks: "How` 4；`We need to answer` 4；`The user wants me` 4；`The user asks: "What` 3
- g1k-T 后续步开头：`The user says: "Your` 8；`The user asks for` 7；`The user asks: "What` 7；`The user asks to` 4；`The search_text returned no` 4；`The calculator tool is` 3
- g1k-T 收尾：`Close the thinking block` 9；`Let me list the` 4；`No tool needed.` 3；`Thus final answer.` 3；`I'll list files in` 3；`Let me search for` 3
- g1k-F 首步开头：`The user asks for` 6；`The user is asking` 5；`The user wants me` 4；`Okay, let's see. The` 3；`The user asks about` 3；`The user asks: "How` 3
- g1k-F 后续步开头：`The user wants to` 7；`The user asks for` 6；`The user asks: "How` 4；`The user asks: "What` 3；`The search for "magnetic` 3；`The list_files call failed` 3
- g1k-F 收尾：`另外，用户提到“不要调用工具”，所以我不能使用任何工具来获取更多信息，必须直接回复用户。因此，正确的做法是向用户询问他们需要什么帮助，以便进一步处理。` 4；`No tool needed.` 3；`I'll list files in` 3；`Let me try searching` 3；`Let me list the` 3；`用户要求处理 score，但没有提供具体路径。我需要先询问路径，不能调用工具。` 3
