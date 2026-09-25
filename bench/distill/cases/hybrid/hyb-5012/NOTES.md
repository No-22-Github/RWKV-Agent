## Traps
- TR-AMBIG: the first request asks what the order is worth while every row
  carries a sterling price and a euro price. At the euro prices the order is
  6213.00; at the sterling prices it is 5374.50. The order does not say which
  currency the account is kept in, so the assistant has to ask.

## Reference solution
1. Turn 1: two currencies are priced on every row and the request names neither,
   so the assistant asks and calls no tool.
2. list_files: the workspace holds orders/dundalk-2026-09.csv and README.md.
3. Turn 2 settles it on euros. read_file the order and multiply each line:
   180 x 16.90 + 240 x 9.65 + 150 x 5.70 = 3042.00 + 2316.00 + 855.00 = 6213.00.

## Why the answer is unique
With the currency fixed, each of the three order lines contributes crates times
the one euro price held against it, and the README confirms both prices on a row
describe the same product rather than two separate orders. The decoy 5374.50 is
the same three lines valued in sterling, a figure the file really supports but
for the other currency. Nothing on the order is discounted, repeated or left
unpriced, so the euro value of the September order is 6213.00.

## Five alternative phrasings of the task
1. kilbride smokehouse dundalk order september value
2. september export order priced in euros
3. smoked salmon and trout order with sterling and euro prices
4. kilbride smokehouse trade order billing currency
5. dundalk fine foods september order euro total
