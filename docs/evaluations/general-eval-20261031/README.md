# 通用能力评测（general-eval v1.0）与 G1L 基模快测基线

日期：2026-10-31。工具：`rwkv-lab geval`（`internal/lab/geval/`）。题集：`bench/general-eval/v1.0/`（数据仓库，见 [bench/general-eval/README.md](../../../bench/general-eval/README.md)）。

## 为什么要这套

考卷（agent-exam）只测我们 10 个工具的 Agent 任务。think-sft 包（`think-sft-pack-20261031b`，日常对话 1 万 + Agent 1 万）
还想带来的东西——日常对话、中文多轮、思考质量、指令遵循——考卷测不到。这套题补这一块，
用法是**同基模训练前后对照**（以及和 Qwen3.5-4B 比），不是和公开榜单比绝对分。

## 题目构成

| 项 | 全量 | 快测 | 抽法 | 判分 |
| --- | ---: | ---: | --- | --- |
| IFEval 英文 | 541 | 180 | 全量 | 规则（Google 原版规则的 Go 移植），主指标 prompt-level strict |
| IFEval 中文 | 541 | 180 | 全量 | 规则（Marco-Bench-MIF 版规则），同上 |
| MT-Bench 英文 | 80 | 27 | 全量，每题 2 轮；快测按 8 类分层 | DeepSeek v4.1-flash 按 FastChat 单答打分 1–10 |
| MT-Bench 中文 | 80 | 27 | 同上 | 同上，用 MT-Bench-ZH 的裁判提示词 |
| GSM8K | 500 | 167 | 从 1319 随机抽 | `\boxed{}` 里的数（没有就取最后一个数） |
| MATH-500 | 200 | 67 | 从 500 按难度分层抽 | `\boxed{}` 规则比对；不等时请裁判判等价 |
| C-Eval | 250 | 83 | val 集按 52 科分层抽 | 选项字母 |
| CMMLU | 250 | 83 | test 集按 67 科分层抽 | 选项字母 |
| **合计** | **2442** | **814** | | |

BFCL 全量（3641 题）不在这套里，需要时用现有 `rwkv-cli bfcl-eval` 单独跑，只比训练前后。

**中文 IFEval 选 Marco-Bench-MIF `zh_local` 的理由**：它是 IFEval 541 题逐题对应的中文版，而且是**本地化**改写
（题材换成杭州西湖、长城关隘这类，不是机翻），ACL 2025 发表，apache-2.0，自带改过的中文判分规则（中文按字计数、
中文逗号算逗号、中文版 yes/no 固定句式）。其他候选：Multi-IF（facebook）是多轮且 CC BY-NC，P-MMEval 的 IFEval 没有中文，
M-IFEval 没有中文。注意它给 538/541 题都加了"用简体中文回答"一类的语言约束，所以中文版的语言检查项远多于英文版。

**抽样**：种子 `20261031`；每个 task、每种用途（全量/快测）各自一条 PCG 随机流（由种子+task 名哈希得到），
改一个 task 不影响别的；分层用最大余数法按层大小分配名额。`geval build` 两次输出 sha256 相同（已验证）。
题源固定到具体提交，见 bench 侧 README 的许可表（C-Eval CC BY-NC-SA、CMMLU CC BY-NC，仅研究用）。

## 格式（与 think-sft 训练一致）

```
User: 问题\n\nAssistant: <think            ← 单轮，生成点停在 <think，模型自己补 >
User: q1\n\nAssistant: <think></think>a1\n\nUser: q2\n\nAssistant: <think   ← 多轮
```

- 不加 System；历史回答写空思考块；所有块（用户问题、历史回答）都按 `collapse_blank.py` 的规则压空行、去行尾空格。
- 停止：整数停止 token `0,24281`（EOS、`User`）+ 客户端文本停止串 `\n\nUser:`。
- 终答取 `</think>` 之后的文本；思考没闭合就当作没有答案（计错）。
- 预算 8192 生成 token；采样 `agent-fast`；复读检测开（循环时提前按 length 结束）。
- chat 模型（Qwen）走 `--completion chat-completions`，用模型自己的对话模板，思考取 `reasoning_content`。

数学题末尾追加 `Please reason step by step, and put your final answer within \boxed{}.`；选择题加题头
`以下是一道单项选择题，请选出正确答案。` 和结尾 `请在回答的最后一行写出“答案：”加选项字母。`

## 污染检查

对每题的原题文本（`raw`，不含我们加的说明）取 13-gram（英文按词、中日韩按字），在训练包
`train-rows.jsonl`（40037 行）+ `validation-rows.jsonl`（826 行）全文里查，算覆盖率（命中的 n-gram 占比），≥0.5 记为污染。

| task | 题数 | 有任一 13-gram 命中 | 覆盖率 ≥0.2 | ≥0.5（剔除） |
|---|---:|---:|---:|---:|
| ifeval-en | 541 | 3 | 1 | 0 |
| ifeval-zh | 541 | 0 | 0 | 0 |
| mtbench-en | 80 | 1 | 0 | 0 |
| mtbench-zh | 80 | 3 | 0 | 0 |
| gsm8k | 500 | 0 | 0 | 0 |
| math500 | 200 | 1 | 1 | 0 |
| ceval | 250 | 2 | 0 | 0 |
| cmmlu | 250 | 3 | 0 | 0 |

**没有一题被剔除。** 覆盖率最高的两题看过原文：math500/179（0.47）命中的是 MATH 训练集另一道平面方程题的同款作答格式说明；
ifeval-en/3756（0.41）命中的是 `My answer is yes./no./maybe.` 这组固定选项句。都是模板，不是泄题。
训练包里 IFEval 式约束句很少（"in all lowercase letters" 只出现在 6 行），GSM8K/MATH-500 原题 0 命中。
结果写在每题的 `contam` 字段里；分表里若有被剔除的题，会额外给出"净分"。

## 跑法

```bash
go build -o local/bin/rwkv-lab ./cmd/rwkv-lab
```

iRWKV（无适配器，基模）：

```bash
NO_PROXY=100.64.0.5 local/bin/rwkv-lab geval run --completion irwkv --api-url http://100.64.0.5:8103/v1 --model rwkv-7.2b --subset quick --parallel 48 --out local/runs/geval-YYYYMMDD/<名字>
```

rwkv_lightning + 适配器（NoRA/MiSS 先用 `rwkv-cli adapter register` 注册）：

```bash
local/bin/rwkv-lab geval run --completion rwkv-lightning-cuda --api-url <端点>/v1 --model <模型id> --adapter-id <适配器id> --batch-inflight <卡数> --subset quick --parallel 64 --out local/runs/geval-YYYYMMDD/<名字>
```

Qwen（vLLM 等 OpenAI 兼容端点）：

```bash
local/bin/rwkv-lab geval run --completion chat-completions --api-url <端点>/v1 --model <模型> --subset quick --out local/runs/geval-YYYYMMDD/<名字>
```

评分与对照（裁判走 Command Code 上的 DeepSeek，判过的题缓存在 `<run>/judge.jsonl`，重评不重复花钱）：

```bash
source ~/.commandcode_key.sh && local/bin/rwkv-lab geval score --judge-url "$API_BASE" local/runs/geval-YYYYMMDD/<名字>
```

```bash
local/bin/rwkv-lab geval report <基线 run> <对照 run>...
```

- 每题结束立刻追加到 `<run>/results.jsonl` 并 fsync；中断后**原命令重跑**即续跑，出错的题自动重试；配置变了会拒绝续跑（`RESUME REFUSED`）。
- `--subset full` 跑全量 2442 题；`--tasks gsm8k,math500` 只跑部分项；`--limit 2` 每项只跑 2 题（冒烟）。
- `report` 给多个 run 并排的分表、输出统计，以及每个 run 对第一个 run 的逐题翻转（赢/输）与符号检验 p。
  MT-Bench 是 1–10 连续分，不进翻转表。

## 判分细节与已知偏差

IFEval 判分是 Go 移植，Python 依赖库 Go 没有，以下几处是近似：

- 语种识别：`langdetect` → `whatlanggo`（先按文字系统，再按三元组），中文报 `zh-cn`。
- 英文句子数：nltk punkt → 规则切分（`. ! ?` + 常见缩写表）。
- 中文句子数：按 `。！？…` 切。Marco 原代码仍用英文 punkt，中文整段算一句，"至少 N 句"必挂；这里改了。
- `capital_word_frequency` 的 nltk 分词 → 正则分词。
- 中文"用双引号括起来"：Marco 原代码只认英文 `"`，这里也认 `“…”`。

**还没做的验证**：拿 Google/Marco 官方 Python 判分器对同一批回答逐条对拍。准备好的对拍脚本被本机安全策略拦下
（不允许执行下载来的代码），需要用户放行或自己跑。目前的依据是单测（48 条 IFEval 已知用例）+ 人工抽看中文失败样本（都是模型真没照做）。

其余：

- MT-Bench 回答为空（思考没闭合）直接记 1 分，不请裁判；裁判输出解析不到 `[[分]]` 记 −1 并排除（本次 0 例）。
- MATH-500 规则判等价（Hendrycks `strip_string` + 数值比较），不等时请裁判回答 YES/NO；本次 2 题靠裁判改判为对。
- 选择题抽取顺序：`答案：X` → `\boxed{X}` → `answer is X` → 加粗选项 `**C. …**` → 最后一行的孤立字母。
- **格式性失分**：IFEval 的 `nth_paragraph_first_word` 要求用空行分段，而 RWKV 的块内不出现空行（训练格式如此），
  基模这一项 0/13。对照时这项不说明能力变化。

## 统计项（从输出直接算，不额外出题）

- **思考闭合**：输出是完整的 `<think>…</think>`。
- **空思考**：`<think></think>` 里没内容。分 turn1（无历史）和 turn2（MT-Bench 第二轮，历史里有空思考块）。
- **思考语言=题目语言**：思考里汉字数 ≥ 英文词数记为中文，和题目语言比。
- **复读**：复读检测触发（最近 768 字符里新出现的 24 字片段 <5%），这时生成提前按 length 结束，所以"撞上限"基本等于复读。
- **思考字数 p50/p90、生成 token p50、回答字数 p50**：按 task 分开，简单题（选择题、GSM8K）看思考是不是过长。

## G1L 基模快测基线（iRWKV 8103）

- 模型：`rwkv-7.2b` = `rwkv-g1l-7b-temp-3797`（iRWKV 0.1.dev6+gf3177b596，WKV 状态 fp16、前缀缓存关）。
- 814 题，48 并发，生成 13 分 52 秒，0 作废；评分 75 秒（裁判 DeepSeek v4.1-flash，`deepseek/deepseek-v4.1-flash`）。
- 代码：fed6925e + 本次未提交的 geval（run.json 记为 `-dirty`）；之后只补了选择题加粗写法的抽取规则，已对本 run 重评。
- 产物：`local/runs/geval-20261031/irwkv8103-base-quick/`（不入库）。

### 分数

| 项 | 指标 | 基模 |
|---|---|---:|
| ifeval-en | prompt_strict | **60.6** |
|  | inst_strict | 69.1 |
|  | prompt_loose | 62.8 |
|  | inst_loose | 70.9 |
| ifeval-zh | prompt_strict | **48.9** |
|  | inst_strict | 68.9 |
|  | prompt_loose | 51.7 |
|  | inst_loose | 70.3 |
| mtbench-en | score | **6.20** |
|  | turn1 | 6.96 |
|  | turn2 | 5.44 |
| mtbench-zh | score | **5.44** |
|  | turn1 | 6.41 |
|  | turn2 | 4.48 |
| gsm8k | acc | **74.8** |
| math500 | acc | **70.1** |
| ceval | acc | **56.6** |
| cmmlu | acc | **53.0** |

### 输出统计

| 项 | 思考闭合 | 空思考 | 思考语言一致 | 复读 | 思考字数 p50 / p90 | 生成 token p50 | 回答字数 p50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ifeval-en | 86.7% | 0% | 100% | 18.9% | 1919 / 4978 | 657 | 726 |
| ifeval-zh | 90.0% | 23.9% | 97.1% | 13.9% | 643 / 2186 | 780 | 316 |
| mtbench-en | 87.0% | 33.3% | 100% | 13.0% | 2463 / 8282 | 655 | 649 |
| mtbench-zh | 77.8% | 24.1% | 100% | 22.2% | 891 / 2711 | 963 | 247 |
| gsm8k | 77.8% | 0% | 100% | 22.2% | 2687 / 6632 | 746 | 467 |
| math500 | 71.6% | 0% | 100% | 22.4% | 1448 / 16660 | 558 | 301 |
| ceval | 72.3% | 0% | 97.6% | 27.7% | 1056 / 2642 | 735 | 4 |
| cmmlu | 71.1% | 0% | 100% | 27.7% | 710 / 3131 | 590 | 4 |

带历史时的空思考：turn1 5.7%（46/814）→ **turn2 51.9%（28/54）**。和今天 Agent 格式基线（历史有空思考块时 77% 步骤照抄）同一个毛病，
程度轻一些。

### 读法

- **基模最大的问题是思考停不下来**：选择题有 28% 在思考里绕圈触发复读检测、思考没闭合就没有答案。
  GSM8K/C-Eval/CMMLU 的"没抽到答案"全部来自这一类（抽取规则本身只漏过 1 题，已补）。所以这几项的分数 ≈ "不复读率 × 答对率"，
  训练后复读率下降本身就会抬分，对照时要和复读率一起看。
- 简单题思考偏长：C-Eval 中位 1056 字、GSM8K 中位 2687 字。
- 中文 IFEval 比英文低 12 分，主要掉在重复题干（2/12）、两段式回答（2/10）、句子数（6/18）、无逗号（7/17）、引号包裹（10/24）。
- 中文题思考语言基本是中文（97–100%），与 Agent 任务里"中文题只有约 3 成用中文想"不同。
- MT-Bench 第二轮普遍掉 1.5–2 分，和空思考照抄（第二轮一半不想）同时出现。

## 下一步

对照组：temp-3797 上的 think-sft `checkpoint-5004`（NoRA r16 lr2e-5，约第 1 轮结束）vs 同端点基模。
适配器要挂在 rwkv_lightning 上（iRWKV 不能按请求挂适配器），需要用户提供端点并注册适配器；
基模要在**同一个 lightning 端点**上重跑一遍再配对，不和本页 iRWKV 的数混比。
