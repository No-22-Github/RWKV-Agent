## Traps
- TR-DUPROW: the 4 May retry appended three byte-identical copies of existing rows (the same LN-70xxxx line_id, same order, same every field). POT-CLAY-40 therefore tops the ROW count (12 rows: 9 distinct orders, 3 of them re-sent lines), while SED-TRAY-M tops the ORDER count (10 rows, all distinct orders, sitting in the tail of the export). Ranking by rows hands over the decoy; ranking by distinct orders gives the answer.

## Reference solution
1. Read README.md: one row per order line, a SKU at most once per order, retried lines re-appear byte-identical under the same line_id, so rows are not orders.
2. Sample the export head with a line window to fix the column grammar.
3. Rank codes by rows first: search POT-CLAY-40 — 12 hits, 3 of them byte-identical re-sent lines, 9 distinct orders.
4. Search SED-TRAY-M — 10 rows in the tail of the file, all distinct orders.
5. Sweep the remaining codes the same way; none reaches 9 distinct orders. Winner: SED-TRAY-M.

## Why the answer is unique
The README pins the semantics: a SKU appears at most once per order, so distinct order_id values per SKU are order counts, and the retried lines are byte-identical under the same line_id, so they cannot add orders. POT-CLAY-40 leads on rows only because of the re-sent lines; no reading turns its 9 orders into 10. SED-TRAY-M's 10 distinct orders top every other code, with no tie at the top. The answer is SED-TRAY-M.
