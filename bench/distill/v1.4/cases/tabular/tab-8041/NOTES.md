## Traps
- TR-ABSENT: data/monthly-invoices-september.csv holds only the eight invoices entered so far (2121.82 pounds); data/README.md says monthly invoicing moved to the new membership software on 18 September and later invoices haven't been entered yet. Presenting 8319.84 + 2121.82 = 10441.66 as the September stall-fee income is the decoy answer.
- TR-MULTISRC: reading only one of the two files misses a channel; the daily log alone is 8319.84.

## Reference solution
1. List data/: two fee CSVs and a README.
2. Sum stall-fee-collections-september.csv: nine market days times three sections, 8319.84 pounds complete.
3. Read monthly-invoices-september.csv and the README: eight invoices entered, later ones unentered pending the software import.
Final answer (2-4 sentences): The daily collections log is complete for September: 8319.84 pounds across the three sections. Monthly invoices only cover the eight entered so far (2121.82 pounds); invoicing moved to the new membership software on 18 September and invoices raised after that haven't been entered yet, so the month's stall-fee total cannot be settled yet. I can re-run the total once the first import lands in early October. Criteria: contains 8319.84 (either spelling); the partial sum 10441.66 may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Changelog
- v2：去掉部分合计的排除：S5 三遍老师都给出「已记录合计 X，但不完整」，这是 v1.4 §4.1「只能答一部分」示范的写法，被排除词误判；完整性改由逐条读终答把关。

## Why the answer is unique
10441.66 treats the entered invoices as the whole monthly billing, and the README states invoices raised after 18 September are still outside the ledger, so it is not September's stall-fee income; 8319.84 alone ignores the invoice channel. The daily log is complete, so its total is the certain part, and the reply names the unentered invoices and the import as the next step.
