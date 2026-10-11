# v1.41 联合配额复算

`plan.py`是只读规划工具，复用修正后的`v14_composition.py`统计与batch-scoped剔除规则；默认来源是v1.4加b13。它不会调用老师、修改题目或训练数据，也不将预测当作入库结果。

```bash
python3 bench/distill/tools/v141/plan.py --json local/runs/distill/v141/allocation-current.json
# 已完成新批时可追加：--extra-rows local/runs/distill/v141/<batch>/corpus/rows.jsonl
```

输出包括实际基线、来源SHA256、不可相加的独立下限，以及旧路径替换/b12/查询/零调用四组条件预算。比例使用原始整数分子分母，不使用显示值反推。预算采用调用上限与查询下限；必须通过真实老师、选路、重放、质量剔除确认。默认预算对应[现行规格](../../v1.41/distill-allocation-v1.41.md)；新增来源、来源移除或路径行为变更后需重算并调整预算。

当前版本依赖工作区已修正的`v14_composition.py`（base700题面与首轮分母修正）；不修改或替代该统计实现。发布包的污染来源移除、family隔离、suffix、pack和行为验收属于制作任务，本脚本不执行这些任务。
