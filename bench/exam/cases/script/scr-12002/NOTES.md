## Traps
修复冷链装车摘要的缺值报错，并按复点、扫描、计划三层来源取箱数。
- TR-PRECEDENCE：box_sources.json 定义复点 > 扫描 > 计划。D1 首行复点 3 必须覆盖计划 10；D4 的复点 0 必须覆盖扫描 6。
- TR-MISSING：空串、NA、-、null 四种未填表示散落在三列；直接 int 会报错，把未填都当 0 并立即停止会漏掉较低来源的有效值。

## Reference solution
1. 批量读取 traceback、仓库说明、来源配置、CSV 和脚本。
2. 修复逐行取值：按 priority 检查，跳过 unset，第一个有效数即该行箱数；全未填记 0，并保留 dock。
3. 运行脚本核对输出，共 3 次调用。

## Why the answer is unique
七行托盘分别取 3、4、5、2、7、0、0 箱。按 dock 合计 D1=10、D2=9、D3=2、D4=0。配置明确来源先后及缺值集合，README 明确保留所有 dock、排序和 CSV 字符格式。唯一 stdout 为：
```
dock,boxes
D1,10
D2,9
D3,2
D4,0
```

## Scoring boundary
两份不同正确实现都应过，允许末尾换行差异；保留零箱 dock 是任务目标。原脚本、仅捕获异常继续、先用计划值、把字符串 0 当未填都应失败。仅凭此固定输入不能排除硬编码完整输出，且不穷举未来新增缺值类型；记录这一判分边界。

EXAM-CANARY-a8f0c936
