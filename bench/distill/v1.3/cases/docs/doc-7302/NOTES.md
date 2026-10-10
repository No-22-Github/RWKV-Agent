## Traps
- TR-DECOY: the delivery note lists four item rows but only 金骏眉 (备注
  湖畔店正常入库) is receivable for this store; 正山小种 and 土陶茶罐 are both
  marked 湖畔店勿收 (rerouted to the Yan'an shop) and the empty crates are
  退回, taken back by the driver. Registering all four rows is the trap.

## Reference solution
1. Read README.md: the logbook takes one line per receival with the fields
   日期 到货 品名 数量 承运 单号 签收人, and only rows the note marks
   湖畔店正常入库 are entered.
2. Read notes/delivery-DH-2210.txt.
3. Read the tail of logbook/receiving-2026-09.txt to match the line style.
4. Append the 金骏眉 line for DH-2210.

## Why the answer is unique
The note itself reroutes or withdraws the other three rows (改送延安店 /
延安店加单 / 退回), and the house rule only books rows marked
湖畔店正常入库, so exactly one line can be appended: 2026-09-28 到货 金骏眉
8饼 顺达冷链 DH-2210 签收人 阿芷. The old entries stay in place, the delivery
note is unchanged, and the appended line cannot carry a quantity or product
that the note does not list for this store.
