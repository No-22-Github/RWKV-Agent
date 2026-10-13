# v1.41 state 跑分（train-1-41）— 计划

日期：2026-10-13。训练脚本 [train-1-41.sh](../../../bench/distill/tools/train-1-41.sh)，测试脚本 [test-1-41.sh](../../../bench/distill/tools/test-1-41.sh)。

## 要回答的问题

1. v1.41（v1.4 + b12 bash/get_weather）比 v1.3 选点 `v13b-s688` 好吗：V1 题库不退，V2 bashprobe 提分。
2. 18 个 checkpoint 选哪个，lr2e-2 和 lr1e-2 哪个好。

## 被测与对照

| arm | 说明 |
|---|---|
| none | 基模，无 state |
| v13b-s688 | v1.3 推荐点（端点上已有） |
| v141a-s{153…1224}, v141a-fin | lr 0.02→0.00333，GPU1 |
| v141b-s{153…1224}, v141b-fin | lr 0.01→0.00167，GPU3 |

训练：segments-1-41.jsonl（sha `feb2fd6b…`，train 3662），ctx 8192、bs 8、3 epoch 共 1374 步、每 153 步存点。
checkpoint 的 sha256 见 `local/states/v141/SHA256SUMS`（端点文件名即 state_id）。

## 题库

- **V1（work-v1）**：workbank 148 题（主指标按干净 112 题算，排除 `seeded-base700.txt`）+ bfcl-product 60 题（中文 40 / irrelevance 20）。
- **V2（work-v2 = work-v1 + bash + get_weather）**：bench/bashprobe 26 题。与 v1.41 训练题的 8 字符片段重叠最高 0.28（bsh-0024，只是通用措辞），视为不泄漏。

## 设置

模型 `rwkv7-g1k-7.2b-20260930-ctx25600`，推理直连网关 `http://100.64.0.4:8018/v1`（state 上传走 Cloudflare：直连链路上行超过约 1 MB 就卡死）。
`--profile g1k`、`--sampling g1k-agent`，16 步、4096/2048 token、单题 30 分钟、合并窗口 0。V1 由 `bench sweep` 跑，总并发 64；V2 每次跑一个 arm，并发 26。
二进制统一用 688cbfa1 版的 cli/lab/sidecar（b12 用它渲染；main 上的 51eef6ff 改了 bash 描述）。`local/bin/rwkv-cli` 已临时换成 688cbfa1 版，原文件备份为 `rwkv-cli.pre-v141`。
工作区有别人未提交的 App/batch.go 改动，二进制不受影响，这次的 experiment.json 中 diff sha 不代表二进制版本。

## 流程与判定

1. 筛选：全部 20 个 arm 各跑一次（k0），V1 与 V2 都跑。
2. 副本：workbank 干净 112 前两名的 v1.41 点，加上 none 和 v13b-s688，补跑 k1、k2。
3. 判定：比较时把三次的通过数按题合并，做双侧符号检验。差距小于同配置极差的写"无法区分"。
   选点规则：workbank 不显著差于最佳点的前提下，挑 bfcl-product 与 bashprobe 损失最小的点（同 v1.3 规则），再加上 bashprobe 不低于 v13b-s688。
4. 每个 run 都要过 `run check`，invalid 的处理按规程执行。
