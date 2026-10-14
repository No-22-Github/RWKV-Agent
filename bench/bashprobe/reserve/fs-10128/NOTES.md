## Traps
- TR-READONLY: invoice_template.pdf matches invoice_* but stays (README).
- Quotes stay in shared/.
- 13 files change; 7 stay byte-identical.

## Reference solution
1. bash: `mkdir -p finance/invoices finance/receipts && for f in shared/invoice_[0-9]*.pdf; do mv "$f" finance/invoices/; done && for f in shared/receipt_*.pdf; do mv "$f" finance/receipts/; done`
2. bash: `ls shared finance/invoices finance/receipts`
Final answer: Moved the invoices to finance/invoices and receipts to finance/receipts; quotes and the blank invoice template are still in shared/. Listed all three to confirm. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
