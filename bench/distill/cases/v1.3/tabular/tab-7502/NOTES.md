## Traps
- TR-DEFN: README defines what counts - voided invoices were cancelled and never paid, so the August figure covers status=Settled only. Summing every Hearth & Honey August row regardless of status gives 6757.75.

## Reference solution
1. read_file README.md: only settled invoices were paid; voided ones stay for audit.
2. data_query: {"path":"data/wholesale_invoices.csv","filter":{"invoice_month":"2026-08","cafe_chain":"Hearth & Honey","status":"Settled"},"operation":"sum","field":"amount"} -> 5441.46.
3. Reply with the number 5441.46 only.

## Why the answer is unique
The decoy 6757.75 adds the voided invoices, but the question asks what Hearth & Honey owed, and the README states voided invoices were cancelled and never paid, so they are not part of what anyone owed. Each invoice carries exactly one status, so no reading keeps a voided invoice in the figure. July and September rows fail the month condition. The answer is 5441.46.
