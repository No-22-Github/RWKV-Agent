# 客户端合批吞吐对照（PLAN）

日期：2026-10-15。状态：已实测，结果见 `REPORT.md`（执行时的偏离也记在那里）。

## 目的

2026-10-15 起 agent-eval 默认 `--remote-batch-wait 20ms --remote-batch-max 32`（见 `benchmark-protocol.md` §5）。
本对照确认两件事：

1. 合批后每分钟完成的模型调用数明显高于不合批（预期：不合批时被 bsz=1 显存带宽卡在约 125 次前向/秒/卡，
   实测约 50 次调用/分钟/节点）。
2. 单次调用耗时没有因为合批而变差到不可接受（以 EOS 结束的调用要等同批最长的一条，见协议 §5 "仍然存在的限制"）。

## 固定条件

| 项 | 取值 |
|---|---|
| 节点 | 同一台推理节点、同一个 rwkv_lightning 进程，两组之间不重启、不换模型；跑前跑后各记一次 `/v1/models` 与 `/v1/server/status` |
| 模型 / adapter | 同一个 7.2B 模型 + 同一个 MiSS adapter（`--adapter-id`），两组完全相同 |
| 题目 | workbank 20 题：按 case 路径排序后每隔 7 题取 1 题，取前 20 题（覆盖各 scenario，见下方命令） |
| 并发 | `--case-parallelism 64`（20 题时实际同时在跑的最多 20 题；要看满 64 路，就把同样两组改跑全量 148 题，作为可选附加组） |
| 采样 / 预算 | `--sampling greedy`，`--max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-timeout 30m` |
| 节点独占 | 对照期间节点上不跑其他任务（共享端点上的别人的流量会直接污染吞吐数字） |

两组只有一个变量：

| 组 | 合批参数 |
|---|---|
| A（关） | `--remote-batch-wait 0s` |
| B（默认） | 不传（= `20ms` / `32`） |

两组顺序：A → B → A → B（各跑 2 次，交替，排除节点预热和时段影响）。

## 命令

```bash
CASES=$(find bench/workbank/cases -name case.json | sort | awk 'NR % 7 == 1' | head -20 \
  | xargs -n1 dirname | xargs -n1 basename | sed 's/^/--case /' | tr '\n' ' ')
NODE=http://100.64.0.1:8018/v1          # 换成要测的节点
OUT=local/runs/batch-throughput-$(date +%Y%m%d)

run() {  # $1 = 组名, 其余 = 合批参数
  name=$1; shift
  ./local/bin/rwkv-cli agent-eval \
    --completion rwkv-lightning-cuda --model <模型id> --api-url "$NODE" --adapter-id <adapter> \
    --profile g1k --strict-spec \
    --cases bench/workbank/cases --tool-catalog work-v1 --file-tools lines --include-draft $CASES \
    --max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --case-parallelism 64 --case-timeout 30m \
    --sampling greedy "$@" \
    --output "$OUT/$name"
}
run a1-nobatch --remote-batch-wait 0s
run b1-batch
run a2-nobatch --remote-batch-wait 0s
run b2-batch
```

每个 run 跑完照常过闸门（A 组会显示 `got 0: unbatched run…`，属预期）：

```bash
for d in "$OUT"/*; do ./local/bin/rwkv-lab run check "$d" --arm greedy --rwkv --cases 20; done
```

## 指标与算法

从每个 run 的 `summary.json` 计算（`cases[].turns[].cost`，字段定义见 `internal/agent/eval/cost.go`）：

- **每分钟完成调用数** = 全部题的 `steps` 之和 ÷（最晚 `ended_at_ms` − 最早 `started_at_ms`）× 60000。
- **单次调用耗时** = 每题 `model_ms / steps`，报中位数与 p90；同时报 `wait_ms / steps`（首 token 等待：合批窗口 + 排队 + prefill）。
- 辅助：整轮墙钟、`hit_timeout` 题数、`length_steps` 合计（复读到上限的调用数，它决定 EOS 调用要等多久）。

```bash
python3 - "$OUT"/* <<'PY'
import json, statistics, sys
for run in sys.argv[1:]:
    cases = json.load(open(f"{run}/summary.json"))["cases"]
    costs = [c["cost"] for c in cases if c.get("cost")]
    steps = sum(c["steps"] for c in costs)
    span = max(c["ended_at_ms"] for c in costs) - min(c["started_at_ms"] for c in costs)
    per_call = sorted(c["model_ms"] / c["steps"] for c in costs if c["steps"])
    wait = sorted(c.get("wait_ms", 0) / c["steps"] for c in costs if c["steps"])
    p90 = lambda xs: xs[int(0.9 * (len(xs) - 1))]
    print(f"{run}: calls/min {steps / span * 60000:.1f}  wall {span / 60000:.1f} min  "
          f"call ms p50 {statistics.median(per_call):.0f} p90 {p90(per_call):.0f}  "
          f"wait ms p50 {statistics.median(wait):.0f}  "
          f"timeouts {sum(bool(c.get('hit_timeout')) for c in costs)}  "
          f"length steps {sum(c.get('length_steps', 0) for c in costs)}")
PY
```

## 判定（跑前写定）

- B 组每分钟调用数 ≥ A 组的 2 倍（两次的均值相比）→ 合批默认成立。
- B 组单次调用 p90 不高于 A 组 p90 → 无尾部回退；若更高，看 `length_steps`：是 EOS 调用被复读拖住，
  就把 `--remote-batch-max` 降到 16 再补一组 B'，记录取舍。
- 两组通过题数差异只作旁证，不作结论：批维度不同 fp16 数值可能有微小差异，20 题样本也太小。
- 结果写进本目录 `REPORT.md`，并在 `benchmark-protocol.md` §5 引用实测数字。
