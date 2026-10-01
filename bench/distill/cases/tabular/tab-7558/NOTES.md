## Traps
- TR-HEADER: 台账末行是系统生成的当月合计（月份为「全部」，README 写明不参与统计），把合计行当成一张销货单再与 9 月回款相减会得 19095.10。
- TR-DECOY: receipts 文件里混着一笔 8 月的回款（README 写明按记账月份归属），从台账合计里把全部回款都扣掉会得 1033.84；正确答案是只扣 9 月回款，差 1383.95。

## Reference solution
1. 查询一：{"path":"data/ledger_2026-09.csv","filter":{"月份":"2026-09"},"operation":"sum","field":"金额"}，得 17711.15（月份过滤天然排除末行合计）。
2. 查询二：{"path":"data/receipts_2026-09.csv","filter":{"记账月份":"2026-09"},"operation":"sum","field":"金额"}，得 16327.20。
3. 相减得 1383.95，终答只报数字。

## Why the answer is unique
decoy 19095.10 把非销货的合计行当成了明细；decoy 1033.84 把 8 月回款也扣了，与 README 写明的归属矛盾。两份文件各只有一种按月过滤的读法，答案唯一为 1383.95。
