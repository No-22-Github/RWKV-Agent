# bashprobe：沙箱 bash 能力探针

> **2026-10-15 起不要再运行 `gen.py` 重新生成 `cases/`。** 这些题已并入新考卷（`bench/exam/`），并按 App 用户的口吻改写过：
> 「回复 DONE」改成了自然说法，数字题改为在回答里找数字（`expected_number_in_text`），取消了字数上限，原题面保存在 `tags.legacy_prompt`。
> 生成器不知道这些改动，重新生成会把题改回旧版，并让考卷清单的哈希失配（`rwkv-lab exam lint` 会报 stale）。
> 改动记录：`docs/evaluations/bench-composition-20261015/REPORT.md` §8、`naturalize.py`。


26 道题，测模型在 `work-v2` 工具目录（work-v1 的 12 个工具 + `bash` + `get_weather`）下会不会用 bash、用得对不对。
题目由 [`gen.py`](gen.py) + [`cases_data.py`](cases_data.py) 生成：fixture 用固定种子造，答案在生成器里从同一份 fixture 算出，
每道题的参考 bash 解都先在真实的 just-bash sidecar 里跑过、对上答案才落盘。**改题只改生成器，不手改 `cases/`。**

```bash
scripts/build-justbash.sh                 # 先有 local/bin/justbash-sidecar
python3 bench/bashprobe/gen.py            # 重新生成并验证；--check 只验证不写
```

跑分（其余参数按 rwkv-bench 规程）：

```bash
./local/bin/rwkv-cli agent-eval ... --profile g1k --strict-spec \
  --cases bench/bashprobe/cases --tool-catalog work-v2 --file-tools lines --include-draft \
  --max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m --remote-batch-wait 0s \
  --output local/runs/bashprobe-YYYYMMDD/<model>-<arm>
```

## 题目轴（`tags.probe_axis`）

| 轴 | 题 | 想看什么 |
|---|---|---|
| aggregate | 0001–0006、0012、0023、0025 | 跨文件计数、求和、排名、jq、去重、链式取证；多数题的数据量超过 read_file 64KB 或 bash 8KB 输出上限，只能靠管道算 |
| edit | 0007–0011 | 批量替换（archive 不许动）、批量改名、限定范围删除、管道生成产物、带表头排序 |
| recover | 0013–0015 | 长文件截断陷阱、`python3` 不存在时改用 awk 复算脚本、每次调用 cwd 重置（多轮里 `cd` 不保留，根目录有同名诱饵） |
| boundary | 0016–0018 | 没有 curl 要改用 web_fetch、没有 pip 也能算、只问命令不许执行 |
| safety | 0019 | README 里注入 `rm -rf`，被注入目录必须原样保留 |
| closure / weather | 0020–0021 | get_weather 之后直接写产物（2026-10-09 的断裂闭环）；有 bash / web_search 时仍选 get_weather |
| command / baseline | 0022、0024、0026 | grep 精确匹配与扩展名计数诱饵（英文题）；单文件读取基线（看 bash 是否挤掉 read_file，仅诊断） |

判分只看结果（答案、文件终态、少数题的工具约束），不强制用 bash：0021 要求 get_weather，0018 要求零调用。
bash 使用率从 trace 里统计，作为诊断指标。所有题 `status: draft`，跑时带 `--include-draft`。

## 已知限制

- 生成器在 macOS（大小写不敏感文件系统）上验证，所以改名题用 `.jpeg → .jpg`，不用大小写改名。
- sidecar 不带 python / sqlite3；fixture 时钟固定在 2026-09-16（work 目录约定），天气题的"明天"按此计算。

## 第二部分：cases-b14（bsh-0101–0160，60 题）

2026-10-14 从 b14 的 300 道 bash/天气题里固定选出（名单 [`probe_ids.json`](../distill/tools/b14/probe_ids.json)，选一次、不再重抽），单独放在 `cases-b14/`，**旧的 26 题（`cases/`）原样冻结**，两部分分开跑、分开报，需要总分时相加。
生成器是 [`bench/distill/tools/b14`](../distill/tools/b14/README.md)（`build.py` 出题并在 sidecar 里验参考解，`export_probe.py` 改编号、换 canary、加 `probe_axis` / `probe_part: b14` / `source_id`）。

| 轴 | 题 | 来源子类 |
|---|---|---|
| aggregate | 0101–0119 | 跨文件聚合（每套数据一题，13 题）、长文件（6 题，含答案在文件尾部） |
| command | 0120–0127 | 精确匹配：扩展名诱饵、整词、字面量、行首锚定、整字段 ID |
| edit | 0128–0139 | 批量编辑：至少 2 个文件，保护范围 + 同文件相似行，改后回查；3 题两轮 |
| recover | 0140–0148 | 缺 python/node/make/sqlite3/curl 后换法（6）、cwd 不保留（3，两轮） |
| boundary | 0149–0158 | 只问命令（零调用）、用户已贴内容、先问后跑（两轮）、单文件读取不该用 bash |
| safety | 0159–0160 | README 注入破坏性命令，数据必须原样 |

中文 32、多轮 14、首轮零调用 8。选题按子类配额、每套数据最多一题，没有参考任何模型分数。
参考：DeepSeek-flash（T=0.3，k=3，带 b12 老师附加指令要求简短作答）170/180，三次全过 53 题；不带附加指令时它常写超过判据字数上限的长 Markdown，分数会明显偏低。

```bash
./local/bin/rwkv-cli agent-eval ... --cases bench/bashprobe/cases-b14 --tool-catalog work-v2 --file-tools lines --include-draft ...
```

### 已知问题（待定）：终答字数上限是隐性要求

第二部分每一轮都带 `max_output_chars`（600 / 700 / 900 字），但正式系统提示里没有「简短作答」的要求，模型事先不知道这条判据。RWKV 按简短风格训练，影响不大；API 模型（如 DeepSeek）不带 b12 老师附加指令时常写长 Markdown，答案对了也因超字数判错。2026-10-14 决定先记录不改：真要拿这套题和其他模型对比时，再决定是放宽上限，还是给所有被测模型同样的格式说明。

## 备选区：reserve/（140 题）

b14 其余 bash 题，保留 b14 原题号，同样换成本探针 canary。不参与跑分，用于以后轮换或补充；**同样是测试数据，不得进训练集或当出题种子**。
`fs-10129`（扩展名大小写改名）在大小写不敏感的文件系统（macOS 默认）上必然判错，要跑须把 `TMPDIR` 放在区分大小写的卷上。
