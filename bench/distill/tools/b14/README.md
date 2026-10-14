# b14 出题脚本（v1.42：bash 与 get_weather「做对」批，work-v2）

v1.42 的 300 道题：bash 200（10001–10200）、天气 100（10201–10300）。

> **2026-10-14 起 b14 是测试题，不是蒸馏数据。** `export_probe.py` 把构建结果搬出 distill 目录：`probe_ids.json` 里固定的 90 题成为 `bench/bashprobe/cases-b14`（bsh-0101–0160）和 `bench/weatherprobe/cases-b14`（wth-0101–0130），其余 210 题进两个探针的 `reserve/`。`bench/distill/v1.42/cases` 只是构建暂存区，导出后删除。下文的老师跑题、behavior.py 属于当初的蒸馏设想，已不适用。规划见 [distill-allocation-v1.42.md](../../v1.42/distill-allocation-v1.42.md)，出题报告见 [b14-authoring.md](../../v1.42/reports/b14-authoring.md)。

| 文件 | 题号 | 内容 |
| --- | --- | --- |
| `m9agg.py` | 10001–10066 | M9a 跨文件聚合、M9c 长单文件：16 个数据世界 × 4 题 + 2，答案是一个数或短名称，README 写口径和近似值诱饵 |
| `m9exact.py` | 10067–10090 | M9g 精确匹配：扩展名计数诱饵、整词 grep、`[WARN]` 字面量、行首锚定、精确 ID |
| `m9edit.py` | 10091–10130 | M9b 批量编辑：至少改 2 个文件，带必须原样保留的范围，要求改后回查；10 题两轮 |
| `m9recover.py` | 10131–10160 | M9d 缺 python/node/perl/make/sqlite3/curl/pip 后换法，M9f cwd 不保留（两轮），M9c 答案在长文件末尾 |
| `m9neg.py` | 10161–10200 | M9e 负例：只问命令（5 题第二轮要求执行）、用户已贴内容、单文件读取、README 注入 |
| `m10w.py` | 10201–10300 | M10a–M10g：明后天标签和地标、隐式需求和本地规则、照抄格式写文件、多轮换城市、查不到的地点、复合请求、概念负例 |
| `aggcore.py` | — | 聚合引擎：同一份 `AGG_SRC` 既用来选种子、算答案，也原样嵌进 verify.py |
| `common.py` | — | 批次设置、按 lint 规则自动定 level、自动补陷阱对应的 axes、fixture 哈希守卫、overlay 回读的参考解检查 |

```bash
scripts/build-justbash.sh                              # 先有 local/bin/justbash-sidecar（需要 bun）
cd bench/distill/tools/b14 && python3 build.py         # 写 300 题、在 sidecar 里跑 bash 参考解、写 specs.json
python3 build.py --no-sidecar                          # 没有 sidecar 时只写题，bash 题全部标 UNVERIFIED
python3 export_probe.py                                # 搬到两个探针的 cases-b14/ 与 reserve/，删除暂存区（逐字节可复现）
python3 dedup.py --json ../../v1.42/reports/b14-dedup.json   # 8 字符片段重叠
python3 stats.py --json ../../v1.42/reports/b14-stats.json   # 子类、中文、多轮、零调用占比
```

- 随机数固定种子，重跑逐字节一致（已核对）。只重建部分题用 `--only m9edit` 或 `--ids cfg-10091,...`；这两种情况下不改写 `specs.json`。
- just-bash sidecar 是写时复制的，命令改的是 overlay、不落盘；`casegen.check_reference` 读宿主目录看不到改动，所以这里的 `run_reference` 用 sidecar 的 `read` op 回读。
- verify.py 先校验整份 fixture 的 sha256，任何破坏（数字 +1、删首行）都会让它失败；答案仍按 fixture 重新计算。
- 解题者不得读这里的文件（同 b10、b12）。
