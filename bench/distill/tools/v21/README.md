# v2.1 流水线脚本（MiSS 第二轮，带思考）

计划见 [distill-allocation-v2.1.md](../../v2.1/distill-allocation-v2.1.md)，出题规格见 [authoring-v2.1.md](../../v2.1/authoring-v2.1.md)，本轮产出报告见 [v2.1-pack-20261017.md](../../v2.1/reports/v2.1-pack-20261017.md)。由 `../v20/` 复制改成，和 v2.0 的区别：

- 老师和渲染都走 `--harness app`：App 的系统提示词、工具顺序、暂存文件说明，重复/同工具拦截开（2/3/3）。
- 去污染多查新考卷 `bench/exam/cases`。
- `render.sh` 选路径时加 `--keep-recovery`：工具报错/被拒的那步保留为不训练的上下文，强制作答阶段的终答照常训练。
- `build_refusal.py` + `refusal.sh`：构造"工具被拒后作答"——重复最后一个只读调用 1–2 次触发 App 拦截，千问在无工具下重答，只训练这一步。
- `scan_forbidden.py`：找"工具已关闭后还训练工具调用"的行，`finalize.py` 整轮剔除。
- `finalize.py` 可同时吃多个批次和 `--rows` 文件，概念题按题封顶（`--concept-cap`），`--max-tokens` 定上下文。

```bash
go build -o local/bin/rwkv-cli-v21 ./cmd/rwkv-cli
go build -tags chatcompletions -o local/bin/rwkv-cli-chat-v21 ./cmd/rwkv-cli
go build -o local/bin/rwkv-lab-v21 ./cmd/rwkv-lab
scripts/build-justbash.sh

export TEACHER_ENV_FILE=~/.commandcode_key_v21.sh TEACHER_MODEL=Qwen/Qwen3.7-Flash PARALLEL=24
bench/distill/tools/v21/run_teacher.sh main '*' 1        # 老师一遍（24 路并发零报错）
bench/distill/tools/v21/retry_failed.sh main             # 失败题重跑进 teacher-k1（k2 见报告，手动跑）
bench/distill/tools/v21/render.sh main                   # 路径 → 过滤 → 按步渲染

# v2.0 旧路径换 App harness 重渲染（逐字一致，只换提示词）
local/bin/rwkv-lab-v21 corpus render --cases local/runs/distill/v20/qwen/cases --script local/runs/distill/v20/qwen/script.jsonl \
  --out local/runs/distill/v21/v20app-qwen --source distill-v20-qwen --profile g1k-think --tool-catalog work-v2 \
  --cli local/bin/rwkv-cli-v21 -- --harness app

bench/distill/tools/v21/refusal.sh v20/qwen ref-v20 110  # 被拒后作答
bench/distill/tools/v21/refusal.sh v21/main ref-v21 75

python3 bench/distill/tools/v21/finalize.py --batch main --rows local/runs/distill/v21/v20app-qwen/rows.jsonl ... \
  --concept-cap 80 [--max-tokens 16320] --out local/runs/distill/v21/final-<日期>
```

产物都在 `local/runs/distill/v21/`，不入库。
