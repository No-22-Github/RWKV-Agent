## Traps
- TR-AMBIG: the first request names Lowthorpe Stores, and the order file prices lines for
  two shops of that name, Norwich and Ely. Priced for Ely the order is 560.00
  (48 x 4.25 + 16 x 9.50 + 30 x 6.80); priced for Norwich it is 539.00 (60 x 4.25 +
  25 x 6.80 + 12 x 9.50). The file alone cannot say which shop the invoice means, so the
  assistant has to ask.

## Reference solution
1. list_files: the workspace holds orders/lowthorpe-2026-09.csv and README.md.
2. read_file orders/lowthorpe-2026-09.csv: the shop column carries two shops trading as
   Lowthorpe Stores, so the request is not yet settled and the assistant asks which one.
3. Turn 2 fixes the Ely shop. Multiply and add that shop's lines:
   48 x 4.25 + 16 x 9.50 + 30 x 6.80 = 204.00 + 152.00 + 204.00 = 560.00.

## Why the answer is unique
After the clarification one shop is in scope. Every line carries its own units and unit
price and the README says lines are invoiced at the unit price on the line, so the Ely
order is the sum of its three lines: 560.00. The decoy 539.00 is the Norwich shop's
three lines; it is a real figure, but it belongs to the other account, and the request
was settled on the Ely shop before the lines were priced.

## Five alternative phrasings of the task
1. cleeve wholesale lowthorpe stores september order
2. lowthorpe stores ely and norwich order lines
3. what does the lowthorpe stores order come to
4. cleeve september invoice lowthorpe
5. lowthorpe stores order value september
