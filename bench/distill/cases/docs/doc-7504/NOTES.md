## Traps
- TR-DECOY: faq/tickets-0912.csv 的 TK-4480 是换机请求，看起来最像要升级的工单，但 triage 给它的是 MACRO-SWAP-GUIDE，真正 escalate 的是 TK-4482。 A careless pass reports `TK-4480`.

## Reference solution
1. List faq/ to see the digest inputs.
2. Read README.md and the tickets CSV.
3. Read faq/macros.txt, then summarize topics per ticket and the macro each one got.

## Why the answer is unique
TK-4480 carries the macro MACRO-SWAP-GUIDE, and macros.txt shows that macro is a self-service guide, so it was handled without escalation; the only escalate row is TK-4482. Billing is the topic with three of the five tickets, and no reading of the CSV changes those counts.
