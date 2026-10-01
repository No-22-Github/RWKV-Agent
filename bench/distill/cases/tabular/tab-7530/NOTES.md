## Traps
- TR-MULTISRC: 只看入库流水会得到 687 件。README 写明净入库 = 当月入库件数减去当月出库件数，出库流水是另一半。

## Reference solution
1. 读 README.md：净入库按当月入库件数减当月出库件数计算。
2. data_query: {"path":"data/goods_in.csv","filter":{"月份":"2026-07"},"operation":"sum","field":"件数"} -> 687。
3. data_query: {"path":"data/goods_out.csv","filter":{"月份":"2026-07"},"operation":"sum","field":"件数"} -> 349。
4. 相减：687 - 349 = 338；终答只报数字 338。

## Why the answer is unique
decoy 687 只数了入库件数，但题面问净入库，README 把口径定为入库减出库，出库件数必须从入库合计里扣掉。6 月与 8 月的行被月份条件排除。答案只有 338。
