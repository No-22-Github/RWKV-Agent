# bashprobe：沙箱 bash 能力探针

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
