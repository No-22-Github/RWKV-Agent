## Traps
- TR-RULEFILE: the rate card splits sites into the standard price and a two-person crew price, and names the July medical roster. Billing Pellworth Clinic's nine visits at the standard rate gives 775.8 instead of 1348.2.

## Reference solution
1. Turn 1: list_files to find the invoice list and the rate card.
2. read finance/cleaning-rates-2026.md: standard 86.20 per visit, crew sites 149.80, and Pellworth Clinic is named on the July medical roster.
3. read invoices/july-2026.csv; Pellworth Clinic has nine visits, so 9 x 149.80 = 1348.20.
4. Turn 2 needs no further call: the rate card and invoice row for Hargrave House were both read in turn 1, giving 12 x 86.20 = 1034.40.

## Why the answer is unique
The rate card is the only source of prices, and it fixes two rates: 86.20 for standard sites and 149.80 for the named medical roster. Pellworth Clinic is named on the roster, so its nine visits cost 9 x 149.80 = 1348.20; the 775.8 reading prices the site at the standard rate the card reserves for everyone else. Hargrave House is not on the roster, so its twelve visits are 12 x 86.20 = 1034.40. No other price exists in the card.

## Five alternative phrasings of the task
1. sudlow facility care pellworth clinic july invoice
2. what does hargrave house owe sudlow
3. sudlow cleaning rounds july charges
4. sudlow medical roster sites july
5. july visit billing sudlow facility care
