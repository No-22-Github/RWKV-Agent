## Traps
- TR-RULEFILE: the return window sits in terms/terms-of-sale.md, which separates stock goods (clause 6.1, 30 days) from anything shown against a build number (clause 6.2, 21 days). The hive body line on orders/SC-2291-thistlebank.md carries build BN-7714, so clause 6.2 governs. Stopping at the stock clause gives the decoy 30.

## Reference solution
1. List the workspace: a README, a terms folder with two sheets, and the order confirmation.
2. Read orders/SC-2291-thistlebank.md: the hive body line is shown against build BN-7714.
3. Read terms/terms-of-sale.md: goods shown against a build number may be returned within 21 days of delivery, and no other clause gives a return window, so the window for this order is 21 days.

## Why the answer is unique
The decoy 30 is wrong because clause 6.1 covers only stock goods ordered from the catalogue, while clause 6.2 catches anything shown against a build number on the confirmation, whatever the item is. The two clauses are mutually exclusive, since a line either carries a build number or it does not, and the hive body line on SC-2291 carries BN-7714. Clause 6.3 rules out live colonies only and clause 6.4 covers when money is paid, not how long the customer has to ask, so exactly one window applies to this order: 21 days.
