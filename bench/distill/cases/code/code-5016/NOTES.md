## Traps
- None. No trap tag is set: the empty basket is a case the quote helper answers on its own line, and the charge it returns is a named constant.

## Reference solution
1. Read quotes/shipping.py: shipping_quote() answers an empty basket on its own branch and returns HANDLING_PENCE (call 1).
2. Read the constant: HANDLING_PENCE is 275, so an empty basket is charged 275 pence (call 2). The answer is 275.

## Why the answer is unique
An empty basket is basket_pence 0: it is below FREE_OVER_PENCE, and the branch for zero returns HANDLING_PENCE rather than the handling fee plus an amount priced by the basket, so the charge does not depend on anything that is missing from the basket. The only number the branch can return is the constant, which is 275, and quotes/orders.py gives the same empty basket as 0 pence, so the answer is 275.
