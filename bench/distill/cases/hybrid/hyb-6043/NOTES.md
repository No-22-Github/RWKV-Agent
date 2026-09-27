## Traps
- TR-DUPROW: the scanner re-uploaded two batches, so FN-2201, AB-4402 and AD-3301 each appear twice. Summing the fastener rows as they stand gives 661 instead of 541.
- TR-HEADER: the office TOTAL line closes the file at 886. Adding the units column wholesale including the footer gives 1998.

## Reference solution
1. Turn 1: list_files to find the count file and the README.
2. read README.md: the scanner repeats a few lines and the office writes the TOTAL footer.
3. read stock/october-2025.csv; keep one line per sku, skip the footer, and total the fasteners: 120 + 84 + 132 + 95 + 110 = 541.
4. Turn 2 needs no further call: the same read gives the adhesives total 45 + 72 + 56 = 173.

## Why the answer is unique
The README states each repeated line is the same count written twice and that the TOTAL footer is written by the office system. A sku identifies one counted product, so the three repeats contribute nothing beyond their first line: the fasteners are 120 + 84 + 132 + 95 + 110 = 541, not the 661-row sum that counts FN-2201 twice. The footer's 886 spans every category, so folding it in gives 1998, a figure that answers nothing asked. The adhesives are 45 + 72 + 56 = 173 once AD-3301's repeat is dropped.

## Five alternative phrasings of the task
1. staithe fixtures fastener units october count
2. how many adhesive units on the shelf
3. staithe fixtures shelf count by category
4. october 2025 stock count staithe
5. staithe fixtures stock by sku
