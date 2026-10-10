# b12 样板题构建脚本（v1.41：bash + get_weather，work-v2）

v1.41 的 20 道样板题：M9 bash 12 道（`m9a.py` 多文件统计 / 批量修改 / 长文件，`m9b.py` 工具缺失恢复 / 有 bash 但不该用 / cwd 不保留），
M10 专用工具优先 8 道（`m10.py`、`m10b.py`）。规格见 [distill-allocation-v1.41.md](../../../../../docs/distill/v1.41/distill-allocation-v1.41.md)。

```bash
scripts/build-justbash.sh                          # 先有 local/bin/justbash-sidecar
cd bench/distill/tools/v1.41/b12_build && python3 build.py   # 写题 + 在 sidecar 里跑每道 bash 题的参考解
./gate.sh                                          # 只对 9xxx 题跑 bank lint + bank verify --strict-shape
```

- 随机数带固定种子，重跑逐字节一致；数值类题会换种子直到答案字面量不出现在 fixture 里，避免破坏测试撞上无关数字。
- 放量出题照这里的写法：参考解进 `REFS`，`build.py` 跑不通就不收。
- 解题者不得读这里的文件（同 b10）。
