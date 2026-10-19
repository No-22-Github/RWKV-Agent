# b22d（v2.2 计算器边界，题号 34301–34370）

    cd bench/distill/tools/b22d && python3 build.py

- D1 心算即可 30 题 nt-34301..34330（`d1a/d1b/d1c.py`）：每轮 `tools: []`，一半题 `must_offer: [calculator]`。
- D2 计算器报错后恢复 20 题 hyb-34331..34350（`d2a/d2b.py`）：`must_offer: [calculator, bash]`，`max_calls: {calculator: 2}`，只判结果。
- D0 对照：该用计算器 20 题 hyb-34351..34370（`d0a/d0b.py`）：只判结果（容差 0.006 起），不卡工具。
- `common.py` 的 `mk()`：compute() 是答案唯一来源，内嵌进 verify.py 重算；GIVEN 断言题面含所有输入数字；D2 的参考 awk 命令每次构建都在 just-bash 沙箱里真跑并核对输出。
- 固定种子（无随机），重跑逐字节一致。
