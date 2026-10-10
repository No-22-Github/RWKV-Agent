# b10 试跑题构建脚本

v1.4 M2 里程碑（b10 试跑）70 道题的生成脚本，每个文件对应一个题类：
m2 查不到、m3 遵守不调工具、m4 小工具清单、m5 写任务闭环、m6 表格/日志工具化、m7 信源优先级、m8 计算器。

- 随机数全部带固定种子，重跑会逐字节生成相同的 `bench/distill/v1.4/cases/<scenario>/<id>`。
- 题目本身才是资产；这些脚本留作复现与 M3 放量时的出题参考（每题的 fixture、判据、verify.py、NOTES 写法）。
- 解题者不得读这里的文件（见 [b10-solver-brief.md](../../v1.4/b10-solver-brief.md)）。

```bash
cd bench/distill/tools/b10 && for f in m*.py; do python3 $f; done
```
