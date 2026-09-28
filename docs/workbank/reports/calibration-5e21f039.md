# workbank 难度校准 — bank_version sha256:5e21f0399358a453cd817dc07c32481894a2ac2e09066ceee571efa8804266b6

> 由 `tools/calibrate.py` 生成：**声明难度 vs 实测通过率**。
> 判定口径（handoff §M6）：标 L1 但所有配置 < 20%，或标 L0 但通过率 < 50%。

## 本轮新增 112 题的偏离

| 指标 | 值 |
|---|---|
| 新增题 | 112 |
| 被标记的题 | 20 |
| `harder_than_declined` | 18 |
| `l0_too_hard` | 2 |

> **这份表是暂定的。** B2–B5 的 27B（REF）run 因端点 502 未跑，
> 这些题的「所有配置」目前只有 9B 一栏。handoff §6.3 明确：
> **9B 失分若集中在 `capability` 层，正是题目在正常工作（27B 会、9B 不会）**，
> 而不是难度标错。所以上表里绝大多数 `harder_than_declined` 在 REF 补测后应当消失。
> 端点恢复、补充 REF 后请重跑本脚本覆盖本文件。

## 各行明细（新增题）

| case | level | per-config pass | overall | flag |
| cfg-0010 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| code-0006 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| fs-0006 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| fs-0008 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| hyb-0008 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| log-0016 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| nt-0012 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| scr-0006 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| scr-0016 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| scr-0017 | L0 | qwen9b-expansion 0% | 0% (0/3) | l0_too_hard |
| scr-0018 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| scr-0020 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| tab-0019 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| tab-0020 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| web-0006 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| web-0007 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| web-0008 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| web-0013 | L0 | qwen9b-expansion 0% | 0% (0/3) | l0_too_hard |
| web-0015 | L1 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| web-0016 | L2 | qwen9b-expansion 0% | 0% (0/3) | harder_than_declined |
| cfg-0005 | L0 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| cfg-0006 | L1 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| cfg-0007 | L1 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| cfg-0008 | L2 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| cfg-0009 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| cfg-0011 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| cfg-0012 | L2 | qwen9b-expansion 100% | 100% (3/3) | - |
| cfg-0013 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| cfg-0014 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| cfg-0015 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| cfg-0016 | L2 | qwen9b-expansion 100% | 100% (3/3) | - |
| code-0005 | L0 | qwen9b-expansion 67% | 67% (2/3) | - |
| code-0007 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| code-0008 | L2 | qwen9b-expansion 33% | 33% (1/3) | - |
| code-0009 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| code-0010 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| code-0011 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| code-0012 | L2 | qwen9b-expansion 100% | 100% (3/3) | - |
| doc-0005 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| doc-0006 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| doc-0007 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| doc-0008 | L2 | qwen9b-expansion 100% | 100% (3/3) | - |
| doc-0009 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| doc-0010 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| doc-0011 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| doc-0012 | L2 | qwen9b-expansion 100% | 100% (3/3) | - |
| fs-0005 | L0 | qwen9b-expansion 67% | 67% (2/3) | - |
| fs-0007 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| fs-0009 | L0 | qwen9b-expansion 67% | 67% (2/3) | - |
| fs-0010 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| fs-0011 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| fs-0012 | L2 | qwen9b-expansion 100% | 100% (3/3) | - |
| hyb-0005 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| hyb-0006 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| hyb-0007 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| hyb-0009 | L0 | qwen9b-expansion 67% | 67% (2/3) | - |
| hyb-0010 | L1 | qwen9b-expansion 33% | 33% (1/3) | - |
| hyb-0011 | L1 | qwen9b-expansion 33% | 33% (1/3) | - |
| hyb-0012 | L2 | qwen9b-expansion 33% | 33% (1/3) | - |
| log-0005 | L0 | qwen27b-expansion 100%, qwen9b-expansion 67% | 83% (5/6) | - |
| log-0006 | L1 | qwen27b-expansion 67%, qwen9b-expansion 0% | 33% (2/6) | - |
| log-0007 | L1 | qwen27b-expansion 100%, qwen9b-expansion 0% | 50% (3/6) | - |
| log-0008 | L2 | qwen27b-expansion 100%, qwen9b-expansion 0% | 50% (3/6) | - |
| log-0009 | L0 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| log-0010 | L1 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| log-0011 | L1 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| log-0012 | L2 | qwen27b-expansion 100%, qwen9b-expansion 33% | 67% (4/6) | - |
| log-0013 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| log-0014 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| log-0015 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| log-0017 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| log-0018 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| log-0019 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| log-0020 | L2 | qwen9b-expansion 67% | 67% (2/3) | - |
| nt-0005 | L0 | qwen27b-expansion 100%, qwen9b-expansion 67% | 83% (5/6) | - |
| nt-0006 | L1 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| nt-0007 | L1 | qwen27b-expansion 100%, qwen9b-expansion 67% | 83% (5/6) | - |
| nt-0008 | L2 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| nt-0009 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| nt-0010 | L1 | qwen9b-expansion 33% | 33% (1/3) | - |
| nt-0011 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| scr-0005 | L0 | qwen9b-expansion 67% | 67% (2/3) | - |
| scr-0007 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| scr-0008 | L2 | qwen9b-expansion 67% | 67% (2/3) | - |
| scr-0009 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| scr-0010 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| scr-0011 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| scr-0012 | L2 | qwen9b-expansion 100% | 100% (3/3) | - |
| scr-0013 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| scr-0014 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| scr-0015 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| scr-0019 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| tab-0005 | L0 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| tab-0006 | L1 | qwen27b-expansion 67%, qwen9b-expansion 100% | 83% (5/6) | - |
| tab-0007 | L1 | qwen27b-expansion 100%, qwen9b-expansion 100% | 100% (6/6) | - |
| tab-0008 | L2 | qwen27b-expansion 100%, qwen9b-expansion 33% | 67% (4/6) | - |
| tab-0009 | L0 | qwen27b-expansion 67%, qwen9b-expansion 67% | 67% (4/6) | - |
| tab-0010 | L1 | qwen27b-expansion 67%, qwen9b-expansion 33% | 50% (3/6) | - |
| tab-0011 | L1 | qwen27b-expansion 100%, qwen9b-expansion 67% | 83% (5/6) | - |
| tab-0012 | L2 | qwen27b-expansion 100%, qwen9b-expansion 33% | 67% (4/6) | - |
| tab-0013 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| tab-0014 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| tab-0015 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| tab-0016 | L2 | qwen9b-expansion 100% | 100% (3/3) | - |
| tab-0017 | L0 | qwen9b-expansion 100% | 100% (3/3) | - |
| tab-0018 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| web-0005 | L0 | qwen9b-expansion 67% | 67% (2/3) | - |
| web-0009 | L0 | qwen9b-expansion 67% | 67% (2/3) | - |
| web-0010 | L1 | qwen9b-expansion 67% | 67% (2/3) | - |
| web-0011 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |
| web-0012 | L2 | qwen9b-expansion 33% | 33% (1/3) | - |
| web-0014 | L1 | qwen9b-expansion 100% | 100% (3/3) | - |

## 已有 40 题（回归对照，未动）

| case | level | per-config pass | overall | flag |
| nt-0001 | L0 | closeout-v0-deepseek 0%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 0%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 0%, v2-g1k 0% | 42% (20/48) | l0_too_hard |
| web-0001 | L0 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 40%, v2-deepseek 100%, v2-g1k 0% | 48% (23/48) | l0_too_hard |
| cfg-0001 | L0 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 75%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 93%, v2-deepseek 100%, v2-g1k 0% | 65% (31/48) | - |
| cfg-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 50%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 27%, v2-deepseek 100%, v2-g1k 0% | 42% (20/48) | - |
| cfg-0003 | L1 | closeout-v0-deepseek 0%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 0%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 0%, qwen27b-expansion 33%, qwen9b-baseline40 0%, qwen9b-expansion 0%, v2-deepseek 0%, v2-g1k 0% | 2% (1/48) | - |
| cfg-0004 | L2 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 75%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 93%, v2-deepseek 25%, v2-g1k 0% | 50% (24/48) | - |
| code-0001 | L0 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 100%, v2-g1k 0% | 69% (33/48) | - |
| code-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 25%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 0%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 0%, v2-deepseek 25%, v2-g1k 0% | 23% (11/48) | - |
| code-0003 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 0%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 80%, v2-deepseek 100%, v2-g1k 0% | 60% (29/48) | - |
| code-0004 | L2 | closeout-v0-deepseek 0%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 0%, qwen27b-expansion 0%, qwen9b-baseline40 0%, qwen9b-expansion 0%, v2-deepseek 0%, v2-g1k 0% | 8% (4/48) | - |
| doc-0001 | L0 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 100%, v2-g1k 0% | 69% (33/48) | - |
| doc-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 50%, deepseek-flash-nexttoken 75%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 67%, v2-deepseek 75%, v2-g1k 0% | 48% (23/48) | - |
| doc-0003 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 33%, qwen9b-baseline40 100%, qwen9b-expansion 47%, v2-deepseek 100%, v2-g1k 0% | 48% (23/48) | - |
| doc-0004 | L2 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 40%, v2-deepseek 75%, v2-g1k 0% | 38% (18/48) | - |
| fs-0001 | L0 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 73%, v2-deepseek 75%, v2-g1k 0% | 58% (28/48) | - |
| fs-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 100%, v2-g1k 0% | 69% (33/48) | - |
| fs-0003 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 53%, v2-deepseek 100%, v2-g1k 0% | 54% (26/48) | - |
| fs-0004 | L2 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 100%, v2-g1k 0% | 69% (33/48) | - |
| hyb-0001 | L0 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 100%, v2-g1k 0% | 69% (33/48) | - |
| hyb-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 50%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 67%, qwen9b-baseline40 100%, qwen9b-expansion 80%, v2-deepseek 0%, v2-g1k 0% | 40% (19/48) | - |
| hyb-0003 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 25%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 93%, v2-deepseek 100%, v2-g1k 0% | 60% (29/48) | - |
| hyb-0004 | L2 | closeout-v0-deepseek 0%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 0%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 67%, qwen9b-baseline40 0%, qwen9b-expansion 40%, v2-deepseek 0%, v2-g1k 0% | 19% (9/48) | - |
| log-0001 | L0 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 100%, v2-g1k 0% | 69% (33/48) | - |
| log-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 100%, v2-g1k 0% | 69% (33/48) | - |
| log-0003 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 73%, v2-deepseek 100%, v2-g1k 0% | 58% (28/48) | - |
| log-0004 | L2 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 33%, v2-deepseek 100%, v2-g1k 0% | 38% (18/48) | - |
| nt-0002 | L1 | closeout-v0-deepseek 0%, closeout-v0-g1k 100%, closeout-v0-g1k-par8 100%, closeout-v1-g1k 100%, closeout-v1-g1k-par8 100%, closeout-v2-g1k 100%, closeout-v3-g1k 100%, deepseek 0%, deepseek-flash-nexttoken 25%, g1k 100%, g1k-steps10 100%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 93%, v2-deepseek 0%, v2-g1k 100% | 73% (35/48) | - |
| nt-0003 | L1 | closeout-v0-deepseek 0%, closeout-v0-g1k 100%, closeout-v0-g1k-par8 100%, closeout-v1-g1k 100%, closeout-v1-g1k-par8 100%, closeout-v2-g1k 100%, closeout-v3-g1k 100%, deepseek 0%, deepseek-flash-nexttoken 0%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 0%, qwen27b-expansion 67%, qwen9b-baseline40 100%, qwen9b-expansion 93%, v2-deepseek 0%, v2-g1k 0% | 48% (23/48) | - |
| nt-0004 | L2 | closeout-v0-deepseek 0%, closeout-v0-g1k 100%, closeout-v0-g1k-par8 100%, closeout-v1-g1k 100%, closeout-v1-g1k-par8 100%, closeout-v2-g1k 100%, closeout-v3-g1k 100%, deepseek 0%, deepseek-flash-nexttoken 75%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 0%, v2-g1k 0% | 60% (29/48) | - |
| scr-0001 | L0 | closeout-v0-deepseek 0%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 93%, v2-deepseek 100%, v2-g1k 0% | 56% (27/48) | - |
| scr-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 20%, v2-deepseek 100%, v2-g1k 0% | 33% (16/48) | - |
| scr-0003 | L1 | closeout-v0-deepseek 0%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 50%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 0%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 67%, v2-deepseek 25%, v2-g1k 0% | 33% (16/48) | - |
| scr-0004 | L2 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 25%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 0%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 53%, v2-deepseek 0%, v2-g1k 0% | 29% (14/48) | - |
| tab-0001 | L0 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 75%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 25%, v2-g1k 0% | 60% (29/48) | - |
| tab-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 75%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 0%, v2-g1k 0% | 58% (28/48) | - |
| tab-0003 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 50%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 20%, v2-deepseek 100%, v2-g1k 0% | 38% (18/48) | - |
| tab-0004 | L2 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 0%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 100%, v2-deepseek 100%, v2-g1k 0% | 60% (29/48) | - |
| web-0002 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 75%, deepseek-flash-nexttoken 75%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 0%, qwen9b-expansion 7%, v2-deepseek 50%, v2-g1k 0% | 29% (14/48) | - |
| web-0003 | L1 | closeout-v0-deepseek 100%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 50%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 100%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 67%, v2-deepseek 75%, v2-g1k 0% | 52% (25/48) | - |
| web-0004 | L2 | closeout-v0-deepseek 0%, closeout-v0-g1k 0%, closeout-v0-g1k-par8 0%, closeout-v1-g1k 0%, closeout-v1-g1k-par8 0%, closeout-v2-g1k 0%, closeout-v3-g1k 0%, deepseek 100%, deepseek-flash-nexttoken 100%, g1k 0%, g1k-steps10 0%, qwen27b-baseline40 0%, qwen27b-expansion 100%, qwen9b-baseline40 100%, qwen9b-expansion 47%, v2-deepseek 100%, v2-g1k 0% | 48% (23/48) | - |

## 本轮不据此改题

handoff §M6 明确：**校准偏离表送主控，本轮不据此改题**——改标或返修都会动
`bank_version`，而扩量批次刚入账，此时改动会让 152 题的第一份横测表当场作废。
