# bench/distill

蒸馏数据。题目、老师脚本、工具都先按**数据版本**分目录，与 [`docs/distill/`](../../docs/distill/README.md) 的版本目录一一对应。

```
cases/<版本>/<场景>/<题号>/     蒸馏题（case.json + verify.py + NOTES.md）
cases-shelved/<版本>/…         下架题
scripts/<版本>/<批次>.jsonl     老师动作脚本，corpus render --script 的输入
tools/                         跨版本通用：step.py（盲解）、collect.py、to_segments.py、classify_failures.py
tools/<版本>/                   该版本专用的构建脚本、检查脚本、老师 suffix、工作目录
batches.jsonl                  批次登记（author 以此为准）
exclude.jsonl · tag-map.json   打包排除表、标签映射（tag-map 路径写死在 Go 里，不要挪）
audit-20260926/                蒸馏审阅的统计与清洗策略
```

| 版本 | 题目 | 老师脚本 | 专用工具 |
| --- | --- | --- | --- |
| v1 | `cases/v1/`：5xxx b01–b03，6xxx b04 | base700、b01–b04、b04r | `tools/v1/w0-cases.tsv` |
| v1.3 | `cases/v1.3/`：7xxx | b05-baseline、b05–b07 | `tools/v1.3/`：v13_* 脚本、train-1-3.sh / test-1-3.sh、扫描结果 json |
| v1.4 | `cases/v1.4/`：8xxx b10 | b09-m1、b10-pilot | `tools/v1.4/`：b10_build、b10_check / b10_merge、v14_*、b09_work、b10-suffix.txt |
| v1.41 | `cases/v1.41/`：9xxx b12 | — | `tools/v1.41/`：b12_build、b12-suffix.txt |

所有命令仍以 `bench/distill/cases` 为题库根（`--cases bench/distill/cases`），加载器会递归读到各版本目录；
只要某个版本时把根换成 `bench/distill/cases/v1.4`。`bank lint` 接受 `[<版本>/]<场景>/<题号>` 两种层级。
