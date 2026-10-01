## Traps
- TR-DECOY: a test can fail on several days, so rows are not tests. August checkout has 15 rows but 9 distinct tests; counting rows gives 15 (turn 1). The worst offender is checkout_guest_paid with 3+2+4+1+4 = 14 failures (turn 2). September has 7 distinct flaky checkout tests (turn 3, same definition after the scope change).

## Reference solution
1. Read flaky-tests-2026.csv and the README definition (turn 1).
2. Filter suite=checkout, month=2026-08, count distinct test names: 9.
3. Sum failures per test for August: checkout_guest_paid = 14 (turn 2).
4. Re-run the same count for 2026-09: 7 distinct tests (turn 3).

## Why the answer is unique
The README pins the flaky definition to the month, and the test column gives an exact distinct count: 9 rows-to-tests confusion is the only careless reading and it contradicts the definition. The worst test's failure sum is additive over its rows and unique. September re-runs the identical definition. Answers are uniquely 9, 14, 7.

## Five alternative phrasings
- How many checkout tests were flaky last month
- Count the flaky tests in the checkout suite for August
- Which test failed most often and how many times
- Same question but for September
- Give me the flaky-test count for the checkout suite in September
