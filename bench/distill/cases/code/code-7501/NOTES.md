## Traps
- TR-DECOY: src/rules.py 的注释里写着 30% 的旧口径（未采纳），粗读会把封顶当成 30%。 A careless pass reports `0.30`.

## Reference solution
1. List src/ and read discount.py.
2. Trace tiered_discount: the tier rate times the subtotal, capped by DISCOUNT_CAP.
3. Read rules.py and note its 30% note is an unadopted draft, then answer.

## Why the answer is unique
The 30% figure lives only in a comment marked 未采纳 in rules.py, and no code path references it, so the enforced cap is DISCOUNT_CAP = 0.25 inside tiered_discount's min(). The rate table covers all three tiers, leaving no second reading of the cap.
