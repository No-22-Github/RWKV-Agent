# Harness 偏好重建三部曲 (2026-08-31)

> 本目录包含 2026-08-31 在 `rwkv7-g1i-7.2b-20260805-ctx16384` 上完成的高并发探针与 Harness 偏好重建完整记录。
> 本系列报告是仓库根目录 [`PREFERENCES.md`](../../../PREFERENCES.md) 的唯一实验与数据事实源。

---

## 三部曲报告目录

| 轮次 | 报告文件 | 核心内容与重大发现 |
| --- | --- | --- |
| **第一轮** | [harness-preference-rebuild-report-20260831.md](harness-preference-rebuild-report-20260831.md) | **偏好测绘**：P1–P5 五大维度 400 格探针，确立长上下文降解点（10k–20k）、子 Agent 强近因效应（−55~−60 pp）、回填包裹无差异性；直接产出 16 条 Harness 规则与 `PREFERENCES.md`。 |
| **第二轮** | [harness-round2-report-20260831.md](harness-round2-report-20260831.md) | **量尺重建**：造题校准剔除天花板/地板题目；首次精确定位**单文件长提取在 4.5k–5k token 之间的工作流悬崖**（先崩的是读回长文件后收尾作答的纪律，而非输出格式）。 |
| **第三轮** | [harness-round3-report-20260831.md](harness-round3-report-20260831.md) | **真实计数与收敛**：启用真词表进程内计数（废除偏差 16%~40% 的估算器）；将提取悬崖精确重标为 4673–5021 tokens；Query-Aware 压缩修复与中文检索退化检测落地。 |

---

## 关联阅读

- **规则落地总纲**：[`PREFERENCES.md`](../../../PREFERENCES.md)
- **长篇复盘报告**：[`docs/reports/harness-layer-optimization-report.html`](../../reports/harness-layer-optimization-report.html)
- **文档总索引**：[`docs/README.md`](../../README.md)
