## Traps
- TR-DUPROW: five delivery notes in flour_deliveries_2026-08.csv were reprinted, so adding every line gives 1188
  sacks while the distinct notes come to 1038 sacks. The reprinted notes belong to Coldharbour Flour, Dunmere Mill, Eastgate Grain, Graveling & Sons, so those four supplier totals come out high.

## Reference solution
1. List the workspace: the August delivery log and an empty reports directory.
2. Read flour_deliveries_2026-08.csv, keep one line per note_id, and add the sacks per supplier.
3. Write reports/supplier_totals.csv with the header supplier,sacks and one alphabetically ordered line per
   supplier.

## Why the answer is unique
Every reprinted line repeats its note_id, supplier, date and sack count exactly, so the repeats are the same
delivery note printed twice and cannot be counted again. Grouping the 48 distinct notes by supplier leaves one
total per supplier, and no other reading of the file produces a different set of totals.
