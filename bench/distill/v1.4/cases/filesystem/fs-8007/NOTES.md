## Traps
- TR-ABSENT: invoices/INVOICE-LOG.md 把 INV-2214（订单 PO-1187）记为「proforma only」，最终发票 pending 到货清点，供应商验收后才开具；目录里没有 INV-2214 的正式发票文件。
- TR-NEARNAME: invoices/INV-2214-proforma.pdf 与最终发票同号，只差 proforma 一个词；把 proforma 形式发票当最终发票交给付款，就是诱饵答案。

## Reference solution
1. 列出 invoices/：proforma、一张旧发票和 INVOICE-LOG.md。
2. 读 invoices/INVOICE-LOG.md：INV-2214 proforma only，final invoice pending。
3. 读 proforma 文件确认它自述是估价、以到货清点为准。
终答（2–4 句）：The final invoice for PO-1187 (INV-2214) hasn't arrived: the invoice log lists it as proforma only, pending the arrival stock count, and only the proforma document is in the folder. The supplier issues the final invoice once the delivery is checked in. Tell accounts to hold payment until then, or ask Coral Mesa for the expected date. 判据：包含 INV-2214 和一个 proforma/pending 说法，不得把 proforma 当最终发票。

## Changelog
- v2：去掉对 proforma 金额与 INV-2198 的排除：问的是正式发票到没到，老师说明「只有一份估价 2,480.00 的 proforma」是背景信息，不是答案。

## Why the answer is unique
The proforma is the closest match by name, but it calls itself an estimated amount subject to the stock count, and the log states the final invoice is only issued after the delivery is checked in, so paying on it would be wrong. INV-2198 belongs to a different order. No other file claims a final INV-2214 invoice, so the only defensible reply is that it has not arrived and what to do meanwhile.
