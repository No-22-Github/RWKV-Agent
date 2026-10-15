## Traps
- TR-DECOY: `apply_discount_legacy` is a different function (used by checkout/old_basket.py, which must not be listed). promo_report.py also has the call, with a comment next to it.
Turn 1 expects the definition file pricing/discounts.py. Turn 2 asks for callers: checkout/cart.py and reports/promo_report.py (both must be named).

## Reference solution
1. Search `def apply_discount` -> pricing/discounts.py.
2. Search `apply_discount(` -> cart.py and promo_report.py (old_basket.py only calls the legacy function).

## Why the answer is unique
Exactly two modules call `apply_discount(`: checkout/cart.py and reports/promo_report.py. Passing `item.get` etc. does not matter. No tests directory exists.

EXAM-CANARY-516e22a1
