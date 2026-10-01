## Traps
- TR-DECOY: out/run-summary.json 里 test_tier_basic 与失败用例同前缀，粗读容易指认错用例。 A careless pass reports `test_tier_basic`.

## Reference solution
1. Read out/run-summary.json for the failed entry and its assertion.
2. Open tests/test_pricing.py and check tier_price's boundary against the assertion.
3. Name the failing test and the two values in the assert.

## Why the answer is unique
tier_price treats 50 as the low tier because of <=, so tier_price(50) returns 9.05 and the boundary assertion expecting 9.10 fails, matching the summary's only failed entry. test_tier_basic passed and its inputs never reach the boundary, so the failing test is test_tier_boundary on 9.05 vs 9.10.
