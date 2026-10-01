## Traps
- TR-DECOY: data/shipments.tsv 里「花市直供」与目标渠道「花市代发」相邻。把直供的行（或两渠道一起）求和会得到 6395.47。8 月的行是月份干扰项。

## Reference solution
1. data_query: {"path":"data/shipments.tsv","filter":{"发货月份":"2026-09","渠道":"花市代发"},"operation":"sum","field":"货款"} -> 8865.94。
2. 终答只报数字 8865.94。

## Why the answer is unique
decoy 6395.47 是「花市直供」的合计，但题面点名「花市代发」，README 写明两条渠道分开结算，每行只属于一条渠道，不存在混算的读法。8 月的行被月份条件排除。答案只有 8865.94。
