## Traps
- TR-RULEFILE: the staging terms live in docs/staging-terms-2026.md and put a 20% levy on what Craft exhibitors owe after refunds. Invoicing Colvend Pottery without the levy gives 555.0 instead of 666.0.
- TR-SIGN: the refund column holds money already paid back, written as a positive amount. Charging the levy on the booth fee while ignoring the refund gives 768.0 instead of 666.0.

## Reference solution
1. Turn 1: list_files to find the invoice list, the terms and the README.
2. read README.md: the refund column is money paid back and is stored positive.
3. read docs/staging-terms-2026.md: Craft owes a 20% levy on the amount left after refunds.
4. read invoices/exhibitors-2026.csv; Colvend Pottery owes 640.00 - 85.00 = 555.00, plus the levy, 666.00.
5. Turn 2 needs no further call: the three files read in turn 1 give Dunbreck Weavers 480.00 - 60.00 = 420.00 plus the levy, 504.00.

## Why the answer is unique
Both rules are pinned by the fixtures the turn-1 read covers. The README says the refund is money already paid back, stored positive, so it comes off the booth fee; charging the levy on the untouched fee gives 768.0, which pays the levy on money the exhibitor already has back. The terms put the levy on the amount owed after refunds, so the no-levy reading of 555.0 applies a schedule the fair does not run for Craft. That leaves (640.00 - 85.00) x 1.20 = 666.00 for Colvend Pottery and (480.00 - 60.00) x 1.20 = 504.00 for Dunbreck Weavers.

## Five alternative phrasings of the task
1. hallowfield craft fair colvend pottery invoice
2. what does dunbreck weavers owe hallowfield
3. hallowfield exhibitor invoices staging levy
4. colvend pottery booth fee after refund
5. hallowfield craft fair final invoices 2026
