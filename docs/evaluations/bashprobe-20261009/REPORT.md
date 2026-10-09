# bashprobe 首轮：g1k 不会主动选 bash / get_weather（2026-10-09）

- HEAD：c680600（bash 工具 + work-v2 + bashprobe 提交），探索性单副本 k=1
- 端点：api-7b.rwkvos.com，实际加载 `rwkv7-g1k-7.2b-20260930-ctx25600`，albatross-1.3.0
- 配置：桌面 App 当前档案——`--profile g1k`，采样 g1k-agent + presence 0.5 / frequency 0.1 / decay 0.996，
  max-steps 16，`--tool-catalog work-v2`（14 个工具，bash 与 get_weather 都在 `<tools>` 里，已核对 prompt）
- 题库：`bench/bashprobe`，26 题（参考解均已在 just-bash sidecar 中验证可解）

## 结果

| 组 | 通过 | bash 调用 | get_weather 调用 | 说明 |
|---|---|---|---|---|
| App 配置（带 App state） | 1/26 | 0 | 0 | 唯一通过的是单文件读取基线 0022 |
| 同配置去掉 state | 1/26 | 1（`pip install pandas`，照抄用户原话） | 0 | 10 题直接作答不调工具 |
| 带 state，题面追加「请用 bash 命令完成」（21 题） | 1/21 | 3 | — | 唯一一次正常使用 `grep -c "level=fatal" big.log` 即答对 |

## 结论

1. **选择是瓶颈，不是命令能力。** 明说"用 bash"时 21 题仍只调 3 次；但一旦调用，命令是对的（grep -c 一次答对）。
   不调 bash 时，模型用 list_files / search_text / read_file 硬做：在 .py 文件里搜字符串 ".py" 来数行数、逐个 read_file
   十几个文件、对 64KB 截断后的内容直接作答。
2. **state 不是主因。** 去掉 state 也几乎不调 bash；state 让模型更倾向调工具（旧工具），没有让它学会新工具。
3. **get_weather 两组都是 0。** 0021 直接问"成都今天下雨吗"也去搜网页；0020 连搜 13 次网页直到步数用尽。
   与 2026-10-09 App 实测（单问天气 12/12 调 get_weather）不同，差别在工具目录：work-v2 里多了 12 个 work 工具，
   模型回到训练语料里熟悉的工具。系统提示里新增的两句选用提示没有起作用。
4. 旧问题照旧：一半以上失败停在"强制作答阶段又吐工具调用"；带 state 组 4 题输出退化成乱码；
   还会编造 `read` / `search_files` / `sort_lines` / `curl` 这类不存在的工具名。

## 下一步

靠提示词改不动选择，需要训练数据：蒸馏语料补 bash 与 get_weather 的轨迹（批量统计、批量修改、长文件计数、
python 不可用时改用 awk、专用工具优先于 web_search），与 work-v2 题库升级一起做。bashprobe 作为验收题集，
训练前后各跑一次。
